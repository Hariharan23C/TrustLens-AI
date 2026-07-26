# ML upgrade plan (Phase 2)

The current checkers in `checks/` are rule-based on purpose: every score is
traceable to an explicit reason, which is the whole point of "Explain WHY."

The planned scikit-learn upgrade **adds a second signal alongside the rules**
rather than replacing them:

1. **Data**: log real (anonymised) scan inputs + a manually-labelled
   safe/suspicious/dangerous column once enough scans accumulate.
2. **Features**: `TfidfVectorizer` over message/offer-letter text; a small
   set of engineered numeric features (domain length, digit ratio, etc.)
   reused from the existing `checks/*.py` heuristics.
3. **Model**: start with `LogisticRegression` or `RandomForestClassifier` —
   both expose feature importances, keeping results explainable.
4. **Blend**: final risk_score = weighted average of the rule-based score
   and the model's predicted probability, so a new model can never silently
   override a well-understood heuristic.
5. **Serving**: train offline (`ml/train.py`, not yet written), pickle with
   `joblib`, load once at Flask startup — no added runtime dependency beyond
   scikit-learn + joblib.

Not started yet — this file is the plan so the next contributor (or future
you) knows where the seams are.
