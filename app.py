from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utils.url_checker import URLChecker
from utils.email_checker import EmailChecker
from utils.internship_checker import InternshipChecker
from utils.offer_checker import OfferChecker
from utils.qr_checker import QRChecker
from utils.scam_detector import ScamDetector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trustlens.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))

url_checker = URLChecker()
email_checker = EmailChecker()
internship_checker = InternshipChecker()
offer_checker = OfferChecker()
qr_checker = QRChecker()
scam_detector = ScamDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    total_checks = Verification.query.count()
    scam_count = Verification.query.filter_by(result='Scam').count()
    safe_count = Verification.query.filter_by(result='Safe').count()
    suspicious_count = Verification.query.filter_by(result='Suspicious').count()
    recent_checks = Verification.query.order_by(Verification.timestamp.desc()).limit(10).all()
    
    stats = {
        'total': total_checks,
        'scam': scam_count,
        'safe': safe_count,
        'suspicious': suspicious_count
    }
    return render_template('dashboard.html', stats=stats, recent_checks=recent_checks)

@app.route('/history')
def history():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    verifications = Verification.query.order_by(Verification.timestamp.desc()).paginate(page=page, per_page=per_page)
    return render_template('history.html', verifications=verifications)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    content = data.get('content', '')
    verification_type = data.get('type', '')
    
    if not content or not verification_type:
        return jsonify({'error': 'Missing required fields'}), 400
    
    result, explanation, confidence = "", "", 0.0
    
    if verification_type == 'url':
        result, explanation, confidence = url_checker.check(content)
    elif verification_type == 'email':
        result, explanation, confidence = email_checker.check(content)
    elif verification_type == 'internship':
        result, explanation, confidence = internship_checker.check(content)
    elif verification_type == 'offer':
        result, explanation, confidence = offer_checker.check(content)
    elif verification_type == 'qr':
        result, explanation, confidence = qr_checker.check(content)
    elif verification_type == 'scam_message':
        result, explanation, confidence = scam_detector.check(content)
    else:
        return jsonify({'error': 'Invalid verification type'}), 400
    
    verification = Verification(
        type=verification_type,
        content=content[:200],
        result=result,
        confidence=confidence,
        explanation=explanation,
        ip_address=request.remote_addr
    )
    db.session.add(verification)
    db.session.commit()
    
    return jsonify({
        'result': result,
        'confidence': confidence,
        'explanation': explanation,
        'type': verification_type
    })

@app.route('/api/stats')
def api_stats():
    total = Verification.query.count()
    scam = Verification.query.filter_by(result='Scam').count()
    safe = Verification.query.filter_by(result='Safe').count()
    suspicious = Verification.query.filter_by(result='Suspicious').count()
    return jsonify({'total': total, 'scam': scam, 'safe': safe, 'suspicious': suspicious})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
