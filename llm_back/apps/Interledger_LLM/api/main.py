from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .agent.main import process_message_with_extraction, get_client
from .payment import send_payment_async, DEFAULT_ASSET_CODE, DEFAULT_ASSET_SCALE
import os
import json
import time
import tempfile
import base64
from pathlib import Path
from dotenv import load_dotenv
import requests

# Cargar variables de entorno desde .env si existe
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../../"))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

app = FastAPI(title="WhatsApp LLM API", version="1.0.0")

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "whatsapp-verify-token")


class MediaItem(BaseModel):
    type: str
    source: str


class WhatsAppMessage(BaseModel):
    """Modelo para recibir mensajes de WhatsApp"""
    wa_id: str
    name: str
    message: str
    identity_key_hash: Optional[str] = None
    media: Optional[List[MediaItem]] = None


class LLMResponse(BaseModel):
    """Modelo para la respuesta del LLM"""
    monto: Optional[float] = None
    destinatario: Optional[str] = None
    response: str
    wa_id: str
    name: str
    audio_url: Optional[str] = None  # URL del audio si la entrada era audio
    image_analysis: Optional[Dict[str, Any]] = None
    payment_payload: Optional[Dict[str, Any]] = None
    payment_status: Optional[Dict[str, Any]] = None
    payment_confirmation: Optional[Dict[str, Any]] = None


AUDIO_OUTPUT_DIR = Path(__file__).resolve().parent / "audio_responses"
AUDIO_OUTPUT_DIR.mkdir(exist_ok=True)


def _is_remote_url(path: str) -> bool:
    return path.startswith("http://") or path.startswith("https://")


def _is_audio_source(source: str) -> bool:
    audio_exts = (".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac")
    if _is_remote_url(source):
        return any(source.lower().split("?")[0].endswith(ext) for ext in audio_exts)
    if os.path.isfile(source):
        return source.lower().endswith(audio_exts)
    return False


def _is_image_source(source: str) -> bool:
    image_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp")
    if _is_remote_url(source):
        return any(source.lower().split("?")[0].endswith(ext) for ext in image_exts)
    if os.path.isfile(source):
        return source.lower().endswith(image_exts)
    return False


def _download_to_temp(url: str, suffix: str) -> str:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as tmp:
        tmp.write(response.content)
    return temp_path


def _transcribe_audio(source: str) -> str:
    client = get_client()
    temp_path = None
    file_path = source

    if _is_remote_url(source):
        _, ext = os.path.splitext(source.split("?")[0])
        suffix = ext if ext else ".mp3"
        temp_path = _download_to_temp(source, suffix=suffix)
        file_path = temp_path

    try:
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                response_format="text",
                language="es",
            )
        return transcription.strip()
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def _synthesize_audio_response(text: str) -> str:
    client = get_client()
    timestamp = int(time.time())
    filename = AUDIO_OUTPUT_DIR / f"respuesta_{timestamp}.mp3"

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
    )

    with open(filename, "wb") as audio_file:
        audio_file.write(response.content)

    return f"file://{filename.absolute()}"


def _encode_image_to_base64(source: str) -> Dict[str, str]:
    if _is_remote_url(source):
        response = requests.get(source, timeout=30)
        response.raise_for_status()
        content = response.content
        path = source.split("?")[0]
    else:
        with open(source, "rb") as image_file:
            content = image_file.read()
        path = source

    encoded = base64.b64encode(content).decode("utf-8")
    _, ext = os.path.splitext(path.lower())
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    mime_type = mime_map.get(ext, "image/png")
    return {"data": encoded, "mime": mime_type, "is_remote": _is_remote_url(source), "original": source}


def _parse_json_text(text: str) -> Dict[str, Any]:
    candidate = text.strip()
    if "```json" in candidate:
        start = candidate.find("```json") + 7
        end = candidate.find("```", start)
        candidate = candidate[start:end].strip()
    elif "```" in candidate:
        start = candidate.find("```") + 3
        end = candidate.find("```", start)
        candidate = candidate[start:end].strip()

    try:
        data = json.loads(candidate)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


SPANISH_NUMBER_MAP = {
    "cero": "0",
    "uno": "1",
    "una": "1",
    "dos": "2",
    "tres": "3",
    "cuatro": "4",
    "cinco": "5",
    "seis": "6",
    "siete": "7",
    "ocho": "8",
    "nueve": "9",
    "diez": "10",
}


def _normalize_account_text(value: str) -> str:
    words = value.lower().strip().split()
    digits: List[str] = []

    for w in words:
        w_clean = "".join(ch for ch in w if ch.isalnum())
        if not w_clean:
            continue
        if w_clean.isdigit():
            digits.append(w_clean)
        elif w_clean in SPANISH_NUMBER_MAP:
            digits.append(SPANISH_NUMBER_MAP[w_clean])

    if digits:
        return "".join(digits)

    return value.strip()

# file:///Users/misaelalvarezcamarillo/Desktop/misil.jpg


def _analyze_image(source: str) -> Dict[str, Any]:
    image_info = _encode_image_to_base64(source)
    prompt = (
        "Analiza el ticket y devuelve únicamente un JSON en este formato exacto:\n"
        "{\n"
        '  "monto": numero,\n'
        '  "destinatario": "string"\n'
        "}\n"
        "- \"monto\" debe ser un número (sin símbolo de moneda).\n"
        "- \"destinatario\" debe ser el número de cuenta o link de wallet/billetera"
        "- No escribas números con palabras; siempre usa dígitos.\n"
        "- Si no encuentras alguno de los datos, usa null.\n"
        "- No incluyas texto adicional fuera del JSON.\n"
        "- Si hay múltiples números, elige el que represente la cuenta/wallet."
    )

    client = get_client()
    if image_info["is_remote"]:
        image_payload = {
            "type": "input_image",
            "image_url": image_info["original"],
        }
    else:
        data_url = f"data:{image_info['mime']};base64,{image_info['data']}"
        image_payload = {
            "type": "input_image",
            "image_url": data_url,
        }
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    image_payload,
                ],
            }
        ],
    )

    parsed = _parse_json_text(response.output_text)
    monto = parsed.get("monto")
    destinatario = parsed.get("destinatario")

    try:
        if isinstance(monto, str):
            monto = float(monto.replace("$", "").replace(",", "").strip())
    except (ValueError, AttributeError):
        monto = None

    if isinstance(destinatario, str):
        destinatario = _normalize_account_text(destinatario) or None

    return {"monto": monto, "destinatario": destinatario}


def _load_system_prompt() -> Optional[str]:
    system_prompt_path = os.path.join(
        os.path.dirname(__file__),
        "agent",
        "system_prompt.md",
    )
    if os.path.exists(system_prompt_path):
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


async def _handle_whatsapp_message(
    wa_id: str,
    name: str,
    message: str,
    media: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    system_prompt = _load_system_prompt()

    user_message = message or ""
    audio_input = False
    image_input = False
    image_analysis: Optional[Dict[str, Any]] = None
    selected_media_type = None
    selected_media_url = None

    if media:
        for item in media:
            media_type = item.get("type", "").lower()
            media_url = item.get("source")
            if not media_url:
                continue
            if media_type in ("audio", "voice"):
                selected_media_type = "audio"
                selected_media_url = media_url
                break
            if media_type == "image":
                selected_media_type = "image"
                selected_media_url = media_url
                break

    if selected_media_type == "audio":
        audio_input = True
        user_message = _transcribe_audio(selected_media_url)
    elif selected_media_type == "image":
        image_input = True
        image_analysis = _analyze_image(selected_media_url)
        summary_parts = []
        monto = image_analysis.get("monto")
        destinatario = image_analysis.get("destinatario")
        if monto is not None:
            summary_parts.append(f"un monto aproximado de ${monto:,.2f}")
        if destinatario:
            summary_parts.append(
                f"una cuenta o wallet con número {destinatario}")
        summary = ", ".join(
            summary_parts) if summary_parts else "sin datos claros"
        user_message = (
            "El usuario envió un ticket de compra. "
            f"Se identificó {summary}. "
            "Confirma la transacción al usuario con un mensaje claro."
        )
    elif _is_audio_source(message):
        audio_input = True
        user_message = _transcribe_audio(message)
    elif _is_image_source(message):
        image_input = True
        image_analysis = _analyze_image(message)
        summary_parts = []
        monto = image_analysis.get("monto")
        destinatario = image_analysis.get("destinatario")
        if monto is not None:
            summary_parts.append(f"un monto aproximado de ${monto:,.2f}")
        if destinatario:
            summary_parts.append(
                f"una cuenta o wallet con número {destinatario}")
        summary = ", ".join(
            summary_parts) if summary_parts else "sin datos claros"
        user_message = (
            "El usuario envió un ticket de compra. "
            f"Se identificó {summary}. "
            "Confirma la transacción al usuario con un mensaje claro."
        )

    result = process_message_with_extraction(user_message, system_prompt)
    monto = result.get("monto")
    destinatario = result.get("destinatario")
    response_text = result.get("response", "")

    # Normalizar destinatario a dígitos si es posible
    if isinstance(destinatario, str):
        destinatario = _normalize_account_text(destinatario) or None

    # Ajustar la respuesta para asegurarnos de que incluya los datos numéricos
    additions = []
    if monto is not None and f"{monto}" not in response_text:
        additions.append(f"monto ${monto:,.2f}")
    if destinatario and destinatario not in response_text:
        additions.append(f"cuenta {destinatario}")
    if additions:
        response_text = response_text.rstrip(". ")
        response_text += ". " + \
            " ".join(f"Confirmo {item}." for item in additions)

    response_payload: Dict[str, Any] = {
        "monto": monto,
        "destinatario": destinatario,
        "response": response_text,
        "wa_id": wa_id,
        "name": name,
        "audio_url": None,
        "image_analysis": image_analysis,
        "payment_payload": None,
        "payment_status": None,
    }

    if audio_input and response_payload["response"]:
        response_payload["audio_url"] = _synthesize_audio_response(
            response_payload["response"])

    if monto is not None and destinatario:
        try:
            amount_major = float(monto)
            amount_value = str(
                int(round(amount_major * (10 ** DEFAULT_ASSET_SCALE))))
        except (ValueError, TypeError):
            amount_value = str(monto)
        payment_payload = {
            "senderWalletUrl": wa_id,
            "receiverWalletUrl": destinatario,
            "amount": amount_value,
            "assetCode": DEFAULT_ASSET_CODE,
            "assetScale": DEFAULT_ASSET_SCALE,
        }
        response_payload["payment_payload"] = payment_payload
        payment_result = await send_payment_async(payment_payload)
        response_payload["payment_status"] = payment_result

        confirmation = payment_result.get("service_response") if isinstance(
            payment_result, dict) else None
        if confirmation and isinstance(confirmation, dict):
            response_payload["payment_confirmation"] = confirmation

    return response_payload


@app.get("/")
async def root():
    """Endpoint de salud"""
    return {"status": "ok", "message": "WhatsApp LLM API is running"}


@app.get("/webhook/whatsapp")
async def verify_webhook(
    mode: Optional[str] = Query(None, alias="hub.mode"),
    token: Optional[str] = Query(None, alias="hub.verify_token"),
    challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """
    Endpoint para verificación de Webhook de WhatsApp (modo GET).
    WhatsApp enviará un challenge que debemos devolver si el token es válido.
    """
    if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook/whatsapp", response_model=LLMResponse)
async def receive_whatsapp_message(message: WhatsAppMessage):
    """
    Endpoint para recibir mensajes de WhatsApp y procesarlos con el LLM.

    Ejemplo de uso:
    {
        "wa_id": "5215513076942",
        "name": "Yorch Juárez",
        "message": "capital dem mexicox?",
        "identity_key_hash": null
    }
    """
    try:
        media_payload = None
        if message.media:
            media_payload = [item.dict() for item in message.media]

        response_payload = await _handle_whatsapp_message(
            wa_id=message.wa_id,
            name=message.name,
            message=message.message,
            media=media_payload,
        )
        return LLMResponse(**response_payload)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing message: {str(e)}")


@app.post("/webhook/whatsapp/raw")
async def receive_whatsapp_message_raw(message: dict):
    """
    Endpoint alternativo que acepta el formato raw del mensaje de WhatsApp.
    Útil si el mensaje viene en un formato diferente.
    """
    try:
        # Extraer información del mensaje
        wa_id = message.get("wa_id", "unknown")
        name = message.get("name", "Unknown User")
        message_text = message.get("message", "")

        if not message_text:
            raise HTTPException(
                status_code=400, detail="Message content is required")
        media_payload = message.get("media")
        response_payload = await _handle_whatsapp_message(
            wa_id=wa_id,
            name=name,
            message=message_text,
            media=media_payload,
        )

        return response_payload

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing message: {str(e)}")
