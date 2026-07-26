"""
checks/email_check.py
Scores a sender email address (optionally with the claimed
organisation name and/or email body) for spoofing red flags.
"""

import re
from . import build_result

FREE_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com",
    "icloud.com", "protonmail.com", "aol.com", "yandex.com", "zoho.com",
}

URGENCY_WORDS = [
    "urgent", "immediately", "act now", "limited time", "verify your account",
    "suspended", "act fast", "final notice", "expire", "click here",
]

DISPOSABLE_HINTS = ["temp-mail", "guerrillamail", "mailinator", "10minutemail", "yopmail"]


def _domain_of(email):
    m = re.search(r"@([\w.-]+)$", email.strip().lower())
    return m.group(1) if m else ""


def check_email(email, claimed_org="", body_text=""):
    reasons = []
    score = 0
    email = (email or "").strip()

    if not email or "@" not in email:
        return build_result(0, ["No valid email address provided."])

    domain = _domain_of(email)
    local_part = email.split("@")[0].lower()

    if any(hint in domain for hint in DISPOSABLE_HINTS):
        score += 40
        reasons.append(f"'{domain}' is a disposable/temporary email service.")

    if domain in FREE_DOMAINS and claimed_org.strip():
        score += 30
        reasons.append(
            f"Claims to be from '{claimed_org.strip()}' but sends from a free personal "
            f"email domain ({domain}) instead of an official company domain."
        )

    # local part stuffed with digits (common in spoofed/burner accounts) e.g. hr.dept8827
    digit_ratio = sum(c.isdigit() for c in local_part) / max(1, len(local_part))
    if digit_ratio > 0.3 and len(local_part) > 4:
        score += 10
        reasons.append("Sender's username is unusually digit-heavy, common in mass-generated accounts.")

    if claimed_org.strip():
        org_slug = re.sub(r"[^a-z0-9]", "", claimed_org.lower())
        domain_slug = re.sub(r"[^a-z0-9]", "", domain.split(".")[0])
        if org_slug and org_slug not in domain_slug and domain_slug not in org_slug and domain not in FREE_DOMAINS:
            score += 20
            reasons.append(
                f"Domain '{domain}' doesn't match the claimed organisation '{claimed_org.strip()}'."
            )

    if body_text.strip():
        text = body_text.lower()
        hits = [w for w in URGENCY_WORDS if w in text]
        if hits:
            score += min(25, 8 * len(hits))
            reasons.append("Message body uses pressure/urgency language: " + ", ".join(hits[:4]))

        if re.search(r"\b(otp|password|cvv|pin|bank account|upi id|aadhaar|card number)\b", text):
            score += 30
            reasons.append("Asks for sensitive credentials (OTP, password, bank/card details) -- legitimate senders never do this by email.")

    return build_result(score, reasons)
