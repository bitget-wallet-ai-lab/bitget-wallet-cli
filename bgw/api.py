"""Bitget Wallet ToB API client with built-in signing."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time

import requests

BASE_URL = "https://bopenapi.bgwapi.io"

# Public demo credentials for testing. Override via env vars for production.
# Test credentials have 2 QPS limit — do not use in production.
API_KEY = os.environ.get("BGW_API_KEY", "6AE25C9BFEEC4D815097ECD54DDE36B9A1F2B069")
API_SECRET = os.environ.get("BGW_API_SECRET", "C2638D162310C10D5DAFC8013871F2868E065040")
PARTNER_CODE = os.environ.get("BGW_PARTNER_CODE", "bgw_swap_public")


def _sign(api_path: str, body_str: str, timestamp: str) -> str:
    """HMAC-SHA256 signature per Bitget Wallet ToB API spec."""
    content = {
        "apiPath": api_path,
        "body": body_str,
        "x-api-key": API_KEY,
        "x-api-timestamp": timestamp,
    }
    payload = json.dumps(dict(sorted(content.items())), separators=(",", ":"))
    sig = hmac.new(API_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.b64encode(sig).decode()


def request(path: str, body: dict | None = None) -> dict:
    """Authenticated POST to Bitget Wallet ToB API.

    Authentication differs by endpoint type:
    - Market Data / Token endpoints: HMAC signature (x-api-key + x-api-signature)
    - Swap endpoints (/swapx/): Partner-Code header only (no HMAC needed)
    """
    timestamp = str(int(time.time() * 1000))
    body_str = json.dumps(body, separators=(",", ":"), sort_keys=True) if body else ""

    headers = {"Content-Type": "application/json"}

    if "/swapx/" in path:
        # Swap endpoints use Partner-Code only
        headers["Partner-Code"] = PARTNER_CODE
    else:
        # Market/Token endpoints use HMAC signature
        signature = _sign(path, body_str, timestamp)
        headers["x-api-key"] = API_KEY
        headers["x-api-timestamp"] = timestamp
        headers["x-api-signature"] = signature

    resp = requests.post(BASE_URL + path, data=body_str or None, headers=headers, timeout=30)
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "message": resp.text[:500]}
    return resp.json()
