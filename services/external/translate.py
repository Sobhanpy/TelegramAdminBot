
"""
ترجمه‌ی نمونه با MyMemory (رایگان و محدود).
"""
from __future__ import annotations
import httpx

async def translate(text: str, target_lang: str = "en") -> str:
    if not text.strip():
        return "متنی برای ترجمه ارسال نشده."
    url = "https://api.mymemory.translated.net/get"
    params = {"q": text, "langpair": f"auto|{target_lang}"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    return data.get("responseData", {}).get("translatedText", "No translation")
