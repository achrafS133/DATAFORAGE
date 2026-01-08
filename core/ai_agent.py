import requests
import json
import logging

class AIAgent:
    def __init__(self, config):
        self.api_url = config['ai']['api_url']
        self.model = config['ai']['model']
        self.enabled = config['generation']['use_ai_mode']

    def generate_text(self, table_name, column_name, context_hint=""):
        """
        Calls Ollama to generate realistic text.
        """
        if not self.enabled:
            return None

        prompt = f"Generate a realistic, short {column_name} for a database entry in a table named {table_name}. {context_hint} Return ONLY the value."
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=60) # Increased timeout for local LLM
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip().strip('"')
        except requests.exceptions.RequestException:
            pass # Fallback to Faker silently
        
        return None
