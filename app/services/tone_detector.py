from app.models.schemas import ToneType
from app.core.logger import get_logger
import re
from typing import Dict, Tuple

logger = get_logger()

class ToneDetector:
    def __init__(self):
        """Initialize the tone detector with pattern matching rules."""
        # Urgency patterns
        self.urgency_patterns = [
            r'\b(?:URGENT|ASAP|EMERGENCY|CRITICAL|IMMEDIATE)\b',
            r'(?i)urgent|emergency|asap|right away|immediately|right now',
            r'!{2,}',  # Multiple exclamation marks
        ]
        
        # Complaint patterns
        self.complaint_patterns = [
            r'(?i)disappointed|frustrated|angry|upset|terrible|worst',
            r'(?i)not acceptable|unacceptable|poor|bad experience',
            r'(?i)third time|again|still not|yet to|never',
            r'(?i)complaint|issue|problem|error|bug|failed|failure',
        ]
        
        # Formal patterns
        self.formal_patterns = [
            r'(?i)dear|sincerely|regards|pursuant|accordingly',
            r'(?i)request|inquire|regarding|concerning|matter',
            r'(?i)documentation|legal|compliance|policy|regulation',
        ]
        
        # Positive patterns
        self.positive_patterns = [
            r'(?i)thank|appreciate|great|good|excellent|wonderful',
            r'(?i)love|enjoy|pleased|happy|satisfied|helpful',
            r'(?i)feature request|suggestion|idea|feedback',
            r'😊|👍|🙏',  # Positive emojis
        ]

    def _check_patterns(self, text: str, patterns: list) -> float:
        """Check how many patterns match in the text and return a score."""
        matches = sum(bool(re.search(pattern, text)) for pattern in patterns)
        return min(matches / len(patterns), 1.0)

    def _analyze_message(self, message: str) -> Dict[str, float]:
        """Analyze the message and return scores for different aspects."""
        return {
            "urgency": self._check_patterns(message, self.urgency_patterns),
            "complaint": self._check_patterns(message, self.complaint_patterns),
            "formality": self._check_patterns(message, self.formal_patterns),
            "positivity": self._check_patterns(message, self.positive_patterns),
        }

    def detect_tone(self, message: str, context: Dict = None) -> Tuple[str, Dict]:
        """
        Detect the appropriate tone for a response based on message content and context.
        
        Args:
            message: The customer's message
            context: Optional context information about the customer and situation
            
        Returns:
            Tuple of (detected tone value, detection metadata)
        """
        # Analyze message
        scores = self._analyze_message(message)
        logger.debug(f"Tone detection scores: {scores}")
        
        # Consider context if available
        priority = "normal"
        if context and context.get("priority"):
            priority = context.get("priority").lower()

        # Decision logic
        if scores["urgency"] > 0.3 or priority == "critical":
            tone = "direct"
            confidence = scores["urgency"]
        elif scores["complaint"] > 0.3:
            tone = "empathetic"
            confidence = scores["complaint"]
        elif scores["formality"] > 0.3:
            tone = "formal"
            confidence = scores["formality"]
        elif scores["positivity"] > 0.3:
            tone = "friendly"
            confidence = scores["positivity"]
        else:
            tone = "professional"
            # Calculate average of non-zero scores for confidence
            non_zero_scores = [s for s in scores.values() if s > 0]
            confidence = sum(non_zero_scores) / len(non_zero_scores) if non_zero_scores else 0.5

        metadata = {
            "detected_tone": tone,
            "confidence": confidence,
            "factors": scores
        }
        
        logger.info(f"Detected tone: {tone} with confidence: {confidence:.2f}")
        return tone, metadata 