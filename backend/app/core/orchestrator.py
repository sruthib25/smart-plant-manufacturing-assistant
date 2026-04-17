"""
================================================================================
ORCHESTRATOR - MULTI-AGENT ROUTING AND REQUEST HANDLING
================================================================================

This module is the "brain" of the Smart Manufacturing Assistant backend.
It coordinates between multiple specialized agents to handle user requests.

WHAT IT DOES:
- Receives user queries from the chat API.
- Validates input using the Guardrail service (safety & relevance checks).
- Routes queries to the appropriate agent (RAG, DIAGNOSTICS, or GENERAL).
- Maintains conversation context using the Memory service.
- Returns AI-generated responses.

HOW IT WORKS:
1. User sends a message via the /chat endpoint.
2. Orchestrator validates the input (guardrails).
3. Orchestrator uses LLM to classify which agent should handle the query.
4. The selected agent processes the query:
   - RAG Agent: Retrieves relevant documents and answers based on them.
   - DIAGNOSTICS Agent: Analyzes current sensor data.
   - GENERAL Agent: Handles general manufacturing questions.
5. Response is saved to memory and returned to the user.

BIG PICTURE:
- This is the central coordination point for all AI interactions.
- It implements a simple "router" pattern for multi-agent systems.
- All context (history, documents, sensor data) flows through here.

ARCHITECTURE:
    [Chat API]
        |
        v
    [Orchestrator]  <-- YOU ARE HERE
        |
    +---+---+---+
    |   |   |   |
    v   v   v   v
  Guard Memory Route Process
  rails        Query  (RAG/DIAG/GEN)
                |
                v
            [LLM Service]
================================================================================
"""

from app.services.llm_service import llm_service       # For generating AI responses
from app.services.rag_service import rag_service       # For document retrieval
from app.services.simulator import simulator           # For simulated sensor data
from app.services.memory_service import memory_service # For session-based chat history
from app.services.guardrail_service import guardrail_service  # For safety checks
import json


class Orchestrator:
    """
    The central coordinator for handling user requests in the Smart Manufacturing Assistant.
    
    Responsibilities:
    - Input validation (guardrails)
    - Query classification and routing
    - Response generation via appropriate agent
    - Memory management (saving conversations)
    """
    
    def __init__(self):
        """
        Initialize the Orchestrator with the system prompt for query routing.
        
        The system prompt instructs the LLM on how to classify user queries
        into one of three categories: RAG, DIAGNOSTICS, or GENERAL.
        """
        self.system_prompt = """You are a Smart Manufacturing Assistant. 
        You have access to the following tools/agents:
        - RAG: For looking up SOPs, manuals, and procedures.
        - DIAGNOSTICS: For analyzing current machine sensor data.
        - GENERAL: For general manufacturing questions.
        
        Your task is to classify the user query and route it to the correct agent. 
        Return ONLY a JSON object: {"agent": "AGENT_NAME", "reasoning": "short explanation"}
        Allowed AGENT_NAMES: RAG, DIAGNOSTICS, GENERAL
        """
    
    def route_query(self, user_query: str, session_id: str = "default") -> dict:
        """
        Determine which agent should handle the user's query.
        
        WHAT: Uses the LLM to classify the query into RAG, DIAGNOSTICS, or GENERAL.
        HOW: Sends the system prompt + chat history + user query to the LLM.
             Parses the JSON response to extract the agent name.
        BIG PICTURE: This is the "dispatcher" that decides the processing path.
        
        Args:
            user_query: The user's message.
            session_id: The session identifier for context retrieval.
            
        Returns:
            dict: Contains "agent" key with value "RAG", "DIAGNOSTICS", or "GENERAL".
        """
        # Include chat history for better context-aware routing
        history = memory_service.get_formatted_history(session_id)
        prompt = f"{self.system_prompt}\n\nChat History:\n{history}\n\nUser Query: {user_query}"
        
        # Get LLM's routing decision
        response = llm_service.generate(prompt)
        
        try:
            # Parse JSON from LLM response
            # LLMs sometimes add extra text, so we extract just the JSON object
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                # Default to GENERAL if no valid JSON found
                return {"agent": "GENERAL"}
        except:
            # Fallback to GENERAL on any parsing error
            return {"agent": "GENERAL"}

    def handle_request(self, user_query: str, session_id: str = "default"):
        """
        Main entry point for processing user requests.
        
        WHAT: Handles the complete request lifecycle from validation to response.
        HOW: 
            1. Validates input with guardrails.
            2. Saves user message to memory.
            3. Routes query to appropriate agent.
            4. Generates response using the selected agent.
            5. Saves AI response to memory.
        BIG PICTURE: This is the function called by the /chat API endpoint.
        
        Args:
            user_query: The user's message.
            session_id: The session identifier for conversation tracking.
            
        Returns:
            str: The AI-generated response or an error/validation message.
        """
        # =====================================================================
        # STEP 1: GUARDRAIL VALIDATION
        # Check for forbidden topics and verify relevance to manufacturing
        # =====================================================================
        is_valid, validation_msg = guardrail_service.validate_input(user_query)
        if not is_valid:
            # Block the request and return the validation message
            return validation_msg

        # =====================================================================
        # STEP 2: SAVE USER MESSAGE TO MEMORY
        # This enables conversation context for future messages
        # =====================================================================
        memory_service.add_user_message(session_id, user_query)
        
        # =====================================================================
        # STEP 3: ROUTE QUERY TO APPROPRIATE AGENT
        # LLM decides whether to use RAG, DIAGNOSTICS, or GENERAL
        # =====================================================================
        routing = self.route_query(user_query, session_id)
        agent = routing.get("agent", "GENERAL")
        
        # Get chat history for context in prompts
        history = memory_service.get_formatted_history(session_id)
        
        final_response = ""
        
        # =====================================================================
        # STEP 4: PROCESS REQUEST WITH SELECTED AGENT
        # =====================================================================
        
        if agent == "RAG":
            # -----------------------------------------------------------------
            # RAG AGENT: Retrieval-Augmented Generation
            # Used for: SOPs, manuals, procedures, documentation lookups
            # How: Retrieves relevant documents from vector DB, then uses LLM
            #      to generate an answer based on the retrieved context.
            # -----------------------------------------------------------------
            docs = rag_service.query(user_query)
            context = "\n".join([d.page_content for d in docs])
            
            rag_prompt = f"""Use the following context to answer the user's question.
            Context:
            {context}
            
            Chat History:
            {history}
            
            Current Question: {user_query}
            Answer:"""
            
            final_response = llm_service.generate(rag_prompt)
            
        elif agent == "DIAGNOSTICS":
            # -----------------------------------------------------------------
            # DIAGNOSTICS AGENT: Machine Health Analysis
            # Used for: Analyzing sensor data, detecting faults, health checks
            # How: Fetches current sensor readings from the simulator,
            #      then uses LLM to analyze and report on machine status.
            # -----------------------------------------------------------------
            data = simulator.get_readings()
            data_str = json.dumps(data, indent=2)
            
            diag_prompt = f"""Analyze the following sensor data and check for faults.
            Normal ranges: Temp 40-70, Vib < 1.0, Pressure 90-110.
            
            Current Data:
            {data_str}
            
            Chat History:
            {history}
            
            Current Question: {user_query}
            Analysis:"""
            
            final_response = llm_service.generate(diag_prompt)
            
        else:
            # -----------------------------------------------------------------
            # GENERAL AGENT: General Manufacturing Q&A
            # Used for: General questions that don't need documents or sensor data
            # How: Direct LLM conversation with chat history context.
            # -----------------------------------------------------------------
            gen_prompt = f"""You are a helpful assistant.
            
            Chat History:
            {history}
            
            Current User Query: {user_query}
            """
            final_response = llm_service.generate(gen_prompt)
            
        # =====================================================================
        # STEP 5: SAVE AI RESPONSE TO MEMORY
        # This enables the AI to reference its own previous responses
        # =====================================================================
        memory_service.add_ai_message(session_id, final_response)
        
        return final_response


# Global singleton instance of the Orchestrator
# Used by the chat API to handle all requests
orchestrator = Orchestrator()

