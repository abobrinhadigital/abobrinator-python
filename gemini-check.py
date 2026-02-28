import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Modelos disponíveis para sua chave:")
try:
    for model in client.models.list():
        # Usando o nome sugerido pelo próprio erro do sistema
        actions = getattr(model, 'supported_actions', 'N/A')
        print(f"- {model.name} (Suporta: {actions})")
except Exception as e:
    print(f"Erro ao listar: {e}")