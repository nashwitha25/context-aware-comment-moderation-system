import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# ---------------- PATHS ----------------
DATA_PATH = "backend/data/final/features_ready.csv"
MODEL_DIR = "backend/model/"

# ---------------- LOAD DATA ----------------
print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

X = df["comment_text"]
y = df["final_label"]

# ---------------- SPLIT ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---------------- TF-IDF ----------------
print("Vectorizing text...")
vectorizer = TfidfVectorizer(
    max_features=80000,
    ngram_range=(1, 3),
    stop_words="english",
    sublinear_tf=True
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

joblib.dump(vectorizer, MODEL_DIR + "vectorizer.pkl")
print("Vectorizer saved")

# ======================================================
# 1️⃣ LOGISTIC REGRESSION
# ======================================================
print("\nTraining Logistic Regression...")
logreg = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

logreg.fit(X_train_vec, y_train)
y_pred_lr = logreg.predict(X_test_vec)

print("Logistic Regression Accuracy:",
      accuracy_score(y_test, y_pred_lr))

joblib.dump(logreg, MODEL_DIR + "logistic_regression.pkl")
print("Logistic Regression saved")

# ======================================================
# 2️⃣ SGD CLASSIFIER (FAST & LARGE DATA FRIENDLY)
# ======================================================
print("\nTraining SGD Classifier...")
sgd = SGDClassifier(
    loss="log_loss",      # IMPORTANT (for probabilities)
    max_iter=1000,
    random_state=42,
    class_weight="balanced"
)

sgd.fit(X_train_vec, y_train)
y_pred_sgd = sgd.predict(X_test_vec)

print("SGD Classifier Accuracy:",
      accuracy_score(y_test, y_pred_sgd))

joblib.dump(sgd, MODEL_DIR + "sgd_classifier.pkl")
print("SGD Classifier saved")

# ======================================================
# 3️⃣ NAIVE BAYES
# ======================================================
print("\nTraining Naive Bayes...")
nb = MultinomialNB()

nb.fit(X_train_vec, y_train)
y_pred_nb = nb.predict(X_test_vec)

print("Naive Bayes Accuracy:",
      accuracy_score(y_test, y_pred_nb))

joblib.dump(nb, MODEL_DIR + "naive_bayes.pkl")
print("Naive Bayes saved")

# ---------------- DONE ----------------
print("\nALL INDIVIDUAL MODELS TRAINED SUCCESSFULLY")
