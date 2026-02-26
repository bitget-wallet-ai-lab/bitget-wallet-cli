"""Bitget Wallet ToB API client with built-in signing."""

import base64
import hashlib
import hmac
import json
import os
import time

import requests

BASE_URL = "https://bopenapi.bgwapi.io"

# Public demo credentials for testing. These may change over time —
# if they stop working, please update to get the latest keys.
# Public demo credentials for testing purposes. These may change over time —
# if they stop working, please update to get the latest keys.
# Override via BGW_API_KEY / BGW_API_SECRET env vars.
API_KEY = os.environ.get("BGW_API_KEY", "4843D8C3F1E20772C0E634EDACC5C5F9A0E2DC92")
API_SECRET = os.environ.get("BGW_API_SECRET", "F2ABFDC684BDC6775FD6286B8D06A3AAD30FD587")
PARTNER_CODE = os.environ.get("BGW_PARTNER_CODE", "bgw_swap_public")


def _sign(api_path: str, body_str: str, timestamp: str) -> str:
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
    timestamp = str(int(time.time() * 1000))
    body_str = json.dumps(body, separators=(",", ":"), sort_keys=True) if body else ""
    signature = _sign(path, body_str, timestamp)

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "x-api-timestamp": timestamp,
        "x-api-signature": signature,
    }
    if "/swapx/" in path:
        headers["Partner-Code"] = PARTNER_CODE

    resp = requests.post(BASE_URL + path, data=body_str or None, headers=headers, timeout=30)
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "message": resp.text[:500]}
    return resp.json()
