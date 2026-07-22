import re
from email_validator import validate_email

class EmailChecker:
    def check(self, email):
        result = "Safe"
        confidence = 0.0
        reasons = []
        
        try:
            validate_email(email)
            domain = email.split('@')[1].lower()
            
            temp_domains = ['tempmail', '10minutemail', 'guerrillamail', 'mailinator']
            if any(d in domain for d in temp_domains):
                reasons.append("Temporary email domain")
                confidence += 0.3
            
            suspicious = ['admin', 'support', 'info', 'noreply']
            local = email.split('@')[0].lower()
            if any(s in local for s in suspicious):
                reasons.append("Generic local part")
                confidence += 0.05
            
            if confidence >= 0.4:
                result = "Suspicious"
            if confidence >= 0.6:
                result = "Scam"
            
            explanation = " | ".join(reasons) if reasons else "Email appears legitimate"
        except:
            result = "Scam"
            confidence = 0.8
            explanation = "Invalid email format"
        
        return result, explanation, min(confidence * 100, 95)
