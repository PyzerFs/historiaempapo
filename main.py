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

# Frases steampunk literárias femininas (sempre funciona)
RESPOSTAS_STEAMPUNK = [
    "Ó nobre alma de bronze e vapor, ouvi tua voz através das engrenagens do tempo...",
]

@app.post("/api/responder")
async def responder(body: Prompt):
    pergunta = body.prompt.strip()
    
    if not pergunta:
        pergunta = "silêncio"

    # Resposta poética aleatória + repete a pergunta de forma elegante
    import random
    intro = random.choice(RESPOSTAS_STEAMPUNK)
    resposta = f"{intro}\n\nTu perguntaste: \"{pergunta}\"\n\nE eu, feita de engrenagens e sonhos, te digo: o conhecimento é o maior combustível do espírito humano. Continue perguntando, pois cada questão acende uma nova fornalha no progresso da humanidade."

    return {
        "texto": resposta,
        "audioBase64": ""  # deixa vazio → o front vai usar voz do navegador
        # imagens removidas para evitar erro
    }
