from app.core.logger import get_logger
from app.core.config import settings
from app.services.langchain_service import LangChainService
from app.models.schemas import EmailRequest, EmailResponse
from typing import Dict, List
from datetime import datetime

logger = get_logger()

class AIAgent:
    def __init__(self):
        """Initialize the AI agent with LangChain service."""
        self.context: Dict[str, str] = {}
        self.langchain = LangChainService()
        logger.info("AI Agent initialized successfully with LangChain service")

    async def process_message(self, message: str) -> str:
        """
        Process the incoming message and generate a response using LangChain.
        
        Args:
            message: The user's input message
            
        Returns:
            str: The AI agent's response
        """
        logger.debug(f"Processing message: {message}")
        
        # Store the message in context
        self.context['last_message'] = message
        self.context['last_timestamp'] = datetime.utcnow().isoformat()
        
        # Generate response using LangChain
        response = await self.langchain.generate_response(message)
        
        logger.debug(f"Generated response: {response}")
        return response

    async def generate_email_response(self, request: EmailRequest) -> EmailResponse:
        """
        Generate an email response based on the request.
        
        Args:
            request: EmailRequest containing message and preferences
            
        Returns:
            EmailResponse with generated message and metadata
        """
        logger.debug(f"Generating email response for request with tone: {request.tone}")
        
        # Store request in context
        self.context['last_email'] = request.customer_message
        self.context['last_tone'] = request.tone.value
        self.context['last_timestamp'] = datetime.utcnow().isoformat()
        
        # Generate response using LangChain
        response = await self.langchain.generate_email_response(request)
        
        logger.debug(f"Generated email response with status code: {response.status_code}")
        return response

    async def get_conversation_history(self) -> List[dict]:
        """Get the current conversation history."""
        messages = await self.langchain.get_conversation_history()
        return [{"role": msg.type, "content": msg.content} for msg in messages]

    async def clear_conversation(self) -> None:
        """Clear the conversation history."""
        await self.langchain.clear_memory()
        self.context.clear()
        logger.info("Conversation cleared")

    async def health_check(self) -> bool:
        """Check if the AI agent and LangChain service are healthy."""
        try:
            # Try to generate a simple response directly using the LLM
            response = await self.langchain.llm.agenerate(["Hi"])
            return bool(response.generations[0][0].text.strip())
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False 