import regex as re

# Patterns
DOMAIN = r"(?:(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})"
URL = r"https?://[^\s)]+"
IPV4 = r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?!$)|$)){4}\b"
EMAIL = r"[A-Za-z0-9._%+-]+@" + DOMAIN
PHONE = r"\+?\d[\d\s().-]{7,}\d"

GA = r"\bUA-\d{4,}-\d+\b"
ADSENSE = r"\bpub-\d{16}\b"

SOCIAL = {
    "twitter": r"(?:https?://)?(?:www\.)?twitter\.com/([A-Za-z0-9_]{1,15})",
    "facebook": r"(?:https?://)?(?:www\.)?facebook\.com/([A-Za-z0-9_.-]+)",
    "instagram": r"(?:https?://)?(?:www\.)?instagram\.com/([A-Za-z0-9_.-]+)",
    "youtube": r"(?:https?://)?(?:www\.)?youtube\.com/(?:c/|channel/|@)?([A-Zaz0-9_.-]+)",
    "linkedin": r"(?:https?://)?(?:[\w.]*linkedin\.com)/in/([A-Za-z0-9_.-]+)",
    "tiktok": r"(?:https?://)?(?:www\.)?tiktok\.com/@([A-Za-z0-9_.-]+)",
    "telegram": r"(?:https?://)?t\.me/([A-Za-z0-9_]+)",
    "reddit": r"(?:https?://)?(?:www\.)?reddit\.com/(?:u|user)/([A-Za-z0-9_-]+)",
    "vk": r"(?:https?://)?vk\.com/([A-Za-z0-9_.-]+)",
    "truthsocial": r"(?:https?://)?truthsocial\.com/@([A-Za-z0-9_.-]+)",
}

PATTERNS = [
    ("url", URL),
    ("ipv4", IPV4),
    ("email", EMAIL),
    ("domain", DOMAIN),
    ("phone", PHONE),
    ("ga", GA),
    ("adsense", ADSENSE),
    ] + [(f"social:{k}", v) for k, v in SOCIAL.items()]

NORMALIZERS = {
"domain": lambda x: x.lower().strip("().,;\n \t"),
"url": lambda x: x.strip("()\n \t"),
"ipv4": lambda x: x,
"email": lambda x: x.lower(),
"phone": lambda x: re.sub(r"[^+\d]", "", x),
"ga": lambda x: x,
"adsense": lambda x: x,
}

for k in SOCIAL.keys():
    NORMALIZERS[f"social:{k}"] = lambda x, _k=k: x.lstrip("@").lower()
    
def extract_indicators(text: str) -> list[dict]:
    found: list[dict] = []
    for typ, pat in PATTERNS:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            raw = m.group(0)
            norm = NORMALIZERS.get(typ, lambda x: x)(raw)
            found.append({"type": typ, "value": norm, "confidence": 0.9})
    # deduplicate by (type, value)
    key = {(x['type'], x['value']): x for x in found}
    return list(key.values())