from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .agent.main import process_message, process_message_with_extraction
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

app = FastAPI(title="WhatsApp LLM API", version="1.0.0")


class WhatsAppMessage(BaseModel):
    """Modelo para recibir mensajes de WhatsApp"""
    wa_id: str
    name: str
    message: str
    identity_key_hash: Optional[str] = None


class LLMResponse(BaseModel):
    """Modelo para la respuesta del LLM"""
    monto: Optional[float] = None
    destinatario: Optional[str] = None
    response: str
    wa_id: str
    name: str


@app.get("/")
async def root():
    """Endpoint de salud"""
    return {"status": "ok", "message": "WhatsApp LLM API is running"}


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
        # Procesar el mensaje con el LLM
        # Puedes cargar el system_prompt desde un archivo si es necesario
        system_prompt = None
        system_prompt_path = os.path.join(
            os.path.dirname(__file__), 
            "agent", 
            "system_prompt.md"
        )
        
        if os.path.exists(system_prompt_path):
            with open(system_prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
        
        # AQUÍ PUEDES MODIFICAR CÓMO SE CONSTRUYE EL MENSAJE PARA EL LLM
        user_message = message.message
        
        # Procesar el mensaje y extraer información estructurada
        result = process_message_with_extraction(user_message, system_prompt)
        
        # Extraer datos de la respuesta
        monto = result.get("monto")
        destinatario = result.get("destinatario")
        response_text = result.get("response", "")
        
        return LLMResponse(
            monto=monto,
            destinatario=destinatario,
            response=response_text,
            wa_id=message.wa_id,
            name=message.name
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


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
            raise HTTPException(status_code=400, detail="Message content is required")
        
        # Procesar con el LLM
        system_prompt = None
        system_prompt_path = os.path.join(
            os.path.dirname(__file__), 
            "agent", 
            "system_prompt.md"
        )
        
        if os.path.exists(system_prompt_path):
            with open(system_prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
        
        # Procesar el mensaje y extraer información estructurada
        user_message = message_text
        result = process_message_with_extraction(user_message, system_prompt)
        
        # Extraer datos de la respuesta
        monto = result.get("monto")
        destinatario = result.get("destinatario")
        response_text = result.get("response", "")
        
        return {
            "monto": monto,
            "destinatario": destinatario,
            "response": response_text,
            "wa_id": wa_id,
            "name": name
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

