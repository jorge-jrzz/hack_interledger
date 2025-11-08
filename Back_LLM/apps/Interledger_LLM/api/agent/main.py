from openai import OpenAI
from typing import Optional
import os
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