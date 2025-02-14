from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Literal
from enum import Enum

class ToneType(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    EMPATHETIC = "empathetic"
    DIRECT = "direct"

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096, description="User message to process")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI agent response")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class Message(BaseModel):
    role: str = Field(..., description="Message role (human or assistant)")
    content: str = Field(..., description="Message content")

class ConversationHistory(BaseModel):
    messages: List[Message] = Field(default_factory=list, description="List of conversation messages")

class EmailContext(BaseModel):
    customer_name: Optional[str] = Field(None, description="Customer's name")
    customer_history: Optional[str] = Field(None, description="Previous interactions or relevant history")
    account_type: Optional[str] = Field(None, description="Customer's account type")
    previous_interactions: Optional[int] = Field(None, description="Number of previous interactions")
    priority: Optional[str] = Field(None, description="Priority level of the request")
    department: Optional[str] = Field(None, description="Department handling the request")
    additional_notes: Optional[str] = Field(None, description="Any additional context")

class ToneDetectionMetadata(BaseModel):
    detected_tone: str = Field(..., description="Detected tone value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the detection")
    factors: Dict[str, float] = Field(..., description="Factors considered in tone detection")

class EmailRequest(BaseModel):
    customer_message: str = Field(
        ..., 
        min_length=1, 
        max_length=8192, 
        description="Customer's email message to respond to"
    )
    context: Optional[EmailContext] = Field(
        default=None,
        description="Additional context for response generation"
    )
    tone: Optional[ToneType] = Field(
        default=None,
        description="Desired tone for the response. If not provided, will be auto-detected."
    )
    max_length: Optional[int] = Field(
        default=2048,
        le=4096,
        description="Maximum length of the response"
    )

class EmailResponseMetadata(BaseModel):
    tone_used: str = Field(..., description="Tone used in the response")
    context_length: int = Field(..., description="Length of the context used")
    generation_settings: Dict[str, float] = Field(..., description="Model generation settings used")
    tone_detection: Optional[ToneDetectionMetadata] = Field(None, description="Tone detection information if auto-detected")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EmailResponse(BaseModel):
    message: str = Field(..., description="Generated email response")
    status_code: int = Field(..., description="HTTP status code")
    execution_time_ms: float = Field(..., description="Time taken to generate response in milliseconds")
    metadata: EmailResponseMetadata = Field(..., description="Additional response metadata")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")

class StatusResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field("1.0.0", description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @validator("status")
    def status_must_be_valid(cls, v):
        valid_statuses = ["running", "error", "maintenance"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v 