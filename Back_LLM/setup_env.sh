#!/bin/bash
# Script para configurar la API key de OpenAI

echo "=========================================="
echo "Configuración de OPENAI_API_KEY"
echo "=========================================="
echo ""

# Verificar si ya está configurada
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OPENAI_API_KEY ya está configurada en esta terminal"
    echo "   Prefijo: ${OPENAI_API_KEY:0:7}...${OPENAI_API_KEY: -4}"
    echo ""
    echo "Para verificar que funciona, ejecuta:"
    echo "  python check_api_key.py"
else
    echo "❌ OPENAI_API_KEY no está configurada"
    echo ""
    echo "Por favor, proporciona tu API key de OpenAI:"
    echo "(O presiona Ctrl+C para cancelar)"
    echo ""
    read -p "Ingresa tu OPENAI_API_KEY: " api_key
    
    if [ -n "$api_key" ]; then
        export OPENAI_API_KEY="$api_key"
        echo ""
        echo "✅ API key exportada para esta sesión"
        echo ""
        echo "Para hacerla permanente, ejecuta:"
        echo "  echo 'export OPENAI_API_KEY=\"$api_key\"' >> ~/.zshrc"
        echo "  source ~/.zshrc"
        echo ""
        echo "Ahora puedes ejecutar el servidor con:"
        echo "  python main.py"
    else
        echo "❌ No se proporcionó ninguna API key"
    fi
fi

