#!/bin/bash
# Script para iniciar el servidor con verificación de API key

echo "=========================================="
echo "Iniciando servidor FastAPI"
echo "=========================================="
echo ""

# Verificar si la API key está configurada
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  ADVERTENCIA: OPENAI_API_KEY no está configurada"
    echo ""
    echo "Por favor, exporta la variable primero:"
    echo "  export OPENAI_API_KEY=\"tu-api-key-aqui\""
    echo ""
    echo "O ejecuta el script de configuración:"
    echo "  source setup_env.sh"
    echo ""
    exit 1
fi

echo "✅ OPENAI_API_KEY configurada"
echo "   Prefijo: ${OPENAI_API_KEY:0:7}...${OPENAI_API_KEY: -4}"
echo ""
echo "🚀 Iniciando servidor..."
echo "   URL: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

# Ejecutar el servidor
python main.py

