import re

class ScamDetector:
    def check(self, message):
        result = "Safe"
        confidence = 0.0
        reasons = []
        
        keywords = ['free', 'win', 'prize', 'urgent', 'bank', 'account', 'password', 'ssn']
        for word in keywords:
            if word in message.lower():
                reasons.append(f"Keyword: {word}")
                confidence += 0.05
        
        urgency = [r'\b(act now|hurry|limited offer)\b', r'\b(final warning|last chance)\b']
        for pattern in urgency:
            if re.search(pattern, message.lower()):
                reasons.append("Urgency language")
                confidence += 0.15
        
        if 'http' in message:
            reasons.append("Contains URL")
            confidence += 0.1
        
        if confidence >= 0.4:
            result = "Suspicious"
        if confidence >= 0.6:
            result = "Scam"
        
        explanation = " | ".join(reasons) if reasons else "Message seems legitimate"
        return result, explanation, min(confidence * 100, 95)
