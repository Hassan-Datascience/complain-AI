import os
import joblib
import logging
from typing import Tuple, Dict, Any, Optional
from app.config import settings
from app.ml.vectorizer import NativeTfidfVectorizer, NativeMultinomialClassifier

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """
    AI Core Engine:
    1. Classification & Priority via trained TF-IDF + Logistic Regression ML models
    2. Actionable Summarization via Anthropic Claude LLM API (with fallback handling)
    """

    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or settings.MODEL_DIR
        self.vectorizer = None
        self.category_model = None
        self.priority_model = None
        self._load_models()

    def _load_models(self):
        """Loads trained sklearn models from disk safely without crashing server."""
        try:
            vec_path = os.path.join(self.model_dir, "vectorizer.pkl")
            cat_path = os.path.join(self.model_dir, "category_model.pkl")
            prio_path = os.path.join(self.model_dir, "priority_model.pkl")

            if os.path.exists(vec_path) and os.path.exists(cat_path) and os.path.exists(prio_path):
                self.vectorizer = joblib.load(vec_path)
                self.category_model = joblib.load(cat_path)
                self.priority_model = joblib.load(prio_path)
                logger.info("AI models and vectorizer loaded successfully.")
            else:
                logger.warning(f"AI model artifacts not found in {self.model_dir}. Run app.ml.train_classifier first.")
        except Exception as e:
            logger.error(f"Error loading ML models: {e}")

    def classify(self, text: str) -> Tuple[str, float]:
        """Predicts complaint category and returns (category_label, confidence_score)."""
        if not self.vectorizer or not self.category_model:
            return "Other", 0.50

        try:
            vectorized = self.vectorizer.transform([text])
            category = self.category_model.predict(vectorized)[0]

            if hasattr(self.category_model, "predict_proba"):
                probs = self.category_model.predict_proba(vectorized)[0]
                confidence = float(max(probs))
            else:
                confidence = 0.85

            return str(category), round(confidence, 4)
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return "Other", 0.50

    def predict_priority(self, text: str) -> Tuple[str, float]:
        """Predicts complaint priority level and returns (priority_label, confidence_score)."""
        if not self.vectorizer or not self.priority_model:
            return "Medium", 0.50

        try:
            vectorized = self.vectorizer.transform([text])
            priority = self.priority_model.predict(vectorized)[0]

            if hasattr(self.priority_model, "predict_proba"):
                probs = self.priority_model.predict_proba(vectorized)[0]
                confidence = float(max(probs))
            else:
                confidence = 0.85

            return str(priority), round(confidence, 4)
        except Exception as e:
            logger.error(f"Priority prediction failed: {e}")
            return "Medium", 0.50

    def summarize(self, text: str) -> Tuple[str, bool]:
        """
        Summarizes complaint text using LLM API.
        Returns tuple: (summary_string, fallback_used_boolean)
        """
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key:
            # Fallback if API key not configured
            summary = text[:120] + "..." if len(text) > 120 else text
            return summary, True

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)

            system_prompt = (
                "You are a civic service assistant. Summarize the following citizen "
                "complaint in exactly one actionable sentence for a municipal service team. "
                "Do not add information not present in the complaint. Do not include "
                "greetings or explanations — output only the summary sentence."
            )

            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=100,
                temperature=0.2,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": text}
                ]
            )

            summary_text = response.content[0].text.strip()
            return summary_text, False
        except Exception as e:
            logger.error(f"LLM Summarization API call failed: {e}. Using fallback.")
            summary = text[:120] + "..." if len(text) > 120 else text
            return summary, True

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Runs complete AI analysis pipeline:
        Category + Priority + Confidence + LLM Summarization
        """
        category, cat_conf = self.classify(text)
        priority, prio_conf = self.predict_priority(text)
        summary, fallback_used = self.summarize(text)

        # Average confidence between category and priority predictions
        overall_confidence = round((cat_conf + prio_conf) / 2.0, 4)

        return {
            "category": category,
            "priority": priority,
            "ai_summary": summary,
            "ai_confidence": overall_confidence,
            "ai_summary_fallback": fallback_used,
        }
