# TrustLens AI

One dashboard. Six checks. Built for students.

TrustLens AI is a rule-based, fully explainable scam/fraud verification tool.
Paste a URL, email, internship post, offer letter, QR code, or scam message —
it scores the risk 0–100 and lists exactly *why*, so you can learn to spot
the pattern yourself next time.

## Checks

- 🔗 URL — phishing/typosquat/shortener heuristics
- ✉️ Email — spoofed sender domains, credential requests
- 🎓 Fake internship postings — upfront fees, unrealistic promises
- 📄 Fake offer letters — missing HR/comp details, payment requests
- ▦ QR codes — decoded client-side, then routed through URL/message checks
- 💬 Scam messages — lottery scams, urgency, OTP phishing

## Stack

- Python 3 + Flask
- SQLite (scan history, no setup required)
- HTML/CSS/vanilla JS (+ [jsQR](https://github.com/cozmo/jsQR) for in-browser QR decoding)
- scikit-learn — planned upgrade, see `ml/README.md`

## Run it locally

```bash
git clone https://github.com/<your-username>/trustlens-ai.git
cd trustlens-ai
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000**.

The SQLite database is created automatically at `instance/trustlens.db` on
first run — nothing to configure.

## Project structure

```
trustlens-ai/
├── app.py                  # Flask routes / API
├── database.py              # SQLite helpers
├── checks/                  # One module per check, all explainable
│   ├── url_check.py
│   ├── email_check.py
│   ├── internship_check.py
│   └── message_check.py
├── templates/index.html
├── static/css/style.css
├── static/js/app.js
├── ml/README.md             # scikit-learn upgrade plan
└── requirements.txt
```

## Why rule-based, not ML, right now

Every verdict needs to be explainable to a student who has never heard of
phishing before — "why is this risky?" matters more than squeezing out
accuracy from a black box. The heuristics in `checks/` are the "explain WHY"
feature by construction. See `ml/README.md` for how a scikit-learn model
will complement (not replace) this later.

## Disclaimer

TrustLens AI flags patterns; it doesn't guarantee an outcome. When in doubt,
verify directly with the official organisation through a channel you trust.
