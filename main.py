# main.py - VERSÃO CORRIGIDA E FUNCIONAL NO RENDER
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import base64
import uuid

# OPTIONAL Gemini
try:
    import google.generativeai as genai
    GENAI = True
except ImportError:
    GENAI = False

# OPTIONAL gTTS fallback
try:
    from gtts import gTTS
    GTTS = True
except ImportError:
    GTTS = False

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

# CORRETO: pega do ambiente (Render)
API_KEY = os.getenv("GEMINI_API_KEY")  # <-- Nome da variável no Render

if API_KEY and GENAI:
    genai.configure(api_key=API_KEY)
    text_model = genai.GenerativeModel("gemini-1.5-flash")
    image_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    text_model = None
    image_model = None
    print("Gemini não configurado. Usando fallback.")

def gerar_audio_fallback(texto):
    if not GTTS:
        return ""
    fname = f"/tmp/tts_{uuid.uuid4().hex}.mp3"
    try:
        tts = gTTS(texto, lang="pt")
        tts.save(fname)
        return base64.b64encode(open(fname, "rb").read()).decode()
    except:
        return ""

def imagem_placeholder():
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAr8B9yR2cYwAAAAASUVORK5CYII="

@app.get("/")
async def root():
    return {"message": "Assistente Steampunk rodando!"}

@app.post("/api/responder")
async def responder(body: Prompt):
    prompt = body.prompt.strip()

    # Tenta usar Gemini
    if API_KEY and GENAI and text_model:
        try:
            # Texto literário
            response = text_model.generate_content(
                f"Responda em português, de forma literária, feminina, poética e educativa, no universo steampunk: {prompt}"
            )
            texto = response.text

            # Áudio com voz feminina
            audio_response = text_model.generate_content(
                texto,
                generation_config={
                    "response_mime_type": "audio/mp3",
                    "temperature": 0.7
                }
            )
            audio_b64 = audio_response.candidates[0].content.parts[0].inline_data.data

            # Imagem steampunk
            img_response = image_model.generate_content([
                f"Crie uma ilustração detalhada em estilo steampunk vitoriano, engrenagens, vapor, bronze, tons sépia e laranja, alta qualidade: {prompt}",
            ], generation_config={"response_mime_type": "image/png"})

            img_b64 = img_response.candidates[0].content.parts[0].inline_data.data

            return {
                "texto": texto,
                "audioBase64": audio_b64,
                "imagens": [f"data:image/png;base64,{img_b64}"]
            }

        except Exception as e:
            print("Erro no Gemini:", str(e))

    # Fallback se Gemini falhar
    texto = f"Ó nobre inventor, em meio às engrenagens do tempo... {prompt}. Que o vapor da curiosidade jamais se esgote em teu peito."
    audio = gerar_audio_fallback(texto)
    img = imagem_placeholder()

    return {
        "texto": texto,
        "audioBase64": audio or "",
        "imagens": [f"data:image/png;base64,{img}"]
    }
