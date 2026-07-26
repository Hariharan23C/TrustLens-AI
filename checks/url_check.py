"""
checks/url_check.py
Heuristic scoring for a submitted URL. No external API calls (keeps it
free and offline-friendly for a student project) -- everything is derived
from the URL string's own structure, which is where most phishing tells
actually live.
"""

import re
from urllib.parse import urlparse
from . import build_result

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
    "buff.ly", "cutt.ly", "rebrand.ly", "shorte.st", "rb.gy",
}

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "update", "account", "confirm",
    "signin", "webscr", "banking", "reset-password", "unlock",
    "suspended", "invoice", "gift", "free-", "bonus", "prize",
]

# Commonly-impersonated brands vs. lookalike patterns (very small illustrative set)
BRANDS = ["google", "microsoft", "paypal", "amazon", "apple", "instagram",
          "whatsapp", "facebook", "netflix", "linkedin", "flipkart"]

SUSPICIOUS_TLDS = {".xyz", ".top", ".club", ".zip", ".gq", ".tk", ".ml", ".work", ".click", ".loan"}


def _looks_like_ip(host):
    return bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host or ""))


def _brand_lookalike(host):
    """Catches 'paypa1-secure.com' style domains: a brand name present, but
    NOT as the actual registrable domain."""
    if not host:
        return None
    for brand in BRANDS:
        if brand in host and not re.search(rf"(^|\.){brand}\.[a-z]{{2,}}$", host):
            return brand
    return None


def check_url(raw_url):
    reasons = []
    score = 0

    raw_url = (raw_url or "").strip()
    if not raw_url:
        return build_result(0, ["No URL provided."])

    if not re.match(r"^https?://", raw_url, re.I):
        raw_url = "http://" + raw_url  # so urlparse behaves; we still flag missing scheme below

    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    full = raw_url.lower()

    if parsed.scheme == "http":
        score += 10
        reasons.append("Uses plain HTTP instead of HTTPS -- no encryption, easy to spoof.")

    if _looks_like_ip(host):
        score += 30
        reasons.append("Domain is a raw IP address rather than a registered domain name.")

    if host in SHORTENERS:
        score += 20
        reasons.append(f"'{host}' is a link shortener -- the real destination is hidden.")

    if "@" in raw_url:
        score += 25
        reasons.append("URL contains an '@' symbol, a classic trick to hide the real destination.")

    hyphen_count = host.count("-")
    if hyphen_count >= 3:
        score += 15
        reasons.append(f"Domain has {hyphen_count} hyphens, common in auto-generated phishing domains.")

    subdomain_count = max(0, host.count(".") - 1)
    if subdomain_count >= 3:
        score += 15
        reasons.append("Unusually deep subdomain chain, often used to disguise the true domain.")

    for tld in SUSPICIOUS_TLDS:
        if host.endswith(tld):
            score += 15
            reasons.append(f"Uses the '{tld}' top-level domain, frequently abused for cheap throwaway scam sites.")
            break

    matched_kw = [kw for kw in SUSPICIOUS_KEYWORDS if kw in full]
    if matched_kw:
        score += min(20, 5 * len(matched_kw))
        reasons.append(
            "Contains urgency/credential-harvesting keywords: " + ", ".join(matched_kw[:4])
        )

    brand = _brand_lookalike(host)
    if brand:
        score += 35
        reasons.append(
            f"Mentions '{brand}' in the domain but isn't the real {brand} domain -- classic brand impersonation."
        )

    if len(raw_url) > 90:
        score += 10
        reasons.append("Unusually long URL, often used to bury the real domain out of view.")

    return build_result(score, reasons)
