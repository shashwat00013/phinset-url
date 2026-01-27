import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.metrics import classification_report, f1_score
from sklearn.pipeline import Pipeline, FeatureUnion
from feature_extractor import extract_url_features


def get_structural_features(urls):
    return np.array([extract_url_features(u) for u in urls])


def build_features():
    text_features = Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3, 5), max_features=8000))
    ])

    structural_features = Pipeline([
        ("selector", FunctionTransformer(get_structural_features, validate=False)),
        ("scaler", StandardScaler())
    ])

    return FeatureUnion([
        ("text_features", text_features),
        ("structural_features", structural_features)
    ])


def evaluate_model(name, classifier, X_train, X_test, y_train, y_test):
    pipeline = Pipeline([
        ("features", build_features()),
        ("classifier", classifier)
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    print(f"\n=== {name} ===")
    print(f"F1 (macro): {f1_score(y_test, y_pred, average='macro'):.4f}")
    print(classification_report(y_test, y_pred))
    return pipeline


def main():
    df = pd.read_csv("clean_urls.csv")
    X = df["url"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    models = [
        ("LogisticRegression", LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear")),
        ("LinearSVC", LinearSVC(class_weight="balanced")),
        ("SGDClassifier", SGDClassifier(loss="hinge", max_iter=2000, class_weight="balanced"))
    ]

    best_model = None
    best_f1 = -1.0

    for name, clf in models:
        model = evaluate_model(name, clf, X_train, X_test, y_train, y_test)
        y_pred = model.predict(X_test)
        score = f1_score(y_test, y_pred, average="macro")
        if score > best_f1:
            best_f1 = score
            best_model = (name, model)

    print(f"\nBest model: {best_model[0]} (F1 macro={best_f1:.4f})")


if __name__ == "__main__":
    main()
