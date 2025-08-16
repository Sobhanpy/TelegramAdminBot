"""
هواشناسی نمونه با Open-Meteo (بدون کلید).
"""
from __future__ import annotations
import httpx

async def get_weather(lat: float, lon: float) -> str:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": True}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    cw = data.get("current_weather", {})
    temp = cw.get("temperature")
    wind = cw.get("windspeed")
    return f"دمای فعلی: {temp}°C | سرعت باد: {wind} km/h"
