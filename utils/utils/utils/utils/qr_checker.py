import re

class QRChecker:
    def check(self, content):
        result = "Safe"
        confidence = 0.0
        reasons = []
        
        if re.match(r'^https?://', content):
            if any(w in content.lower() for w in ['login', 'verify', 'authenticate']):
                reasons.append("QR leads to login page")
                confidence += 0.2
            if 'bit.ly' in content:
                reasons.append("Shortened URL")
                confidence += 0.15
        
        if any(w in content.lower() for w in ['pay', 'upi', 'gpay']):
            reasons.append("Payment QR")
            confidence += 0.25
        
        if confidence >= 0.5:
            result = "Suspicious"
        if confidence >= 0.7:
            result = "Scam"
        
        explanation = " | ".join(reasons) if reasons else "QR code seems safe"
        return result, explanation, min(confidence * 100, 95)
