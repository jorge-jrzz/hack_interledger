
from __future__ import annotations

import os
from typing import Dict, Any

import httpx
import asyncio

PAYMENT_SERVICE_URL = "http://open_payments_api:3000/send-payment"
DEFAULT_ASSET_CODE = os.getenv("PAYMENT_ASSET_CODE", "MX")
DEFAULT_ASSET_SCALE = int(os.getenv("PAYMENT_ASSET_SCALE", "2"))


async def send_payment_async(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envía el pago al servicio remoto de forma asíncrona.

    Args:
        payload: Diccionario con las llaves esperadas por el servicio:
            senderWalletUrl, receiverWalletUrl, amount, assetCode, assetScale

    Returns:
        Diccionario con resultado y detalles
    """
    if not PAYMENT_SERVICE_URL:
        return {
            "status": "skipped",
            "reason": "PAYMENT_SERVICE_URL no está configurada",
            "payload": payload,
        }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                PAYMENT_SERVICE_URL,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            try:
                data = response.json()
            except ValueError:
                data = response.text

            return {
                "status": "success",
                "payload": payload,
                "service_response": data,
            }
    except httpx.RequestError as exc:
        return {
            "status": "error",
            "payload": payload,
            "error": str(exc),
        }

# Alias para mantener compatibilidad si la función es llamada de manera síncrona


def send_payment(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper síncrono para send_payment_async para retrocompatibilidad.
    """
    return asyncio.run(send_payment_async(payload))
