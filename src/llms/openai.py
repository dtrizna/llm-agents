import openai

class OpenAI:
    def __init__(
            self,
            api_key: str,
            model: str = "gpt-3.5-turbo",
            max_tokens: int = 10,
    ):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens

    def query(self, prompt: str) -> str:
        client = openai.OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content
