# teste_gemini.py
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

resposta = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Responda apenas: conexão ok"
)

print(resposta.text)