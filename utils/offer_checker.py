import re

class OfferChecker:
    def check(self, content):
        result = "Safe"
        confidence = 0.0
        reasons = []
        
        patterns = [
            (r'\b(pay|fee).{0,20}(before joining)\b', "Payment requested before joining"),
            (r'\b(sign).{0,20}(immediately)\b', "Pressuring to sign"),
            (r'\b(confidential).{0,20}(offer)\b', "Overly confidential")
        ]
        
        for pattern, reason in patterns:
            if re.search(pattern, content.lower()):
                reasons.append(reason)
                confidence += 0.1
        
        if not re.search(r'\b(company|position|salary)\b', content.lower()):
            reasons.append("Missing standard elements")
            confidence += 0.15
        
        if confidence >= 0.5:
            result = "Suspicious"
        if confidence >= 0.7:
            result = "Scam"
        
        explanation = " | ".join(reasons) if reasons else "Offer seems legitimate"
        return result, explanation, min(confidence * 100, 95)
