"""
checks/message_check.py
Scores freeform text (SMS / WhatsApp / DM screenshots typed in) for scam
patterns. Also reused by the QR flow: whatever text a QR code decodes to
gets run through here (and through url_check if it's a bare link).
"""

import re
from . import build_result

LOTTERY_WORDS = ["you have won", "congratulations you", "lucky draw", "lottery", "claim your prize", "selected winner"]
URGENCY_WORDS = ["urgent", "act now", "immediately", "expires today", "last chance", "within 24 hours", "final warning"]
CREDENTIAL_WORDS = ["otp", "cvv", "pin number", "password", "upi pin", "net banking", "verify your account", "kyc update", "aadhaar"]
MONEY_REQUEST = ["send money", "gift card", "wire transfer", "bitcoin", "crypto payment", "processing fee", "pay a fee", "google pay", "paytm to"]
IMPERSONATION = ["income tax department", "customs department", "courier is held", "your parcel is on hold", "bank security team", "electricity board"]


def check_message(text):
    reasons = []
    score = 0
    text = (text or "").strip()

    if not text:
        return build_result(0, ["No message text provided."])

    t = text.lower()

    lottery_hits = [w for w in LOTTERY_WORDS if w in t]
    if lottery_hits:
        score += 35
        reasons.append("Claims you've won a prize/lottery you never entered.")

    urgency_hits = [w for w in URGENCY_WORDS if w in t]
    if urgency_hits:
        score += 20
        reasons.append("Creates artificial urgency to rush you into acting: " + ", ".join(urgency_hits[:3]))

    cred_hits = [w for w in CREDENTIAL_WORDS if w in t]
    if cred_hits:
        score += 35
        reasons.append("Asks for OTP/PIN/password or account verification -- no bank or service does this over SMS/chat.")

    money_hits = [w for w in MONEY_REQUEST if w in t]
    if money_hits:
        score += 30
        reasons.append("Requests payment via untraceable methods: " + ", ".join(money_hits[:3]))

    imp_hits = [w for w in IMPERSONATION if w in t]
    if imp_hits:
        score += 20
        reasons.append("Impersonates an authority/delivery service to sound official: " + ", ".join(imp_hits[:2]))

    if re.search(r"https?://\S+|www\.\S+", t):
        score += 10
        reasons.append("Contains a link -- verify it separately with the URL checker before clicking.")

    if re.search(r"\b(dear customer|dear user|valued customer)\b", t):
        score += 8
        reasons.append("Generic greeting instead of your name, typical of mass-blasted scam texts.")

    return build_result(score, reasons)
