import math
import numpy as np
from typing import List, Dict, Set, Optional

class NativeTfidfVectorizer:
    """TF-IDF Vectorizer with stop words filtering and L2 normalization."""
    def __init__(self, max_features: int = 1500, stop_words: Optional[Set[str]] = None):
        self.max_features = max_features
        self.stop_words = stop_words or {
            "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with",
            "by", "about", "against", "between", "into", "through", "during", "before",
            "after", "above", "below", "from", "up", "down", "of", "off", "over", "under"
        }
        self.vocabulary_: Dict[str, int] = {}
        self.idf_: np.ndarray = np.array([])

    def _tokenize(self, text: str) -> List[str]:
        cleaned = "".join(c.lower() if c.isalnum() or c.isspace() else " " for c in text)
        words = cleaned.split()
        return [w for w in words if w not in self.stop_words and len(w) > 1]

    def fit_transform(self, raw_documents: List[str]) -> np.ndarray:
        doc_tokens = [self._tokenize(doc) for doc in raw_documents]
        
        df_counts: Dict[str, int] = {}
        for tokens in doc_tokens:
            unique_tokens = set(tokens)
            for t in unique_tokens:
                df_counts[t] = df_counts.get(t, 0) + 1

        sorted_terms = sorted(df_counts.items(), key=lambda x: x[1], reverse=True)[:self.max_features]
        self.vocabulary_ = {term: idx for idx, (term, _) in enumerate(sorted_terms)}
        
        n_docs = len(raw_documents)
        idfs = [math.log((1 + n_docs) / (1 + df_counts[term])) + 1.0 for term, _ in sorted_terms]
        self.idf_ = np.array(idfs)

        return self.transform(raw_documents)

    def transform(self, raw_documents: List[str]) -> np.ndarray:
        n_docs = len(raw_documents)
        n_features = len(self.vocabulary_)
        matrix = np.zeros((n_docs, n_features), dtype=np.float64)

        for doc_idx, doc in enumerate(raw_documents):
            tokens = self._tokenize(doc)
            if not tokens:
                continue
            tf_counts: Dict[int, int] = {}
            for t in tokens:
                if t in self.vocabulary_:
                    idx = self.vocabulary_[t]
                    tf_counts[idx] = tf_counts.get(idx, 0) + 1
            
            for idx, count in tf_counts.items():
                matrix[doc_idx, idx] = (count / len(tokens)) * self.idf_[idx]

            norm = np.linalg.norm(matrix[doc_idx])
            if norm > 0:
                matrix[doc_idx] /= norm

        return matrix


class NativeMultinomialClassifier:
    """Multinomial Naive Bayes / Softmax Classifier with predict_proba support."""
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.classes_: np.ndarray = np.array([])
        self.class_log_prior_: np.ndarray = np.array([])
        self.feature_log_prob_: np.ndarray = np.array([])

    def fit(self, X: np.ndarray, y: List[str]):
        labels = np.array(y)
        self.classes_ = np.unique(labels)
        n_classes = len(self.classes_)
        n_features = X.shape[1]

        self.class_log_prior_ = np.zeros(n_classes)
        self.feature_log_prob_ = np.zeros((n_classes, n_features))

        for idx, c in enumerate(self.classes_):
            X_c = X[labels == c]
            self.class_log_prior_[idx] = math.log(X_c.shape[0] / X.shape[0])
            fc = np.sum(X_c, axis=0) + self.alpha
            self.feature_log_prob_[idx] = np.log(fc / np.sum(fc))

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        jll = X @ self.feature_log_prob_.T + self.class_log_prior_
        max_jll = np.max(jll, axis=1, keepdims=True)
        exp_jll = np.exp(jll - max_jll)
        return exp_jll / np.sum(exp_jll, axis=1, keepdims=True)

    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        best_indices = np.argmax(probs, axis=1)
        return self.classes_[best_indices]
