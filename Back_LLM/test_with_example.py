#!/usr/bin/env python3
"""
Prueba con el ejemplo exacto proporcionado
"""
import requests
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
project_root = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

from openai import OpenAI

# Inicializar cliente con API key del entorno
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY no está configurada en el entorno")

client = OpenAI(api_key=api_key)

def transcribe_audio(audio_file_path: str) -> str:
    """Transcribe un archivo de audio a texto"""
    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file,
            response_format="text",
            language="es"
        )
    return transcription


def is_audio_file(message: str) -> bool:
    """Verifica si el mensaje es una ruta a un archivo de audio"""
    # Extensiones de audio soportadas
    audio_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac']
    
    # Verificar si es una ruta de archivo
    if os.path.isfile(message):
        # Obtener la extensión del archivo
        _, ext = os.path.splitext(message.lower())
        return ext in audio_extensions
    
    return False



def text_to_speech(text: str, output_filename: str = "respuesta.mp3") -> str:
    """Convierte texto a audio y devuelve la ruta del archivo"""
    # Crear directorio de respuestas si no existe
    output_dir = Path(__file__).parent / "audio_responses"
    output_dir.mkdir(exist_ok=True)
    
    speech_file_path = output_dir / output_filename
    
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text
    )
    
    # Guardar el audio
    with open(speech_file_path, "wb") as audio_file:
        audio_file.write(response.content)
    
    # Devolver la ruta absoluta como URL local
    return str(speech_file_path.absolute())


def check_api_key():
    """Verifica si la API key de OpenAI está configurada"""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        # Mostrar solo los primeros y últimos caracteres por seguridad
        masked_key = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"
        print(f"✅ OPENAI_API_KEY configurada: {masked_key}")
        return True
    else:
        print("⚠️  ADVERTENCIA: OPENAI_API_KEY no está configurada")
        print("   El servidor no podrá procesar mensajes con el LLM")
        print("\n   Para configurarla, ejecuta en tu terminal:")
        print("   export OPENAI_API_KEY='tu-api-key-aqui'")
        print("\n   O agrégalo a tu archivo ~/.zshrc o ~/.bashrc:")
        print("   echo 'export OPENAI_API_KEY=\"tu-api-key-aqui\"' >> ~/.zshrc")
        print("   source ~/.zshrc")
        return False

def test_whatsapp_api():
    """Prueba el endpoint con el ejemplo exacto"""
    
    print("=" * 70)
    print("PRUEBA DEL ENDPOINT WHATSAPP CON EL EJEMPLO")
    print("=" * 70)
    print()
    
    # Verificar API key primero
    has_api_key = check_api_key()
    print()
    
    # El ejemplo exacto que proporcionaste
    # Puedes cambiar esto para probar con texto o audio
    original_message = "/Users/misaelalvarezcamarillo/Desktop/Back/Back_LLM/Record (online-voice-recorder.com).mp3"
    # Para probar con texto, descomenta la línea siguiente:
    # original_message = "Quiero enviar 50 pesos a la cuenta 123456789"
    
    payload = {
        "wa_id": "5215513076942",
        "name": "Yorch Juárez",
        "message": original_message,
    }
    
    # Verificar si es un archivo de audio
    is_audio_input = is_audio_file(original_message)
    transcribed_text = None
    
    if is_audio_input:
        print(f"🎤 Detectado archivo de audio: {original_message}")
        print("📝 Transcribiendo audio a texto...")
        try:
            transcribed_text = transcribe_audio(original_message)
            payload["message"] = transcribed_text
            print(f"✅ Transcripción: {transcribed_text}")
            print()
        except Exception as e:
            print(f"❌ Error al transcribir audio: {e}")
            return
    else:
        print(f"📝 Mensaje de texto detectado: {original_message}")
        print()


    url = "http://localhost:8000/webhook/whatsapp"
    headers = {"Content-Type": "application/json"}
    
    print("📤 Enviando mensaje:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("\n" + "-" * 70)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📥 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        print("\n📋 Contenido de la respuesta:")
        
        if response.status_code == 200:
            result = response.json()
            
            # Si la entrada era audio, generar audio de la respuesta
            if is_audio_input:
                response_text = result.get("response", "")
                if response_text:
                    print("🔊 Generando audio de la respuesta...")
                    try:
                        # Generar nombre único para el archivo de audio
                        import time
                        timestamp = int(time.time())
                        audio_filename = f"respuesta_{timestamp}.mp3"
                        audio_file_path = text_to_speech(response_text, audio_filename)
                        
                        # Agregar la URL del audio a la respuesta
                        result["audio_url"] = f"file://{audio_file_path}"
                        result["audio_file"] = audio_file_path
                        
                        print(f"✅ Audio generado: {audio_file_path}")
                        print()
                    except Exception as e:
                        print(f"⚠️  Error al generar audio: {e}")
                        print("   Se devuelve solo la respuesta en texto")
            
            # Mostrar la respuesta completa
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("\n✅ ¡Prueba exitosa!")
            
            if is_audio_input:
                print(f"🎵 URL del audio: {result.get('audio_file', 'No generado')}")
            
            if has_api_key:
                print("✅ El LLM procesó el mensaje correctamente")
            else:
                print("⚠️  Nota: El mensaje se envió pero el LLM no pudo procesarlo")
                print("   Configura OPENAI_API_KEY para obtener respuestas del LLM")
        else:
            error_detail = response.text
            print(error_detail)
            print(f"\n❌ Error: Status {response.status_code}")
            
            # Mensaje específico si falta la API key
            if "OPENAI_API_KEY" in error_detail:
                print("\n💡 Solución: Configura la API key con:")
                print("   export OPENAI_API_KEY='tu-api-key'")
                print("   Luego reinicia el servidor")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("\n   Asegúrate de que el servidor esté corriendo en otra terminal:")
        print("   cd /Users/misaelalvarezcamarillo/Desktop/Back/Back_LLM")
        print("   python main.py")
        print("\n   El servidor debe estar corriendo en http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 70)

if __name__ == "__main__":
    test_whatsapp_api()

