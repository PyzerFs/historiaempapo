from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, base64, uuid

# OPTIONAL Gemini
try:
    import google.generativeai as genai
    GENAI = True
except:
    GENAI = False

# OPTIONAL gTTS fallback
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
    allow_headers=["*"]
)

class Prompt(BaseModel):
    prompt: str

# Configure Gemini (if installed and key present)
API_KEY = os.getenv("AIzaSyAea_AaP3XWGdChgm9aqV_FXzN0zpinmT0")

if API_KEY and GENAI:
    genai.configure(api_key=API_KEY)
    text_model = genai.GenerativeModel("gemini-2.0-flash")
    image_model = genai.GenerativeModel("gemini-2.0-flash")
else:
    text_model = None
    image_model = None


# Fallback TTS
def gerar_audio_fallback(texto):
    if not GTTS:
        return ""
    fname = f"/tmp/tts_{uuid.uuid4().hex}.mp3"
    gTTS(texto, lang="pt").save(fname)
    b64 = base64.b64encode(open(fname, "rb").read()).decode()
    return b64


# Fallback placeholder image
def imagem_placeholder():
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAr8B9yR2cYwAAAAASUVORK5CYII="


@app.post("/api/responder")
async def responder(body: Prompt):
    prompt = body.prompt.strip()

    # TRY GEMINI
    if API_KEY and GENAI and text_model:
        try:
            txt = text_model.generate_content(f"Responda de forma literária, feminina e educativa: {prompt}")
            texto = txt.text

            # AUDIO
            aud = text_model.generate_content(
                f"Leia em voz feminina suave: {texto}",
                generation_config={"response_mime_type": "audio/mp3"}
            )
            audio_b64 = aud.response.candidates[0].content.parts[0].inlineData.data

            # IMAGE
            img = image_model.generate_content(
                f"Crie uma ilustração estilo steampunk sobre: {prompt}",
                generation_config={"response_mime_type": "image/png"}
            )
            img_b64 = img.response.candidates[0].content.parts[0].inlineData.data

            return {
                "texto": texto,
                "audioBase64": audio_b64,
                "imagens": [f"data:image/png;base64,{img_b64}"]
            }
        except Exception as e:
            print("GEMINI ERROR:", e)

    # FALLBACK
    texto = "Era de vapor e aço… " + prompt
    audio = gerar_audio_fallback(texto)
    img = imagem_placeholder()

    return {
        "texto": texto,
        "audioBase64": audio,
        "imagens": [f"data:image/png;base64,{img}"]
    }
