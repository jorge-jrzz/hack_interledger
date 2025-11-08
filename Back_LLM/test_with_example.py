#!/usr/bin/env python3
"""
Prueba con el ejemplo exacto proporcionado
"""
import requests
import json
import os
import sys

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
    payload = {
        "wa_id": "5215513076942",
        "name": "Yorch Juárez",
        "message": "Hola quiero que le pagues 50 pesos a esta cuenta 123456789",
    }
    
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
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("\n✅ ¡Prueba exitosa!")
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

