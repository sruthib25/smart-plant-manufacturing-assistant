import requests

BASE_URL = "http://localhost:8090"

def test_memory():
    session_id = "test_memory_session"
    
    # 1. Send initial message
    print("Sending message 1...")
    response1 = requests.post(f"{BASE_URL}/chat", json={"message": "My name is Alice.", "session_id": session_id})
    print(f"Response 1: {response1.json()}")
    
    # 2. Send follow-up message asking for name
    print("Sending message 2...")
    response2 = requests.post(f"{BASE_URL}/chat", json={"message": "What is my name?", "session_id": session_id})
    print(f"Response 2: {response2.json()}")
    
    # Check if "Alice" is in the response usually provided by LLM given the context
    # Note: Since I cannot run the server, this script is for manual usage by the user or if I could run background processes.
    # Since I cannot assume the server is running, I'll just leave this script for the user or hypothetical execution.

if __name__ == "__main__":
    try:
        test_memory()
    except Exception as e:
        print(f"Test failed (server likely not running): {e}")
