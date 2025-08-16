"""
فیلتر متن/لینک و ضد-فلاود ساده.
"""
import re
import time
from collections import defaultdict
from typing import Iterable

LINK_RE = re.compile(r"(https?://\S+|t\.me/\S+)", re.IGNORECASE)
_user_buckets = defaultdict(list)

def has_link(text: str) -> bool:
    return bool(LINK_RE.search(text or ""))

def contains_forbidden(text: str, words: Iterable[str]) -> str | None:
    t = (text or "").lower()
    for w in words:
        w = w.lower().strip()
        if not w:
            continue
        if re.search(rf"\b{re.escape(w)}\b", t):
            return w
    return None

def flood_hit(chat_id: int, user_id: int, threshold: int = 8, window_seconds: int = 10) -> bool:
    now = time.time()
    key = (chat_id, user_id)
    bucket = _user_buckets[key]
    cutoff = now - window_seconds
    while bucket and bucket[0] < cutoff:
        bucket.pop(0)
    bucket.append(now)
    return len(bucket) > threshold
