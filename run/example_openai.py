import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from src.llms.openai import OpenAI

# NOTE: free tier should allow gpt-3.5-turbo, but still errors with 'insufficient quota'
# see: https://platform.openai.com/docs/guides/rate-limits?context=tier-free#usage-tiers
openai = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    model="gpt-3.5-turbo",
    max_tokens=3,
)

print(openai.query("What is the capital of France?"))
