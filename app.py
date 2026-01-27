from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pickle
from urllib.parse import urlparse
from scipy.sparse import hstack, csr_matrix
from difflib import SequenceMatcher
import re
from feature_extractor import extract_url_features
import numpy as np
import csv
import os
import time

app = Flask(__name__)
CORS(app)

# Provide get_structural_features for compatibility with models pickled when this
# function was referenced via FunctionTransformer in the training pipeline.
def get_structural_features(urls):
    return np.array([extract_url_features(u) for u in urls])

# Load artifacts
model = pickle.load(open("url_phishing_model.pkl", "rb"))
vectorizer = pickle.load(open("tfidf_vectorizer.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

SAFE_DOMAINS = [
    "google.com", "github.com", "amazon.com", "paypal.com",
    "microsoft.com", "apple.com", "facebook.com",
    "twitter.com", "linkedin.com", "youtube.com", "gpt.com",
    "openai.com", "chat.openai.com", "stackoverflow.com",
    "example.com", "wikipedia.org", "reddit.com"
]

RISKY_HOSTS = [
    "github.io", "vercel.app", "netlify.app",
    "pages.dev", "firebaseapp.com"
]

URL_SHORTENERS = [
    "bit.ly", "tinyurl.com", "goo.gl", "t.co",
    "ow.ly", "is.gd", "buff.ly"
]

SUSPICIOUS_TLDS = [
    ".xyz", ".top", ".club", ".online",
    ".site", ".info", ".biz", ".ru", ".cn", ".tk"
]

BRANDS = [
    "google", "paypal", "amazon", "facebook",
    "microsoft", "apple", "instagram", "twitter"
]

# Keywords in path/query that often indicate login or credential capture flows
SUSPICIOUS_WORDS = [
    "login", "signin", "sign-in", "sign_in", "account", "verify",
    "verification", "update", "secure", "security", "reset",
    "password", "passcode", "otp", "2fa", "bank", "banking",
    "payment", "billing", "invoice", "support", "appeal",
    "free", "gift", "bonus", "prize", "reward", "claim", "offer",
    "urgent", "limited", "suspend", "unlock"
]

# -------- TYPO-SQUATTING --------
def is_typosquatting(domain, safe_domains, threshold=0.85):
    for safe in safe_domains:
        score = SequenceMatcher(None, domain, safe).ratio()
        if score >= threshold and domain != safe:
            return safe, score
    return None, 0

# -------- EXTRA CHECKS --------
def is_ip_address(domain):
    return bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain))

def has_many_subdomains(domain):
    return domain.count('.') >= 4

def has_suspicious_tld(domain):
    return any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS)

def brand_misuse(url, domain):
    for brand in BRANDS:
        if brand in url.lower() and brand not in domain:
            return brand
    return None

# -------- HEURISTIC SCORE --------
def heuristic_score(url):
    score = 0
    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace("www.", "")
    path_l = parsed.path.lower()
    query_l = parsed.query.lower()

    if any(h in domain for h in RISKY_HOSTS):
        score += 0.2
    if domain.count('.') > 3:
        score += 0.15
    if domain.count('-') > 2:
        score += 0.1
    if parsed.scheme == "http":
        score += 0.1

    # Suspicious keywords in path/query
    if any((kw in path_l) or (kw in query_l) for kw in SUSPICIOUS_WORDS):
        score += 0.2
        # Extra weight for explicit auth intents
        if "login" in path_l or "signin" in path_l or "sign-in" in path_l:
            score += 0.15
        if "account" in path_l:
            score += 0.1

    return min(score, 0.5)

# -------- CORE CHECK --------
def check_url(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace("www.", "")

    # ---- WHITELIST ----
    for safe in SAFE_DOMAINS:
        if domain == safe or domain.endswith("." + safe):
            # Require HTTPS for safe domains
            if parsed.scheme != "https":
                return {
                    "prediction": "suspicious",
                    "confidence": "85",
                    "reason": f"Trusted domain ({safe}) but using insecure HTTP protocol"
                }
            # If URL path/query contains risky intent words, don't blindly mark safe
            path_l = parsed.path.lower()
            query_l = parsed.query.lower()
            if any((kw in path_l) or (kw in query_l) for kw in SUSPICIOUS_WORDS):
                return {
                    "prediction": "suspicious",
                    "confidence": "75",
                    "reason": "Suspicious keywords on trusted domain"
                }
            return {
                "prediction": "safe",
                "confidence": "99.9",
                "reason": f"Known trusted domain ({safe}) with HTTPS"
            }

    # ---- TYPO-SQUATTING ----
    typo, score = is_typosquatting(domain, SAFE_DOMAINS)
    if typo:
        return {
            "prediction": "unsafe",
            "confidence": f"{round(score*100,1)}",
            "reason": f"Possible typosquatting of {typo}"
        }

    # ---- IP ADDRESS ----
    if is_ip_address(domain):
        return {
            "prediction": "unsafe",
            "confidence": "95",
            "reason": "IP address used instead of domain"
        }

    # ---- URL SHORTENER ----
    if domain in URL_SHORTENERS:
        return {
            "prediction": "suspicious",
            "confidence": "85",
            "reason": "URL shortener used"
        }

    # ---- SUSPICIOUS TLD ----
    if has_suspicious_tld(domain):
        return {
            "prediction": "suspicious",
            "confidence": "80",
            "reason": "Suspicious top-level domain"
        }

    # ---- TOO MANY SUBDOMAINS ----
    if has_many_subdomains(domain):
        return {
            "prediction": "unsafe",
            "confidence": "90",
            "reason": "Too many subdomains detected"
        }

    # ---- BRAND MISUSE ----
    brand = brand_misuse(url, domain)
    if brand:
        return {
            "prediction": "unsafe",
            "confidence": "92",
            "reason": f"Brand impersonation detected ({brand})"
        }

    # ---- SUSPICIOUS KEYWORDS IN URL (non-whitelisted domains) ----
    if domain not in SAFE_DOMAINS:
        path_l = parsed.path.lower()
        query_l = parsed.query.lower()
        if any((kw in path_l) or (kw in query_l) for kw in SUSPICIOUS_WORDS):
            return {
                "prediction": "suspicious",
                "confidence": "82",
                "reason": "Suspicious keywords in URL"
            }

    # ---- ML PREDICTION ----
    text_vec = vectorizer.transform([url])
    struct_vec = scaler.transform([extract_url_features(url)])
    X = hstack([text_vec, csr_matrix(struct_vec)])

    ml_prob = model.predict_proba(X)[0][1]
    rule_prob = heuristic_score(url)
    final_prob = 0.75 * ml_prob + 0.25 * rule_prob

    if final_prob >= 0.85:
        verdict = "unsafe"
    elif final_prob >= 0.6:
        verdict = "suspicious"
    else:
        verdict = "safe"

    return {
        "prediction": verdict,
        "confidence": f"{final_prob * 100:.1f}",
        "details": {
            "ml_probability": round(ml_prob, 3),
            "rule_adjustment": round(rule_prob, 3)
        }
    }

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "URL required"})
    return jsonify(check_url(url))

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json() or {}
    url = str(data.get("url", "")).strip()
    label = str(data.get("label", "")).strip().lower()
    notes = str(data.get("notes", "")).strip()

    if not url or label not in {"safe", "unsafe", "suspicious"}:
        return jsonify({"error": "Provide 'url' and 'label' in {'safe','unsafe','suspicious'}"}), 400

    path = os.path.join(os.getcwd(), "feedback.csv")
    file_exists = os.path.isfile(path)
    with open(path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "url", "label", "notes"])  # header
        writer.writerow([int(time.time()), url, label, notes])

    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    return send_file("index.html")

if __name__ == "__main__":
    print("Server running at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)
