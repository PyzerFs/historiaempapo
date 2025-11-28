from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
import logging  # Para logs no terminal

# Logs no terminal para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega a chave do .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("❌ Chave OpenAI não encontrada! Coloque OPENAI_API_KEY=sk-... no .env")

logger.info(f"🔑 Chave OpenAI carregada: {'Sim' if openai.api_key else 'Não'}")

app = FastAPI()


# CORS amplo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelo de dados para a pergunta
class Pergunta(BaseModel):
    prompt: str = ""


# Serve o HTML na raiz (GET /)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        logger.info("📄 HTML servido na raiz")
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>index.html não encontrado! Crie o arquivo.</h1>")


# Status da API (GET /api)
@app.get("/api")
def status():
    return {"status": "online com OpenAI", "model": "gpt-3.5-turbo"}


# GET teste no responder (para você acessar no browser sem erro 405)
@app.get("/api/responder")
async def responder_get():
    logger.info("🧪 Teste GET no /api/responder")
    return {"erro": "Este endpoint é POST! Use o microfone ou POST JSON. Exemplo: {'prompt': 'Olá'}", "metodo": "GET"}


# Endpoint principal (POST /api/responder) — com logs!
@app.post("/api/responder")
async def responder(p: Pergunta):
    logger.info(f"📩 Recebido POST: prompt='{p.prompt}'")
    
    if not p.prompt.strip():
        texto = "Silêncio... as engrenagens aguardam tua voz, ó inventor. ♡"
    else:
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é uma assistente steampunk carismática da era vitoriana, poética e calorosa. Fale em PT-BR refinado, com vapor, engrenagens e corações. Tema: Revolução Industrial. Seja encantadora!"},
                    {"role": "user", "content": p.prompt}
                ],
                temperature=0.9,
                max_tokens=500
            )
            texto = response.choices[0].message.content.strip()
            logger.info(f"🤖 Resposta GPT gerada: {texto[:50]}...")
        except Exception as e:
            texto = f"Ó falha no éter! Erro: {str(e)}. Verifique a chave ou créditos OpenAI."
            logger.error(f"❌ Erro OpenAI: {e}")
    
    logger.info(f"📤 Enviando resposta: {texto[:50]}...")
    return {"texto": texto}
