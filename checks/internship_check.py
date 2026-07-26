"""
checks/internship_check.py
Two related checkers for the internship/offer-letter scam pattern that
targets students specifically: fake internship postings, and fake offer
letters/PDFs (pasted as text). Both share most of their signal, so they
share a scoring core.
"""

import re
from . import build_result

PAYMENT_PATTERNS = [
    "registration fee", "processing fee", "security deposit", "refundable deposit",
    "pay to confirm", "pay before", "training fee", "kit fee", "activation fee",
    "one-time payment", "convenience fee",
]

CONTACT_RED_FLAGS = ["whatsapp only", "contact us on whatsapp", "telegram group", "dm to apply"]

UNREALISTIC_PHRASES = [
    "work 1 hour a day", "earn up to", "guaranteed placement", "no interview required",
    "selected without interview", "100% job guarantee", "easy money", "work from home and earn",
]

GENERIC_GREETING = ["dear candidate", "dear applicant", "dear student", "hi there,", "dear sir/madam"]

FREE_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com"}


def _shared_signals(text, company_email=""):
    reasons = []
    score = 0
    t = text.lower()

    payment_hits = [p for p in PAYMENT_PATTERNS if p in t]
    if payment_hits:
        score += 40
        reasons.append("Asks for money upfront (" + ", ".join(payment_hits[:2]) + ") -- legitimate employers never charge candidates to work.")

    if any(c in t for c in CONTACT_RED_FLAGS):
        score += 20
        reasons.append("Pushes communication to WhatsApp/Telegram instead of official company channels.")

    unreal_hits = [p for p in UNREALISTIC_PHRASES if p in t]
    if unreal_hits:
        score += 25
        reasons.append("Uses unrealistic promises: " + ", ".join(unreal_hits[:2]))

    if any(g in t for g in GENERIC_GREETING):
        score += 10
        reasons.append("Generic greeting ('Dear Candidate' etc.) instead of your actual name -- suggests a mass-sent template.")

    if re.search(r"\b(bank account|upi id|aadhaar|pan card|otp|cvv)\b", t):
        score += 30
        reasons.append("Requests sensitive personal/financial identifiers, which no legitimate offer process needs upfront.")

    if company_email.strip():
        domain = company_email.strip().lower().split("@")[-1]
        if domain in FREE_DOMAINS:
            score += 25
            reasons.append(f"Offer sent from a free email domain ({domain}) instead of the company's own domain.")

    if not re.search(r"\b(interview|assessment|test|screening|shortlist)\b", t):
        score += 10
        reasons.append("No mention of any interview, assessment, or screening step before the offer.")

    grammar_flags = len(re.findall(r"\s{2,}|[A-Z]{6,}|!{2,}", text))
    if grammar_flags >= 2:
        score += 8
        reasons.append("Formatting/grammar looks unpolished for an official company communication (odd spacing, ALL-CAPS, repeated punctuation).")

    return score, reasons


def check_internship_post(post_text, company_email=""):
    if not post_text.strip():
        return build_result(0, ["No internship posting text provided."])
    score, reasons = _shared_signals(post_text, company_email)
    return build_result(score, reasons)


def check_offer_letter(letter_text, company_email=""):
    if not letter_text.strip():
        return build_result(0, ["No offer letter text provided."])
    score, reasons = _shared_signals(letter_text, company_email)

    t = letter_text.lower()
    if not re.search(r"\b(ctc|stipend|salary|compensation)\b", t):
        score += 8
        reasons.append("No compensation/stipend details stated -- genuine offer letters always specify this.")
    if not re.search(r"\b(hr|human resources|signed|authorized signatory)\b", t):
        score += 8
        reasons.append("No HR contact or authorised signatory named.")

    return build_result(score, reasons)
