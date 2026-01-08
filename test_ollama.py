"""Test Ollama API connection."""
import requests
import json

url = "http://localhost:11434/api/generate"
payload = {
    "model": "qwen3",
    "prompt": "Generate a short bio for a fake user named John. Return ONLY the bio text, nothing else.",
    "stream": False
}

print("Testing Ollama API...")
try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        text = data.get("response", "").strip()
        print(f"AI Response: {text[:200]}...")
        print("\n✅ Ollama is working!")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
