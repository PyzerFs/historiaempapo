from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import base64
import uuid

try:
    import google.generativeai as genai
    GENAI = True
except:
    GENAI = False

try:
    from gtts import gTTS
    GTTS = True
except:
    GTTS = False

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

# PEGA A CHAVE CORRETAMENTE
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY and GENAI:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    print("Gemini 1.5 Flash carregado com sucesso!")
else:
    model = None
    print("AVISO: GEMINI_API_KEY não encontrada ou biblioteca ausente → usando fallback")

def fallback_audio(texto):
    if not GTTS: return ""
    fname = f"/tmp/{uuid.uuid4().hex}.mp3"
    try:
        gTTS(texto, lang="pt").save(fname)
        return base64.b64encode(open(fname, "rb").read()).decode()
    except:
        return ""

def placeholder_img():
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAr8B9yR2cYwAAAAASUVORK5CYII="

@app.get("/")
def home():
    return {"status": "online", "gemini": bool(model)}

@app.post("/api/responder")
async def responder(body: Prompt):
    prompt = body.prompt.strip() or "Olá"

    if model:
        try:
            # Texto + áudio + imagem tudo em uma única chamada (mais rápido e estável)
            response = model.generate_content(
                [
                    f"Responda em português, de forma literária, feminina, poética e steampunk: {prompt}",
                    "Gere também uma imagem steampunk relacionada e um áudio com voz feminina suave em português."
                ],
                generation_config={
                    "temperature": 0.9,
                    "response_mime_type": "multipart/mixed"  # permite texto + áudio + imagem
                }
            )

            texto = "Minha mente de bronze ainda processa sua pergunta..."
            audio_b64 = ""
            img_b64 = placeholder_img()

            for part in response.parts:
                if part.text:
                    texto = part.text
                if hasattr(part, "inline_data") and part.inline_data:
                    mime = part.inline_data.mime_type
                    data = part.inline_data.data
                    if mime.startswith("audio"):
                        audio_b64 = data
                    if mime.startswith("image"):
                        img_b64 = data

            return {
                "texto": texto,
                "audioBase64": audio_b64,
                "imagens": [f"data:image/png;base64,{img_b64}"]
            }

        except Exception as e:
            print("ERRO GEMINI:", str(e))

    # FALLBACK 100% funcional
    texto = f"Ó nobre inventor, em meio ao vapor e engrenagens, ouvi tua voz: \"{prompt}\". Que o fogo da curiosidade nunca se apague em teu peito!"
    audio = fallback_audio(texto)

    return {
        "texto": texto,
        "audioBase64": audio,
        "imagens": [f"data:image/png;base64,{placeholder_img()}"]
    }
