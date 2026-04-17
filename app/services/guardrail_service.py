"""
================================================================================
GUARDRAIL SERVICE - SAFETY AND RELEVANCE FILTERING
================================================================================

This module implements safety guardrails for the Smart Manufacturing Assistant.

WHAT IT DOES:
- Validates user inputs before processing.
- Blocks forbidden topics (politics, violence, etc.).
- Ensures queries are relevant to manufacturing.
- Optionally validates AI outputs (for future PII/safety checks).

WHY GUARDRAILS?
- **Safety**: Prevents the AI from discussing harmful topics.
- **Focus**: Keeps the assistant on-topic for manufacturing.
- **Compliance**: Avoids liability from inappropriate responses.
- **Professional**: Maintains a professional assistant persona.

HOW IT WORKS:
1. **Keyword Blocklist (Fast Check)**:
   - Scans input for forbidden words/phrases.
   - Instant rejection for clearly off-topic content.
   
2. **LLM Relevance Check (Smart Check)**:
   - Uses the AI itself to classify if query is relevant.
   - Catches edge cases the keyword list might miss.
   - Only runs if keyword check passes.

BIG PICTURE:
- First line of defense in the Orchestrator.
- Runs BEFORE any processing happens.
- Protects both the user and the system.

ARCHITECTURE:
    [User Query]
         |
         v
    [Guardrail Service]  <-- YOU ARE HERE
         |
         ├── Blocked? --> Return refusal message
         |
         └── Passed? --> Continue to Orchestrator
================================================================================
"""

from typing import Tuple
from app.services.llm_service import llm_service


class GuardrailService:
    """
    Service for validating user inputs and ensuring safe, relevant interactions.
    
    Implements a two-layer filtering approach:
    1. Fast keyword blocklist for obvious violations.
    2. LLM-based relevance check for nuanced filtering.
    
    Attributes:
        forbidden_topics: List of keywords/phrases to block.
    """
    
    def __init__(self):
        """
        Initialize the guardrail service with a list of forbidden topics.
        
        These topics are explicitly blocked because they're:
        - Off-topic for manufacturing (politics, religion)
        - Potentially harmful (weapons, violence)
        - Outside the assistant's expertise (finance, medical)
        """
        self.forbidden_topics = [
            # Off-topic discussions
            "politics", "religion", "finance", "medical advice",
            "vote", "election",
            # Harmful content
            "bomb", "weapon", "kill", "suicide",
            # Financial advice (liability concerns)
            "stock market", "investment"
        ]

    def check_relevance(self, text: str) -> bool:
        """
        Use the LLM to determine if a query is relevant to manufacturing.
        
        WHAT: Classifies whether the query relates to manufacturing topics.
        HOW: Sends a classification prompt to the LLM, expects YES/NO.
        BIG PICTURE: Catches queries that aren't in the blocklist but still
                     shouldn't be answered (e.g., "How do I bake a cake?").
        
        Args:
            text: The user's query to classify.
            
        Returns:
            bool: True if relevant to manufacturing, False otherwise.
        """
        # Prompt the LLM to act as a relevance classifier
        prompt = f"""You are a relevance classifier for a Smart Manufacturing Assistant.
        The assistant supports:
        - Machine maintenance and diagnostics (vibration, temperature, pressure).
        - Spare parts inventory.
        - Standard Operating Procedures (SOPs).
        - Plant monitoring.
        
        Is the following user query relevant to these topics?
        Query: "{text}"
        
        Answer ONLY 'YES' or 'NO'.
        """
        
        # Get LLM response and normalize
        response = llm_service.generate(prompt).strip().upper()
        
        # Check if YES appears in response (handles "YES.", "Yes!", etc.)
        return "YES" in response

    def validate_input(self, text: str) -> Tuple[bool, str]:
        """
        Validate user input for safety and relevance.
        
        WHAT: Determines if a user query should be processed or blocked.
        HOW: 
            1. Fast keyword check against blocklist.
            2. LLM relevance check if keyword check passes.
        BIG PICTURE: Called by Orchestrator before any processing.
        
        Args:
            text: The user's query to validate.
            
        Returns:
            Tuple[bool, str]: (is_valid, reason)
            - is_valid: True if the query should be processed.
            - reason: Empty if valid, explanation if blocked.
        """
        lower_text = text.lower()
        
        # =====================================================================
        # LAYER 1: KEYWORD BLOCKLIST (Fast)
        # Immediately reject queries containing forbidden topics.
        # This is a fast check that doesn't require LLM calls.
        # =====================================================================
        for topic in self.forbidden_topics:
            if topic in lower_text:
                return False, f"I cannot discuss {topic} as it is outside the scope of manufacturing support."
        
        # =====================================================================
        # LAYER 2: LLM RELEVANCE CHECK (Smart)
        # For queries that pass the keyword check, verify they're actually
        # relevant to manufacturing using the LLM.
        # Skip for very short inputs (greetings like "Hi" or "Hello").
        # =====================================================================
        if len(text.split()) > 1 and not self.check_relevance(text):
            return False, "I can only assist with manufacturing, machine maintenance, and plant operations."

        # Query is valid - allow processing
        return True, ""

    def validate_output(self, text: str) -> Tuple[bool, str]:
        """
        Validate AI output before returning to user.
        
        WHAT: Checks AI responses for safety issues.
        HOW: Currently a placeholder for future implementation.
        BIG PICTURE: Could check for PII leakage, harmful content, etc.
        
        Note: In production, this could:
        - Scan for accidentally exposed PII
        - Check for harmful/inappropriate content
        - Verify factual accuracy
        - Apply content policies
        
        Args:
            text: The AI's generated response.
            
        Returns:
            Tuple[bool, str]: (is_valid, reason)
        """
        # Currently trusting the model - add checks as needed
        return True, ""


# Global singleton instance
# Used by Orchestrator for all validation
guardrail_service = GuardrailService()

