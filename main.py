from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

# Usa Gemini direto (sem try/except pra ver erro real)
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

@app.get("/")
def home():
    return {"status": "Ela está viva!", "gemini": "conectado"}

@app.post("/api/responder")
async def responder(body: Prompt):
    pergunta = body.prompt.strip() or "olá"

    try:
        resposta = model.generate_content(
            f"Responda em português brasileiro, com voz feminina, delicada, poética e totalmente steampunk vitoriana: {pergunta}",
            generation_config={"temperature": 0.9}
        )
        texto = resposta.text
    except Exception as e:
        texto = f"Ó inventor... o éter está instável agora. Mas estou aqui. Tu disseste: \"{pergunta}\". Continua falando comigo ♡"

    return {"texto": texto}
