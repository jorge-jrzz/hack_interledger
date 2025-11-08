#!/usr/bin/env python3
"""
Prueba directa del LLM con el ejemplo específico
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apps.Interledger_LLM.api.agent.main import process_message

def test_llm_direct():
    """Prueba directa del LLM con el mensaje de ejemplo"""
    
    # El ejemplo exacto que proporcionaste
    test_message = "bro"
    wa_id = "5215513076942"
    name = "Yorch Juárez"
    
    print("=" * 60)
    print("PRUEBA DIRECTA DEL LLM")
    print("=" * 60)
    print(f"\nMensaje recibido:")
    print(f"  wa_id: {wa_id}")
    print(f"  name: {name}")
    print(f"  message: '{test_message}'")
    print(f"  identity_key_hash: None")
    print("\n" + "-" * 60)
    print("Procesando con LLM...")
    print("-" * 60 + "\n")
    
    try:
        # Procesar el mensaje directamente con el LLM
        response = process_message(test_message)
        
        print("✅ Respuesta del LLM:")
        print(f"\n{response}\n")
        print("=" * 60)
        print("\nRespuesta completa:")
        print(f"  wa_id: {wa_id}")
        print(f"  name: {name}")
        print(f"  response: {response}")
        print("=" * 60)
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_llm_direct()

