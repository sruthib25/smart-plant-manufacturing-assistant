import requests

BASE_URL = "http://localhost:8090"

def get_sensor_data():
    try:
        response = requests.get(f"{BASE_URL}/sensors")
        if response.status_code == 200:
            return response.json()
    except:
        return {}
    return {}

def send_chat_message(message: str, session_id: str = "default"):
    try:
        response = requests.post(f"{BASE_URL}/chat", json={"message": message, "session_id": session_id})
        if response.status_code == 200:
            return response.json().get("response", "Error getting response")
    except Exception as e:
        return f"Error: {str(e)}"
    return "Error communicating with backend"

def trigger_fault(machine_id: str, fault_type: str):
    try:
        response = requests.post(f"{BASE_URL}/fault", json={"machine_id": machine_id, "fault_type": fault_type})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_chat_sessions():
    try:
        response = requests.get(f"{BASE_URL}/chat/sessions")
        if response.status_code == 200:
            return response.json().get("sessions", [])
    except:
        return []
    return []

def get_chat_history(session_id: str):
    try:
        response = requests.get(f"{BASE_URL}/chat/history/{session_id}")
        if response.status_code == 200:
            return response.json().get("history", [])
    except:
        return []

def delete_chat_history(session_id: str):
    try:
        response = requests.delete(f"{BASE_URL}/chat/history/{session_id}")
        return response.status_code == 200
    except:
        return False
    return []

def get_inventory():
    try:
        response = requests.get(f"{BASE_URL}/maintenance/inventory")
        if response.status_code == 200:
            return response.json().get("inventory", [])
    except:
        return []
    return []

def trigger_scarcity_alert(machine_id: str, part_name: str):
    try:
        response = requests.post(f"{BASE_URL}/maintenance/alert", json={"machine_id": machine_id, "part_name": part_name})
        return response.status_code == 200
    except:
        return False

def analyze_log(file_bytes):
    try:
        files = {"file": ("log.csv", file_bytes, "text/csv")}
        response = requests.post(f"{BASE_URL}/maintenance/analyze-log", files=files)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None
