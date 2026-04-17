"""
================================================================================
SMART MANUFACTURING ASSISTANT - MAIN APPLICATION ENTRY POINT
================================================================================

This is the main entry point for the FastAPI backend application.

WHAT IT DOES:
- Initializes the FastAPI application instance.
- Registers all API routers (sensors, chat, maintenance).
- Provides a health check endpoint at the root path.

HOW IT WORKS:
- FastAPI is a modern, fast web framework for building APIs with Python.
- Routers are modular components that group related endpoints together.
- When run directly, it starts a Uvicorn ASGI server on port 8090.

BIG PICTURE:
- This file is the "backbone" of the backend.
- All HTTP requests from the frontend (Streamlit) come here first.
- Requests are then routed to the appropriate handler (sensors, chat, or maintenance).
- The backend communicates with services (LLM, RAG, Memory, Guardrails, etc.)
  to process requests and return responses.

ARCHITECTURE:
    [Frontend (Streamlit)]
            |
            v
    [main.py - FastAPI Server]  <-- YOU ARE HERE
            |
    +-------+-------+-------+
    |       |       |       |
    v       v       v       v
  sensors  chat  maintenance  (API Routers)
    |       |       |
    v       v       v
  [Services: LLM, RAG, Memory, Guardrails, Inventory, Simulator]
================================================================================
"""

from fastapi import FastAPI
from app.api import sensors, chat

# Initialize FastAPI application with a descriptive title
# This title appears in the auto-generated API documentation (Swagger UI at /docs)
app = FastAPI(title="Smart Manufacturing Assistant")

# Register the Sensors API router
# Provides endpoints for fetching simulated machine sensor data (temperature, vibration, pressure)
app.include_router(sensors.router, tags=["Sensors"])

# Register the Chat API router
# Provides the main chat endpoint for AI-powered conversations
# Handles memory, guardrails, and multi-agent routing
app.include_router(chat.router, tags=["Chat"])

# Register the Maintenance API router
# Provides endpoints for spare parts inventory and CSV log analysis
from app.api import maintenance
app.include_router(maintenance.router, tags=["Maintenance"])


@app.get("/")
def read_root():
    """
    Health check endpoint.
    
    WHAT: Returns a simple status message indicating the system is operational.
    HOW: Just returns a JSON object with a message.
    BIG PICTURE: Used by monitoring systems or users to verify the backend is running.
    """
    return {"message": "System Operational"}


# Development server startup
# Only runs when this file is executed directly (not when imported)
if __name__ == "__main__":
    import uvicorn
    # Start Uvicorn ASGI server
    # - host="0.0.0.0": Accept connections from any network interface
    # - port=8090: The port the server listens on
    # - reload=True: Auto-restart when code changes (development mode)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8090, reload=True)

