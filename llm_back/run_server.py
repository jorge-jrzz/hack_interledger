#!/usr/bin/env python3
"""
Script para ejecutar el servidor FastAPI
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "apps.Interledger_LLM.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

