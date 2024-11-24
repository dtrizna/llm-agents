import os

import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from src.llms.google import Gemini

from dotenv import load_dotenv
load_dotenv()

gemini = Gemini(api_key=os.environ["GEMINI_API_KEY"])

print(gemini.query("What is the capital of France?"))
