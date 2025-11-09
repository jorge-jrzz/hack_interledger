
from __future__ import annotations

import os
from typing import Dict, Any

import requests


PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")
DEFAULT_ASSET_CODE = os.getenv("PAYMENT_ASSET_CODE", "MX")
DEFAULT_ASSET_SCALE = int(os.getenv("PAYMENT_ASSET_SCALE", "2"))


def send_payment(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envía el pago al servicio remoto.

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
        response = requests.post(
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
    except requests.RequestException as exc:
        return {
            "status": "error",
            "payload": payload,
            "error": str(exc),
        }

