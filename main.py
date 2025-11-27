from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Pergunta(BaseModel):
    prompt: str = ""        # aceita vazio também

@app.get("/")
def home():
    return {"status": "online"}

@app.post("/api/responder")
async def responder(p: Pergunta):
    texto = f"Ó nobre inventor, ouvi tua voz: «{p.prompt or 'silêncio'}».\n\nCom vapor e engrenagens, respondo-te com carinho steampunk: o futuro pertence aos que perguntam. ♡"
    return {"texto": texto}
