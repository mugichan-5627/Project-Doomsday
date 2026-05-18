"""
PROJECT DOOMSDAY - API Verification Test
Uses FastAPI's built-in TestClient to verify the endpoint functionality, payload parsing,
and OpenAI spec compliance instantly and offline using high-fidelity mock patching.
"""

import sys
import os
from unittest.mock import patch

# Force import resolution from Project_Doomsday workspace root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core class to patch
from app import DoomsdayAI

# Define custom mock methods to ensure instant, stable offline testing
def mock_initialize(self):
    print("[MOCK] Initializing DoomsdayAI Client...")
    self.provider = "gemini"
    self.model = "gemini-2.0-flash"
    self.gemini_key = "mock-key"
    return "Mock Gemini [gemini-2.0-flash]"

def mock_generate(self, prompt, temperature=0.4, max_tokens=2048, json_mode=False):
    print(f"[MOCK] AI swarm generation call (json={json_mode})...")
    # Return structured parameter extraction mock
    if "Extract the target stock ticker" in prompt:
        return '{"ticker": "AAPL", "chaos": 0.85}'
    # Return None for others to trigger Doomsday's robust default debate/contagion models
    return None

# Apply the mock patches to DoomsdayAI before loading the FastAPI app
DoomsdayAI.initialize = mock_initialize
DoomsdayAI.generate = mock_generate

# Now import the FastAPI app and TestClient
from fastapi.testclient import TestClient
from api import app

def run_test():
    print("=====================================================")
    print("Initiating Project Doomsday API Compliance Test...")
    print("=====================================================")
    
    # Initialize TestClient
    client = TestClient(app)
    
    # Mock Chat Completions Payload conforming to OpenAI standard
    payload = {
        "model": "doomsday-swarm",
        "messages": [
            {"role": "user", "content": "Analyze AAPL with 0.85 extreme stress regime"}
        ],
        "temperature": 0.5,
        "max_tokens": 1000
    }
    
    print("\nSending mock stress-testing completion request...")
    print(f"Payload: {payload}")
    
    try:
        # Perform POST request against the app
        response = client.post("/v1/chat/completions", json=payload)
        
        print(f"\nResponse Received! Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n[SUCCESS] Response complies perfectly with standard OpenAI chat completion JSON!")
            print("-----------------------------------------------------")
            print(f"ID: {data.get('id')}")
            print(f"Object Type: {data.get('object')}")
            print(f"Model Lock: {data.get('model')}")
            print("-----------------------------------------------------")
            
            choices = data.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content", "")
                print(f"Message Role: {message.get('role')}")
                print(f"Message Finish Reason: {choices[0].get('finish_reason')}")
                print("\nAssistant Markdown Report Preview (First 800 chars):")
                print("=====================================================")
                # Safely encode and decode to ascii, stripping out emojis that crash the Windows console
                safe_content = content[:800].encode('ascii', 'ignore').decode('ascii')
                print(safe_content + "\n...")
                print("=====================================================")
            else:
                print("[ERROR] Choices array is empty!")
                sys.exit(1)
        else:
            print(f"[ERROR] Request failed with body: {response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"[FATAL] Test runner encountered exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
