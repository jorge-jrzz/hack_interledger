import uvicorn
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env si existe
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

if __name__ == "__main__":
    uvicorn.run(
        "apps.Interledger_LLM.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )