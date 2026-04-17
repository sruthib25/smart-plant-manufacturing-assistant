"""
================================================================================
CHAT API - AI CONVERSATION ENDPOINTS
================================================================================

This module provides the REST API endpoints for chat functionality.

WHAT IT DOES:
- Accepts user messages and returns AI-generated responses.
- Manages chat sessions (list, retrieve history, clear).
- Routes all chat requests through the Orchestrator.

ENDPOINTS:
- POST /chat         : Send a message and get AI response.
- GET /chat/sessions : List all active chat sessions.
- GET /chat/history/{id} : Get message history for a session.
- DELETE /chat/history/{id} : Clear a session's history.

HOW IT WORKS:
1. Frontend sends POST request with message and session_id.
2. API calls orchestrator.handle_request() which:
   - Validates input (guardrails)
   - Routes to appropriate agent
   - Returns AI-generated response
3. Response is returned to frontend.

BIG PICTURE:
- This is the primary interface for AI interactions.
- All chat messages flow through this endpoint.
- Sessions enable multiple concurrent conversations.

ARCHITECTURE:
    [Frontend Chat UI]
           |
           v (HTTP POST)
    [Chat API]  <-- YOU ARE HERE
           |
           v
    [Orchestrator]
           |
           v
    [LLM / RAG / Memory]
================================================================================
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.core.orchestrator import orchestrator

# Create router instance for chat-related endpoints
router = APIRouter()


class ChatRequest(BaseModel):
    """
    Request model for the chat endpoint.
    
    Attributes:
        message: The user's message text.
        session_id: Unique identifier for the chat session (default: "default").
                   Different session_ids maintain separate conversation histories.
    """
    message: str
    session_id: str = "default"


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Process a chat message and return AI response.
    
    WHAT: Main chat endpoint for AI conversations.
    HOW: Delegates to orchestrator.handle_request() which handles
         guardrails, routing, and response generation.
    BIG PICTURE: This is THE endpoint for all AI chat interactions.
    
    Args:
        request: ChatRequest with message and session_id.
        
    Returns:
        {"response": "AI generated response text"}
    """
    response = orchestrator.handle_request(request.message, request.session_id)
    return {"response": response}


@router.get("/chat/sessions")
async def list_sessions():
    """
    List all active chat sessions.
    
    WHAT: Returns IDs of all sessions with chat history.
    HOW: Queries MemoryService for session keys.
    BIG PICTURE: Used by frontend to populate session dropdown.
    
    Returns:
        {"sessions": ["session-id-1", "session-id-2", ...]}
    """
    from app.services.memory_service import memory_service
    return {"sessions": memory_service.get_all_sessions()}


@router.get("/chat/history/{session_id}")
async def get_history(session_id: str):
    """
    Get the message history for a specific session.
    
    WHAT: Returns all messages in a session.
    HOW: Queries MemoryService for session messages.
    BIG PICTURE: Used when user switches sessions in frontend.
    
    Args:
        session_id: The session to retrieve history for.
        
    Returns:
        {"history": [{"role": "user", "content": "..."}, ...]}
    """
    from app.services.memory_service import memory_service
    return {"history": memory_service.get_messages(session_id)}


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear all messages from a session.
    
    WHAT: Deletes all chat history for a session.
    HOW: Calls MemoryService.clear_history().
    BIG PICTURE: Used when user clicks "Clear History" button.
    
    Args:
        session_id: The session to clear.
        
    Returns:
        {"status": "success", "message": "History cleared"}
    """
    from app.services.memory_service import memory_service
    memory_service.clear_history(session_id)
    return {"status": "success", "message": "History cleared"}
