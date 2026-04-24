import httpx
import time
import sys

def run_test():
    with httpx.Client() as client:
        # Get Auth Token
        res = client.post("http://localhost:8000/auth/login", data={"username": "demo@finsight.app", "password": "demo123"})
        if res.status_code != 200:
            print("Auth failed:", res.status_code, res.text)
            sys.exit(1)
        
        token = res.json()["access_token"]
        print("Successfully obtained auth token.")
        
        # Trigger event in Service A
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"amount": 5550, "currency": "USD", "category": "Food", "merchant": "E2E Integration Test", "date": "2024-04-24"}
        res2 = client.post("http://localhost:8001/ingestion/manual", json=payload, headers=headers)
        
        print("Ingestion response:", res2.status_code, res2.text)
        if res2.status_code == 200:
            print("Ingestion successful. RabbitMQ publish should have triggered.")

if __name__ == "__main__":
    run_test()
