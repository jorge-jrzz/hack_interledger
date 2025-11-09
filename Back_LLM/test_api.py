#!/usr/bin/env python3
"""
Script para probar la API de WhatsApp LLM
"""
import requests
import json

def test_whatsapp_endpoint():
    """Prueba el endpoint /webhook/whatsapp"""
    url = "http://localhost:8000/webhook/whatsapp"
    
    payload = {
        "wa_id": "5215513076942",
        "name": "Yorch Juárez",
        "message": "bro",
        "identity_key_hash": None
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Enviando mensaje a la API...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        print("✅ Respuesta exitosa:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor.")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e}")
        print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_endpoint():
    """Prueba el endpoint de salud"""
    url = "http://localhost:8000/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("✅ Servidor está corriendo:")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"❌ Servidor no está disponible: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Prueba de API WhatsApp LLM")
    print("=" * 50)
    print()
    
    # Primero verificar que el servidor esté corriendo
    if test_health_endpoint():
        print()
        test_whatsapp_endpoint()
    else:
        print("\nPor favor, ejecuta el servidor primero con: python main.py")

