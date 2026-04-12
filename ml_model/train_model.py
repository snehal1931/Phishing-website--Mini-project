"""
Train the Random Forest phishing detection model.
Uses a synthetic dataset if the real dataset isn't available,
then saves the model as phishing_model.pkl.

Run from the project root:
    py ml_model/train_model.py
"""
import os
import sys
import numpy as np
import joblib
from pathlib import Path

# ── Add project root to path so we can import feature_extractor ─────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scanner.feature_extractor import extract_features, features_to_list

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

MODEL_OUT = ROOT / 'ml_model' / 'phishing_model.pkl'

# ── Known phishing URLs for training ────────────────────────────────────────
PHISHING_URLS = [
    "http://free-recharge-india.xyz/claim?user=abc&token=123456",
    "http://193.168.1.1/bank/login.php",
    "http://paytm-kyc-verify.ml/update",
    "http://hdfc-bank-secure-login.tk/auth",
    "http://win-iphone-free.ga/claim?id=999",
    "http://sbi-online-kyc-urgent.cf/verify",
    "http://amazon-lucky-draw.xyz/winner",
    "http://free-4g-recharge.pw/offer",
    "http://google-reward-india.click/gift",
    "http://myaccount-update-now.gq/login",
    "http://phishing-site.com/signin?redirect=http://evil.com",
    "http://192.168.100.55/login/bank.html",
    "http://secure-axis-bank-login.ml/account",
    "http://verify-icici-otp.tk/confirm",
    "http://paytm-cashback-winner.xyz/claim",
    "http://free-jio-data-4g.ga/recharge",
    "http://income-tax-refund.cf/apply?pan=",
    "http://flipkart-lucky-winner.pw/prize",
    "http://whatsapp-premium-unlock.tk/activate",
    "http://bit.ly@malicious-redirect.com/login",
    "http://update-your-kyc-now.xyz/sbi",
    "http://covid-relief-fund.ml/apply",
    "http://pm-kisan-yojna-2024.ga/register",
    "http://aadhaar-link-bank.cf/update",
    "http://epfo-pf-withdraw-online.xyz/claim",
    "http://fake-netflix-india.tk/signup",
    "http://amazon-prime-free.ml/activate",
    "http://airtel-recharge-offer.ga/free",
    "http://bsnl-broadband-offer.cf/apply",
    "http://vodafone-cashback.pw/claim",
    "http://10.0.0.1/admin/login.php",
    "http://172.16.254.1/phish/page",
    "http://secure-login-hdfc--netbanking.com/auth",
    "http://sbi-netbanking--secure.com/login",
    "http://rbi-relief-fund-india.xyz/apply",
    "http://modi-relief-yojna.tk/register",
    "http://ration-card-update-online.ml/apply",
]

SAFE_URLS = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.wikipedia.org",
    "https://www.amazon.in",
    "https://www.flipkart.com",
    "https://www.paytm.com",
    "https://www.phonepe.com",
    "https://www.sbi.co.in",
    "https://www.hdfcbank.com",
    "https://www.icicibank.com",
    "https://www.axisbank.com",
    "https://www.irctc.co.in",
    "https://www.myntra.com",
    "https://www.zomato.com",
    "https://www.swiggy.com",
    "https://www.ola.com",
    "https://www.uber.com",
    "https://www.makemytrip.com",
    "https://www.booking.com",
    "https://mail.google.com",
    "https://drive.google.com",
    "https://docs.google.com",
    "https://github.com",
    "https://stackoverflow.com",
    "https://www.linkedin.com",
    "https://twitter.com",
    "https://www.instagram.com",
    "https://www.facebook.com",
    "https://www.microsoft.com",
    "https://www.apple.com",
    "https://www.netflix.com",
    "https://www.hotstar.com",
    "https://www.nic.in",
    "https://www.incometax.gov.in",
    "https://www.epfindia.gov.in",
    "https://www.digilocker.gov.in",
    "https://uidai.gov.in",
]


def build_dataset():
    X, y = [], []
    for url in PHISHING_URLS:
        feats = extract_features(url)
        X.append(features_to_list(feats))
        y.append(1)          # 1 = Phishing
    for url in SAFE_URLS:
        feats = extract_features(url)
        X.append(features_to_list(feats))
        y.append(0)          # 0 = Safe

    # Augment dataset with noise to avoid overfitting
    rng = np.random.default_rng(42)
    X_arr = np.array(X, dtype=float)
    noise = rng.normal(0, 0.5, X_arr.shape)
    X_aug = np.vstack([X_arr, X_arr + noise])
    y_aug = y + y

    return X_aug, y_aug


def train():
    print("=" * 55)
    print("  Phishing Detector — Model Training")
    print("=" * 55)

    X, y = build_dataset()
    print(f"  Dataset size: {len(y)} samples  "
          f"({y.count(1) if isinstance(y, list) else (np.array(y)==1).sum()} phishing, "
          f"{y.count(0) if isinstance(y, list) else (np.array(y)==0).sum()} safe)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        class_weight='balanced',
    )
    print("\n  Training Random Forest… ", end='', flush=True)
    clf.fit(X_train, y_train)
    print("Done!")

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n  Test Accuracy : {acc*100:.1f}%")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Safe', 'Phishing']))

    MODEL_OUT.parent.mkdir(exist_ok=True)
    joblib.dump(clf, MODEL_OUT)
    print(f"\n  ✅ Model saved → {MODEL_OUT}")
    print("=" * 55)


if __name__ == '__main__':
    train()
