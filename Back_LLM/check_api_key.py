
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
project_root = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

def check_api_key():
    """Verifica si la API key está disponible"""
    print("=" * 70)
    print("VERIFICACIÓN DE OPENAI_API_KEY")
    print("=" * 70)
    print()
    
    # Verificar si existe archivo .env
    if os.path.exists(env_path):
        print(f"✅ Archivo .env encontrado en: {env_path}")
    else:
        print(f"ℹ️  Archivo .env no encontrado en: {env_path}")
        print("   (Está bien si usas variable de entorno directamente)")
    print()
    
    # Verificar en el entorno actual (puede venir de .env o variable de entorno)
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        # Mostrar información parcial por seguridad
        masked = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"
        print(f"✅ OPENAI_API_KEY encontrada")
        print(f"   Longitud: {len(api_key)} caracteres")
        print(f"   Prefijo: {masked}")
        print(f"   Inicia con: {api_key[:3]}...")
        print()
        print("✅ La variable de entorno está configurada correctamente")
        return True
    else:
        print("❌ OPENAI_API_KEY NO encontrada")
        print()
        print("📝 Para configurarla, tienes 3 opciones:")
        print()
        print("   Opción 1: Crear archivo .env (RECOMENDADO)")
        print(f"      Crea un archivo .env en: {project_root}")
        print("      Con el contenido: OPENAI_API_KEY=sk-proj-tu-api-key-aqui")
        print()
        print("   Opción 2: Variable de entorno en la terminal:")
        print("      export OPENAI_API_KEY=\"tu-api-key-aqui\"")
        print()
        print("   Opción 3: Permanente en ~/.zshrc:")
        print("      echo 'export OPENAI_API_KEY=\"tu-api-key-aqui\"' >> ~/.zshrc")
        print("      source ~/.zshrc")
        return False

def test_import():
    """Prueba si el módulo puede leer la API key"""
    print("-" * 70)
    print("PRUEBA DE IMPORTACIÓN DEL MÓDULO")
    print("-" * 70)
    print()
    
    try:
        from apps.Interledger_LLM.api.agent.main import get_client
        print("✅ Módulo importado correctamente")
        
        try:
            client = get_client()
            print("✅ Cliente de OpenAI creado correctamente")
            print("✅ La API key se está leyendo correctamente desde el código")
            return True
        except ValueError as e:
            print(f"❌ Error al crear cliente: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error al importar módulo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    has_key = check_api_key()
    print()
    
    if has_key:
        test_import()
    
    print()
    print("=" * 70)

