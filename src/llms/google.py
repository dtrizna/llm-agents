import google.generativeai as genai

class Gemini:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

    def query(self, prompt: str) -> str:
        """
        Query the Gemini API with a prompt and return the response.
        """
        response = self.client.generate_content(prompt)
        return response.text
