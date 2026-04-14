import requests
import io
import pandas as pd

BASE_URL = "http://localhost:8090"

def test_maintenance():
    # 1. Test Inventory
    print("Testing Inventory...")
    try:
        resp = requests.get(f"{BASE_URL}/maintenance/inventory")
        if resp.status_code == 200:
            print("Inventory OK:", len(resp.json().get("inventory", [])))
        else:
            print("Inventory Failed:", resp.text)
    except Exception as e:
        print(f"Inventory Error: {e}")

    # 2. Test Alert
    print("\nTesting Alert...")
    try:
        resp = requests.post(f"{BASE_URL}/maintenance/alert", json={"machine_id": "m1", "part_name": "TestPart"})
        if resp.status_code == 200:
            print("Alert OK:", resp.json())
        else:
            print("Alert Failed:", resp.text)
    except Exception as e:
        print(f"Alert Error: {e}")

    # 3. Test Log Analysis
    print("\nTesting Log Analysis...")
    try:
        # Create dummy CSV
        df = pd.DataFrame({
            "timestamp": range(10),
            "temperature": [50 + i for i in range(10)],
            "vibration": [0.1 * i for i in range(10)]
        })
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        files = {"file": ("test_log.csv", csv_buffer, "text/csv")}
        resp = requests.post(f"{BASE_URL}/maintenance/analyze-log", files=files)
        
        if resp.status_code == 200:
            result = resp.json()
            print("Analysis OK")
            print("Stats:", result.get("stats"))
            print("Report Length:", len(result.get("report", "")))
        else:
            print("Analysis Failed:", resp.text)
            
    except Exception as e:
        print(f"Analysis Error: {e}")

if __name__ == "__main__":
    test_maintenance()
