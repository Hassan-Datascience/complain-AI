import os
import joblib
import numpy as np
import pandas as pd
from app.ml.vectorizer import NativeTfidfVectorizer, NativeMultinomialClassifier

try:
    from sklearn.feature_extraction.text import TfidfVectorizer as SklearnTfidfVectorizer
    from sklearn.linear_model import LogisticRegression as SklearnLogisticRegression
    from sklearn.metrics import accuracy_score
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

def train_and_save_models(
    data_path: str = "data/training_data.csv",
    output_dir: str = "app/ml"
):
    """
    Trains vectorizer and ML classifiers for category and priority prediction.
    Saves pickle models to app/ml directory.
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training dataset not found at {data_path}")

    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(data_path)

    print(f"Loaded {len(df)} records from {data_path}.")

    X_text = df['description'].astype(str).tolist()
    y_category = df['category'].tolist()
    y_priority = df['priority'].tolist()

    if SKLEARN_AVAILABLE:
        print("\n--- Training with Scikit-Learn Pipeline ---")
        vectorizer = SklearnTfidfVectorizer(
            max_features=1500,
            ngram_range=(1, 2),
            stop_words='english',
            sublinear_tf=True
        )
        X_vec = vectorizer.fit_transform(X_text)

        cat_model = SklearnLogisticRegression(max_iter=1000, C=1.5, random_state=42)
        cat_model.fit(X_vec, y_category)

        prio_model = SklearnLogisticRegression(max_iter=1000, C=1.5, random_state=42)
        prio_model.fit(X_vec, y_priority)

        cat_acc = accuracy_score(y_category, cat_model.predict(X_vec))
        prio_acc = accuracy_score(y_priority, prio_model.predict(X_vec))
    else:
        print("\n--- Training with Native High-Performance ML Engine ---")
        vectorizer = NativeTfidfVectorizer(max_features=1500)
        X_vec = vectorizer.fit_transform(X_text)

        cat_model = NativeMultinomialClassifier(alpha=0.5)
        cat_model.fit(X_vec, y_category)

        prio_model = NativeMultinomialClassifier(alpha=0.5)
        prio_model.fit(X_vec, y_priority)

        cat_preds = cat_model.predict(X_vec)
        prio_preds = prio_model.predict(X_vec)

        cat_acc = np.mean(cat_preds == np.array(y_category))
        prio_acc = np.mean(prio_preds == np.array(y_priority))

    print(f"[Category Model] Training Accuracy: {cat_acc * 100:.2f}%")
    print(f"[Priority Model] Training Accuracy: {prio_acc * 100:.2f}%")

    vec_path = os.path.join(output_dir, "vectorizer.pkl")
    cat_path = os.path.join(output_dir, "category_model.pkl")
    prio_path = os.path.join(output_dir, "priority_model.pkl")

    joblib.dump(vectorizer, vec_path)
    joblib.dump(cat_model, cat_path)
    joblib.dump(prio_model, prio_path)

    print("\nModel artifact files successfully saved:")
    print(f" - {vec_path}")
    print(f" - {cat_path}")
    print(f" - {prio_path}")

if __name__ == "__main__":
    train_and_save_models()
