"""
app.py
TrustLens AI -- a single-dashboard scam/fraud verification tool for students.

Every /api/check-* route follows the same contract:
    POST JSON in -> {"verdict": "safe|caution|danger", "risk_score": 0-100, "reasons": [...]}
and every result is logged to SQLite so the dashboard can show recent activity.

Run:
    python app.py
Then open http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, jsonify

import database
from checks.url_check import check_url
from checks.email_check import check_email
from checks.internship_check import check_internship_post, check_offer_letter
from checks.message_check import check_message

app = Flask(__name__)


@app.before_request
def _ensure_db():
    # init_db() is idempotent (CREATE TABLE IF NOT EXISTS), cheap enough to
    # call defensively rather than relying on a separate init step.
    database.init_db()


def _respond(check_type, input_summary, result):
    database.save_scan(
        check_type, input_summary, result["verdict"], result["risk_score"], result["reasons"]
    )
    return jsonify(result)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/check-url", methods=["POST"])
def api_check_url():
    data = request.get_json(force=True, silent=True) or {}
    url = data.get("url", "")
    result = check_url(url)
    return _respond("url", url, result)


@app.route("/api/check-email", methods=["POST"])
def api_check_email():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "")
    org = data.get("org", "")
    body = data.get("body", "")
    result = check_email(email, org, body)
    return _respond("email", email, result)


@app.route("/api/check-internship", methods=["POST"])
def api_check_internship():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    email = data.get("email", "")
    result = check_internship_post(text, email)
    return _respond("internship", text[:80], result)


@app.route("/api/check-offer-letter", methods=["POST"])
def api_check_offer_letter():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    email = data.get("email", "")
    result = check_offer_letter(text, email)
    return _respond("offer_letter", text[:80], result)


@app.route("/api/check-qr", methods=["POST"])
def api_check_qr():
    """QR images are decoded client-side with jsQR (static/js/app.js) so the
    server never needs a native zbar dependency. The browser sends us the
    already-decoded string, and we route it: URL-shaped content goes through
    check_url, everything else through check_message."""
    data = request.get_json(force=True, silent=True) or {}
    decoded = data.get("decoded_text", "")
    if not decoded.strip():
        return _respond("qr", "(none)", {"verdict": "safe", "risk_score": 0, "reasons": ["No QR content decoded."]})

    if decoded.strip().lower().startswith(("http://", "https://", "www.")):
        result = check_url(decoded)
        result["reasons"].insert(0, f"QR code decodes to a link: {decoded[:60]}")
    else:
        result = check_message(decoded)
        result["reasons"].insert(0, f"QR code decodes to text: {decoded[:60]}")
    return _respond("qr", decoded, result)


@app.route("/api/check-message", methods=["POST"])
def api_check_message():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    result = check_message(text)
    return _respond("message", text[:80], result)


@app.route("/api/history")
def api_history():
    return jsonify(database.get_recent_scans(limit=30))


@app.route("/api/stats")
def api_stats():
    return jsonify(database.get_stats())


if __name__ == "__main__":
    database.init_db()
    app.run(debug=True)
