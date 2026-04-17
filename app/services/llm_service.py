"""
================================================================================
LLM SERVICE - OLLAMA/MISTRAL INTEGRATION
================================================================================

This module provides the interface to the local Large Language Model (LLM).

WHAT IT DOES:
- Communicates with Ollama server running locally.
- Sends prompts and receives AI-generated text responses.
- Provides both single-turn (generate) and multi-turn (chat) interfaces.

WHY OLLAMA + TINYLLAMA?
- **Privacy**: All data stays on your machine - critical for sensitive manufacturing data.
- **No API Costs**: Unlike OpenAI/Claude, no per-token charges.
- **Low Latency**: No internet round-trip, faster responses.
- **Offline Capable**: Works without internet connection.
- **TinyLlama**: Lightweight model that runs on systems with limited RAM.

HOW IT WORKS:
1. Ollama runs as a local server on port 11434.
2. This service sends HTTP POST requests to Ollama's API.
3. Ollama processes the prompt using the Mistral model.
4. The generated text is returned to the caller.

BIG PICTURE:
- This is the "AI engine" that powers all intelligent responses.
- Used by: Orchestrator (routing, agents), Guardrails (relevance check).
- Every AI-generated response in the system flows through this service.

PREREQUISITES:
1. Install Ollama: https://ollama.ai
2. Pull TinyLlama: `ollama pull tinyllama`
3. Ollama runs automatically or start with: `ollama serve`

ARCHITECTURE:
    [Orchestrator / Guardrails]
              |
              v
    [LLM Service]  <-- YOU ARE HERE
              |
              v (HTTP POST)
    [Ollama Server :11434]
              |
              v
    [TinyLlama Model]
================================================================================
"""

import requests
import json
from typing import Dict, Any, Generator


class LLMService:
    """
    Service class for interacting with Ollama's local LLM API.
    
    Ollama exposes a REST API similar to OpenAI's, making it easy to switch
    between local and cloud models if needed.
    
    Attributes:
        model: The model name to use (default: "mistral")
        base_url: The Ollama server URL (default: http://localhost:11434)
    """
    
    def __init__(self, model: str = "tinyllama", base_url: str = "http://localhost:11434"):
        """
        Initialize the LLM service with model and server configuration.
        
        Args:
            model: Name of the Ollama model to use. Must be pulled first.
                   Common options: "tinyllama", "llama2", "codellama"
            base_url: URL where Ollama server is running.
        """
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        """
        Generate text from a single prompt (completion-style).
        
        WHAT: Sends a prompt to the LLM and returns the generated text.
        HOW: Makes a POST request to Ollama's /api/generate endpoint.
        BIG PICTURE: Used for single-turn interactions like query routing,
                     relevance checking, and knowledge-grounded responses.
        
        Args:
            prompt: The text prompt to send to the model.
            
        Returns:
            str: The generated text response, or an error message if failed.
            
        Example:
            >>> llm_service.generate("What is machine learning?")
            "Machine learning is a subset of AI that..."
        """
        # Ollama's generate endpoint for completion-style requests
        url = f"{self.base_url}/api/generate"
        
        # Request payload
        payload = {
            "model": self.model,      # Which model to use
            "prompt": prompt,          # The text prompt
            "stream": False            # Get complete response (not streaming)
        }
        
        try:
            # Send request to Ollama
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Extract the response text from JSON
            return response.json().get("response", "")
            
        except requests.exceptions.ConnectionError:
            # Ollama server is not running
            return "Error: Could not connect to Ollama. Is it running?"
        except Exception as e:
            # Other errors (timeout, invalid response, etc.)
            return f"Error: {str(e)}"

    def chat(self, messages: list) -> str:
        """
        Generate a response in a multi-turn conversation (chat-style).
        
        WHAT: Sends a list of messages (conversation history) and gets a reply.
        HOW: Makes a POST request to Ollama's /api/chat endpoint.
        BIG PICTURE: Used when conversation context matters. Messages include
                     role (user/assistant/system) and content.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
                     Example: [{"role": "user", "content": "Hello"}]
            
        Returns:
            str: The assistant's response text, or an error message.
            
        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are a helpful assistant."},
            ...     {"role": "user", "content": "What is 2+2?"}
            ... ]
            >>> llm_service.chat(messages)
            "2+2 equals 4."
        """
        # Ollama's chat endpoint for conversation-style requests
        url = f"{self.base_url}/api/chat"
        
        # Request payload with message history
        payload = {
            "model": self.model,
            "messages": messages,      # Full conversation history
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            # Chat API returns response in a nested structure
            return response.json().get("message", {}).get("content", "")
            
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama. Is it running?"
        except Exception as e:
            return f"Error: {str(e)}"


# Global singleton instance
# Created once when module is imported, reused throughout the application
llm_service = LLMService()

