"""
Retrains priority + category models using project's NativeTfidfVectorizer
(no scipy/sklearn needed at all).
Run from project root: python scripts/retrain_native.py
"""
import os
import sys
import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath("."))

from app.ml.vectorizer import NativeTfidfVectorizer, NativeMultinomialClassifier

DATA_PATH = "data/training_data.csv"
MODEL_DIR = "app/ml"

def accuracy(y_true, y_pred):
    return np.mean(np.array(y_true) == np.array(y_pred))

def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Training on {len(df)} rows")

    X_text  = df["description"].astype(str).tolist()
    y_cat   = df["category"].tolist()
    y_prio  = df["priority"].tolist()

    vec = NativeTfidfVectorizer(max_features=1500)
    X   = vec.fit_transform(X_text)

    cat_model  = NativeMultinomialClassifier(alpha=0.5)
    cat_model.fit(X, y_cat)

    prio_model = NativeMultinomialClassifier(alpha=0.5)
    prio_model.fit(X, y_prio)

    cat_acc  = accuracy(y_cat,  cat_model.predict(X))
    prio_acc = accuracy(y_prio, prio_model.predict(X))

    joblib.dump(vec,        os.path.join(MODEL_DIR, "vectorizer.pkl"))
    joblib.dump(cat_model,  os.path.join(MODEL_DIR, "category_model.pkl"))
    joblib.dump(prio_model, os.path.join(MODEL_DIR, "priority_model.pkl"))

    print(f"Category model training accuracy : {cat_acc*100:.2f}%")
    print(f"Priority model training accuracy : {prio_acc*100:.2f}%")
    print("All model artifacts saved successfully.")

if __name__ == "__main__":
    main()
