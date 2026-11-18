import requests
import os


class OllamaProvider:

    def __init__(self, model="llama3.2"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt):

        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(
            self.url,
            json=data,
            timeout=120
        )

        response.raise_for_status()

        return response.json()["response"]


class GeminiProvider:

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("Gemini API key not found.")

        from google import genai

        self.client = genai.Client(api_key=self.api_key)

    def generate(self, prompt):

        response = self.client.models.generate_content(
            model="gemini-3.1-flash",
            contents=prompt
        )

        return response.text


class LLMClient:

    def __init__(self, provider):
        self.provider = provider

    def generate(self, prompt):
        return self.provider.generate(prompt)