from openai import OpenAI
from typing import Optional, Dict, Any
import os
import json
import re
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
# Buscar .env en el directorio raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

_client = None
_cached_api_key = None

def get_client():
    """Obtiene el cliente de OpenAI, inicializándolo si es necesario"""
    global _client, _cached_api_key
    
    # Obtener la API key actual del entorno (puede venir de .env o variable de entorno)
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY no está configurada. "
            "Por favor, configura la variable de entorno OPENAI_API_KEY"
        )
    
    # Si el cliente no existe o la API key cambió, crear uno nuevo
    if _client is None or _cached_api_key != api_key:
        _client = OpenAI(api_key=api_key)
        _cached_api_key = api_key
    
    return _client


def process_message(message: str, system_prompt: Optional[str] = None) -> str:
    """
    Procesa un mensaje usando el LLM de OpenAI.
    
    Args:
        message: El mensaje del usuario a procesar
        system_prompt: Prompt del sistema opcional
    
    Returns:
        La respuesta del LLM
    """
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": message})
    
    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Usando un modelo disponible
        messages=messages
    )
    
    return response.choices[0].message.content


def process_message_with_extraction(message: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Procesa un mensaje usando el LLM y extrae información estructurada (monto y destinatario).
    
    Args:
        message: El mensaje del usuario a procesar
        system_prompt: Prompt del sistema opcional
    
    Returns:
        Diccionario con: monto, destinatario, response
    """
    # Preparar el system prompt con instrucciones para extracción
    extraction_prompt = """Eres un asistente que extrae información de transacciones de mensajes de WhatsApp.

Tu tarea es:
1. Extraer el MONTO (número, puede tener $, pesos, etc.)
2. Extraer el DESTINATARIO (número de cuenta, teléfono, o identificador)
3. Generar una respuesta amigable confirmando la transacción

IMPORTANTE: Debes responder SOLO con un JSON válido en este formato exacto:
{
  "monto": <número sin comillas>,
  "destinatario": "<string>",
  "response": "<tu respuesta al usuario>"
}

Si no encuentras monto o destinatario, usa null para esos campos.
"""
    
    if system_prompt:
        extraction_prompt = system_prompt + "\n\n" + extraction_prompt
    
    messages = [
        {"role": "system", "content": extraction_prompt},
        {"role": "user", "content": message}
    ]
    
    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_object"},  # Forzar formato JSON
        temperature=0.3  # Menos creatividad para extracción más precisa
    )
    
    # Obtener la respuesta
    response_content = response.choices[0].message.content
    
    # Intentar parsear el JSON
    try:
        result = json.loads(response_content)
        
        # Validar y limpiar los datos
        monto = result.get("monto")
        if monto is not None:
            # Convertir a float si es string o número
            try:
                # Si es string, limpiar símbolos de moneda
                if isinstance(monto, str):
                    monto = re.sub(r'[^\d.]', '', monto)
                monto = float(monto) if monto else None
            except (ValueError, TypeError):
                monto = None
        
        destinatario = result.get("destinatario")
        if destinatario is not None and destinatario.strip() == "":
            destinatario = None
        
        response_text = result.get("response", "")
        if not response_text:
            response_text = "Procesando tu solicitud..."
        
        return {
            "monto": monto,
            "destinatario": destinatario,
            "response": response_text
        }
    
    except json.JSONDecodeError:
        # Si falla el parseo JSON, intentar extraer manualmente
        # Esto es un fallback en caso de que el LLM no devuelva JSON válido
        monto = None
        destinatario = None
        
        # Intentar extraer monto con regex
        monto_match = re.search(r'\$?\s*(\d+(?:\.\d+)?)', message)
        if monto_match:
            try:
                monto = float(monto_match.group(1))
            except ValueError:
                pass
        
        # Intentar extraer destinatario (números de cuenta/teléfono)
        destinatario_match = re.search(r'(\d{8,})', message)
        if destinatario_match:
            destinatario = destinatario_match.group(1)
        
        return {
            "monto": monto,
            "destinatario": destinatario,
            "response": response_content if response_content else "Procesando tu solicitud..."
        }