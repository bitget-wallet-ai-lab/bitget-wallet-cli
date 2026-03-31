"""Bitget Wallet API client with BKHmacAuth signing."""
from __future__ import annotations

import hashlib
import json
import os
import time

import requests

BASE_URL = "https://copenapi.bgwapi.io"
WALLET_ID = os.environ.get("BGW_WALLET_ID", "")


def _make_sign(method: str, path: str, body_str: str, ts: str) -> str:
    """BKHmacAuth signature: SHA256(Method + Path + Body + Timestamp)."""
    message = method + path + body_str + ts
    digest = hashlib.sha256(message.encode("utf-8")).hexdigest()
    return "0x" + digest


def request(path: str, body: dict | None = None) -> dict:
    """POST request with BKHmacAuth signing."""
    ts = str(int(time.time() * 1000))
    body_str = json.dumps(body, separators=(",", ":"), ensure_ascii=False) if body else ""
    sign = _make_sign("POST", path, body_str, ts)
    token_val = WALLET_ID if WALLET_ID else "toc_agent"
    headers = {
        "Content-Type": "application/json",
        "channel": "toc_agent",
        "brand": "toc_agent",
        "clientversion": "10.0.0",
        "language": "en",
        "token": token_val,
        "X-SIGN": sign,
        "X-TIMESTAMP": ts,
    }
    resp = requests.post(BASE_URL + path, data=body_str or None, headers=headers, timeout=30)
    if resp.status_code != 200:
        return {"status": -1, "error_code": resp.status_code, "msg": resp.text[:500]}
    return resp.json()


def request_get(path_with_query: str) -> dict:
    """GET request with BKHmacAuth signing."""
    ts = str(int(time.time() * 1000))
    sign = _make_sign("GET", path_with_query, "", ts)
    token_val = WALLET_ID if WALLET_ID else "toc_agent"
    headers = {
        "channel": "toc_agent",
        "brand": "toc_agent",
        "clientversion": "10.0.0",
        "language": "en",
        "token": token_val,
        "X-SIGN": sign,
        "X-TIMESTAMP": ts,
    }
    resp = requests.get(BASE_URL + path_with_query, headers=headers, timeout=30)
    if resp.status_code != 200:
        return {"status": -1, "error_code": resp.status_code, "msg": resp.text[:500]}
    return resp.json()
