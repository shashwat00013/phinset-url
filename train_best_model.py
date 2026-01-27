import pickle
import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, f1_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from feature_extractor import extract_url_features


def get_structural_features(urls):
    return np.array([extract_url_features(u) for u in urls])


def main():
    # Load data
    df = pd.read_csv("clean_urls.csv")
    X = df["url"].astype(str)
    y = df["label"].astype(int)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Featureizers
    tfidf = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), max_features=8000)
    scaler = StandardScaler()

    # Fit on train
    X_train_text = tfidf.fit_transform(X_train)
    X_train_struct = get_structural_features(X_train)
    X_train_struct_scaled = scaler.fit_transform(X_train_struct)

    # Combine
    X_train_combined = hstack([X_train_text, csr_matrix(X_train_struct_scaled)])

    # Classifier: LinearSVC with probability calibration
    base_svc = LinearSVC(class_weight="balanced")
    clf = CalibratedClassifierCV(base_svc, method="sigmoid", cv=3)

    # Train
    clf.fit(X_train_combined, y_train)

    # Evaluate
    X_test_text = tfidf.transform(X_test)
    X_test_struct = get_structural_features(X_test)
    X_test_struct_scaled = scaler.transform(X_test_struct)
    X_test_combined = hstack([X_test_text, csr_matrix(X_test_struct_scaled)])

    y_pred = clf.predict(X_test_combined)
    f1 = f1_score(y_test, y_pred, average="macro")
    acc = accuracy_score(y_test, y_pred)

    print("\n=== Calibrated LinearSVC (TFIDF + structural) ===")
    print(f"Accuracy: {acc:.4f}  |  F1 (macro): {f1:.4f}")
    print(classification_report(y_test, y_pred))

    # Save artifacts expected by the Flask app
    pickle.dump(clf, open("url_phishing_model.pkl", "wb"))
    pickle.dump(tfidf, open("tfidf_vectorizer.pkl", "wb"))
    pickle.dump(scaler, open("scaler.pkl", "wb"))

    print("\n✅ MODEL SAVED: url_phishing_model.pkl, tfidf_vectorizer.pkl, scaler.pkl")


if __name__ == "__main__":
    main()
