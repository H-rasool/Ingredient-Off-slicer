import re
from typing import List, Optional

_SPLIT_RX = re.compile(r",\s*(?![^()\[\]{}]*[\)\]\}])")
_HTML_RX = re.compile(r"<[^>]+>")

def smart_split(ingredients: str) -> List[str]:
    return [p.strip() for p in _SPLIT_RX.split(ingredients) if p.strip()]

def strip_tags(s: Optional[str]) -> Optional[str]:
    if s is None: return None
    return _HTML_RX.sub("", s)
