from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    ChatRequest, ChatResponse, StatusResponse, ErrorResponse,
    ConversationHistory, EmailRequest, EmailResponse
)
from app.services.ai_agent import AIAgent
from app.core.logger import get_logger

logger = get_logger()
router = APIRouter()
ai_agent = AIAgent()

@router.post("/chat", 
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse}
    },
    summary="Chat with the AI agent",
    description="Send a message to the AI agent and get a response"
)
async def chat_with_ai(request: ChatRequest):
    try:
        # Check if service is healthy
        if not await ai_agent.health_check():
            raise HTTPException(
                status_code=503,
                detail={"error": "AI service is currently unavailable", "details": "Service is not responding"}
            )
            
        logger.info(f"Received chat request: {request.message}")
        response = await ai_agent.process_message(request.message)
        return ChatResponse(response=response)
    except HTTPException as he:
        logger.error(f"HTTP error in chat request: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "details": str(e)}
        )

@router.post("/email/respond",
    response_model=EmailResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse}
    },
    summary="Generate email response",
    description="Generate a response to a customer email with specified tone and context"
)
async def generate_email_response(request: EmailRequest):
    try:
        # Check if service is healthy
        if not await ai_agent.health_check():
            raise HTTPException(
                status_code=503,
                detail={"error": "AI service is currently unavailable", "details": "Service is not responding"}
            )
            
        logger.info(f"Received email response request with tone: {request.tone}")
        response = await ai_agent.generate_email_response(request)
        return response
    except HTTPException as he:
        logger.error(f"HTTP error in email response request: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Error generating email response: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "details": str(e)}
        )

@router.get("/chat/history",
    response_model=ConversationHistory,
    responses={
        500: {"model": ErrorResponse}
    },
    summary="Get conversation history",
    description="Retrieve the current conversation history"
)
async def get_chat_history():
    try:
        messages = await ai_agent.get_conversation_history()
        return ConversationHistory(messages=messages)
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to retrieve chat history", "details": str(e)}
        )

@router.post("/chat/clear",
    response_model=StatusResponse,
    responses={
        500: {"model": ErrorResponse}
    },
    summary="Clear conversation",
    description="Clear the current conversation history"
)
async def clear_chat():
    try:
        await ai_agent.clear_conversation()
        return StatusResponse(status="conversation cleared")
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to clear chat history", "details": str(e)}
        )

@router.get("/status",
    response_model=StatusResponse,
    responses={
        503: {"model": ErrorResponse}
    },
    summary="Get service status",
    description="Check if the service and LangChain are running and get basic information"
)
async def get_status():
    is_healthy = await ai_agent.health_check()
    if not is_healthy:
        raise HTTPException(
            status_code=503,
            detail={"error": "Service unhealthy", "details": "AI service is not responding"}
        )
    return StatusResponse(status="running") 