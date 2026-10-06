import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logreg = joblib.load(os.path.join(BASE_DIR, "model", "logistic_regression.pkl"))
sgd = joblib.load(os.path.join(BASE_DIR, "model", "sgd_classifier.pkl"))
nb = joblib.load(os.path.join(BASE_DIR, "model", "naive_bayes.pkl"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "model", "vectorizer.pkl"))

hybrid_models = {
    "logreg": logreg,
    "sgd": sgd,
    "nb": nb
}

joblib.dump(hybrid_models, os.path.join(BASE_DIR, "model", "hybrid_models.pkl"))
joblib.dump(vectorizer, os.path.join(BASE_DIR, "model", "hybrid_vectorizer.pkl"))

print("HYBRID MODELS UPDATED SUCCESSFULLY")
