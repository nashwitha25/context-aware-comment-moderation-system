import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report

# Load dataset
df = pd.read_csv("backend/data/final/features_ready.csv")

X = df["comment_text"]
y = df["final_label"]

# Vectorize
vectorizer = TfidfVectorizer(max_features=5000)
X_vec = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42, stratify=y
)

# Load trained models
logreg = joblib.load("backend/model/logreg.pkl")
svm = joblib.load("backend/model/svm.pkl")
rf = joblib.load("backend/model/rf.pkl")


# Get probabilities
logreg_probs = logreg.predict_proba(X_test)[:, 1]
svm_probs = svm.predict_proba(X_test)[:, 1]
rf_probs = rf.predict_proba(X_test)[:, 1]

# Hybrid probability (weighted)
final_probs = (
    0.4 * logreg_probs +
    0.4 * svm_probs +
    0.2 * rf_probs
)

# Final prediction
y_pred = (final_probs >= 0.5).astype(int)

print("HYBRID MODEL PERFORMANCE")
print(classification_report(y_test, y_pred))

# Save hybrid components
joblib.dump(vectorizer, "backend/model/hybrid_vectorizer.pkl")
joblib.dump(
    {"logreg": logreg, "svm": svm, "rf": rf},
    "backend/model/hybrid_models.pkl"
)

print("Hybrid model saved successfully")
