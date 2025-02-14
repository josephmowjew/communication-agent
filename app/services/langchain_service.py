from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from app.core.logger import get_logger
from app.core.config import settings
from app.models.schemas import EmailRequest, EmailResponse, EmailResponseMetadata, ToneType
from typing import Optional, Dict
import time
import json
from app.services.tone_detector import ToneDetector

logger = get_logger()

TONE_GUIDELINES = {
    ToneType.PROFESSIONAL: "Use a professional and polished tone. Be clear, concise, and business-appropriate.",
    ToneType.FRIENDLY: "Use a warm and approachable tone. Be personable while maintaining professionalism.",
    ToneType.FORMAL: "Use a formal and traditional tone. Be respectful and maintain appropriate distance.",
    ToneType.EMPATHETIC: "Use an understanding and supportive tone. Show compassion and acknowledge feelings.",
    ToneType.DIRECT: "Use a clear and straightforward tone. Be concise and get to the point quickly."
}

class LangChainService:
    def __init__(self):
        """Initialize LangChain service with Ollama model and conversation memory."""
        # Initialize Ollama with DeepScaleR model
        # DeepScaleR is a 1.5B parameter model fine-tuned using distributed RL
        # It excels at mathematical reasoning and problem-solving
        self.llm = OllamaLLM(
            base_url=settings.OLLAMA_HOST,
            model=settings.OLLAMA_MODEL,
            temperature=settings.TEMPERATURE,
            context_window=settings.MAX_TOKENS
        )
        
        # Initialize tone detector
        self.tone_detector = ToneDetector()
        
        # Define a custom prompt template optimized for DeepScaleR's capabilities
        template = """You are an AI assistant powered by DeepScaleR, a state-of-the-art language model trained using distributed reinforcement learning. You excel at:
- Mathematical reasoning and problem-solving
- Precise and accurate responses
- Handling complex queries with structured thinking
- Maintaining context in long conversations

Current conversation context:
{history}
Human: {input}
Assistant: Let me provide a clear and structured response."""

        self.chat_prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=template
        )
        
        # Email response template
        self.email_template = """System: You are a customer support agent responding to customer inquiries. You must follow these rules strictly:
1. Respond AS A SUPPORT AGENT addressing the customer's concerns
2. Output ONLY the email response
3. Do not include any explanations or thinking process
4. Do not use XML-like tags
5. Start with "Dear [Customer's Name],"
6. End with an appropriate signature
7. Stay within character limits
8. Maintain the specified tone

SUPPORT AGENT GUIDELINES:
- Immediately acknowledge the urgency/priority of the issue
- Provide SPECIFIC, ACTIONABLE steps the customer can take
- If it's a known issue, provide the current status and ETA
- Include CONCRETE next steps (e.g., specific phone numbers, links, or procedures)
- For urgent issues, provide immediate workarounds if available
- Include your direct contact information and availability
- Specify when the customer can expect updates or resolution
- Sign off with your department name and case reference number

RESPONSE STRUCTURE:
1. Acknowledgment of the specific issue
2. Immediate action items or workarounds
3. Next steps and timeline
4. Your contact information and availability
5. Case reference or ticket number

CONTEXT INFORMATION:
{context}

TONE GUIDELINES:
{tone_guidelines}

CUSTOMER MESSAGE:
{customer_message}

REQUIREMENTS:
1. Provide SPECIFIC, ACTIONABLE solutions
2. Maintain the specified tone
3. Be clear and well-structured
4. Stay within {max_length} characters
5. Include concrete next steps
6. Reference relevant documentation
7. Provide timeline expectations
8. Include case/ticket reference

Generate the support agent's email response below:"""
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            return_messages=True,
            output_key="output",
            input_key="input"
        )
        
        # Create conversation chain
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.chat_prompt,
            verbose=settings.DEBUG
        )
        
        logger.info(f"LangChain service initialized successfully with DeepScaleR model: {settings.OLLAMA_MODEL}")

    def _format_context(self, context: Optional[Dict]) -> str:
        """Format context information for the prompt."""
        if not context:
            return "No additional context provided."
        
        context_str = "Customer Information:\n"
        for key, value in context.dict(exclude_none=True).items():
            formatted_key = key.replace('_', ' ').title()
            context_str += f"- {formatted_key}: {value}\n"
        return context_str

    async def generate_email_response(self, request: EmailRequest) -> EmailResponse:
        """
        Generate an email response based on the request.
        
        Args:
            request: EmailRequest containing message and preferences
            
        Returns:
            EmailResponse with generated message and metadata
        """
        start_time = time.time()
        try:
            # Initialize tone variables
            tone_detection_metadata = None
            tone = request.tone.value if request.tone else None
            
            # Detect tone if not provided
            if tone is None:
                context_dict = request.context.dict() if request.context else {}
                detected_tone, detection_metadata = self.tone_detector.detect_tone(
                    request.customer_message,
                    context_dict
                )
                tone = detected_tone
                tone_detection_metadata = detection_metadata
                logger.info(f"Auto-detected tone: {detected_tone}")
            
            # Ensure tone is valid and convert to ToneType
            try:
                tone_type = ToneType(tone)
                tone_guidelines = TONE_GUIDELINES[tone_type]
            except (ValueError, KeyError) as e:
                logger.warning(f"Invalid tone '{tone}', falling back to professional")
                tone_type = ToneType.PROFESSIONAL
                tone = tone_type.value
                tone_guidelines = TONE_GUIDELINES[tone_type]
            
            # Format the prompt with context and tone
            context_str = self._format_context(request.context)
            prompt = self.email_template.format(
                context=context_str,
                tone_guidelines=tone_guidelines,
                customer_message=request.customer_message,
                max_length=request.max_length or 2048
            )
            
            # Generate response
            logger.debug(f"Generating email response with tone: {tone}")
            response = await self.llm.agenerate([prompt])
            message = response.generations[0][0].text.strip()
            
            # Clean up the response by removing any thinking process
            if "<think>" in message:
                message = message.split("</think>")[-1].strip()
            
            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Create metadata
            metadata = EmailResponseMetadata(
                tone_used=tone,
                context_length=len(prompt),
                generation_settings={
                    "temperature": settings.TEMPERATURE,
                    "max_tokens": settings.MAX_TOKENS,
                    "top_p": settings.TOP_P,
                    "top_k": settings.TOP_K
                },
                tone_detection=tone_detection_metadata
            )
            
            return EmailResponse(
                message=message,
                status_code=200,
                execution_time_ms=execution_time,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error generating email response: {str(e)}")
            execution_time = (time.time() - start_time) * 1000
            raise

    async def generate_response(self, message: str) -> str:
        """
        Generate a response using the LangChain conversation chain.
        
        Args:
            message: The user's input message
            
        Returns:
            str: The generated response
        """
        try:
            logger.debug(f"Generating response for message: {message}")
            response = await self.conversation.apredict(input=message)
            logger.debug(f"Generated response: {response}")
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def get_conversation_history(self) -> list:
        """Get the current conversation history."""
        return self.memory.chat_memory.messages

    async def clear_memory(self) -> None:
        """Clear the conversation memory."""
        self.memory.clear()
        logger.info("Conversation memory cleared") 