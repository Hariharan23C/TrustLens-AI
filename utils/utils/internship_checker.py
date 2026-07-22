import re

class InternshipChecker:
    def check(self, content):
        result = "Safe"
        confidence = 0.0
        reasons = []
        
        scams = [
            (r'\b(urgent|immediate)\b', "Urgency language"),
            (r'\b(pay|fee|deposit).{0,20}(before|upfront)\b', "Asks for payment"),
            (r'\b(no experience).{0,20}(high salary)\b', "Too good to be true")
        ]
        
        for pattern, reason in scams:
            if re.search(pattern, content.lower()):
                reasons.append(reason)
                confidence += 0.1
        
        if confidence >= 0.5:
            result = "Suspicious"
        if confidence >= 0.7:
            result = "Scam"
        
        explanation = " | ".join(reasons) if reasons else "Internship seems legitimate"
        return result, explanation, min(confidence * 100, 95)
