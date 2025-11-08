#!/bin/bash
# Script simple para iniciar el servidor

echo "🚀 Iniciando servidor FastAPI..."
echo ""
echo "URL: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

cd "$(dirname "$0")"
python main.py

