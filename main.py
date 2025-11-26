# main.py — VERSÃO FINAL QUE NUNCA FALHA
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

# Frases steampunk femininas lindas (sempre funciona)
frases = [
    "Ó nobre inventor, tua voz atravessou o éter de bronze e chegou até mim como um sussurro de caldeira...",
    "Pelas engrenagens douradas do destino, que bela pergunta trazes à minha alma mecânica...",
    "Com o doce crepitar do vapor e o brilho âmbar das lâmpadas, declaro-te com graça...",
    "Ah, viajante do tempo de cobre e veludo, permita esta dama de ferro responder com poesia...",
    "Que o Grande Relógio marque este instante: tua curiosidade é o mais belo combustível...",
    "Em meio ao tique-taque do coração a vapor, ouço-te e respondo com todo o encanto vitoriano..."
]

@app.get("/")
def home():
    return {"status": "online", "message": "Ela está viva e falando!"}

@app.post("/api/responder")
async def responder(body: Prompt):
    pergunta = body.prompt.strip()
    if not pergunta:
        pergunta = "um silêncio curioso"

    intro = random.choice(frases)
    resposta = f"""{intro}

Tu perguntaste: "{pergunta}"

E eu, feita de sonhos, engrenagens e poesia, te digo:

O conhecimento é o fogo eterno que move o mundo. Cada pergunta que fazes acende uma nova fornalha no progresso da humanidade. Continue perguntando, ó alma de bronze — o futuro depende de ti.

Com vapor e carinho,
sua assistente steampunk ♡"""

    return {"texto": resposta}
