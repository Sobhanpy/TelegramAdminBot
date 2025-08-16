"""
نرخ ارز با exchangerate.host (بدون کلید).
"""
from __future__ import annotations
import httpx

async def fx_rate(base: str = "USD", symbols: str = "EUR,IRR"):
    url = "https://api.exchangerate.host/latest"
    params = {"base": base.upper(), "symbols": symbols.upper()}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()
