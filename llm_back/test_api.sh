#!/bin/bash

# Script para probar la API de WhatsApp LLM
# Asegúrate de que el servidor esté corriendo en otra terminal

echo "Probando endpoint /webhook/whatsapp..."
echo ""

curl -X POST "http://localhost:8000/webhook/whatsapp" \
  -H "Content-Type: application/json" \
  -d '{
    "wa_id": "5215513076942",
    "name": "Yorch Juárez",
    "message": "bro",
    "identity_key_hash": null
  }' \
  | python3 -m json.tool

echo ""
echo "Prueba completada!"

