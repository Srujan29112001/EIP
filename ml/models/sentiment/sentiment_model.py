"""
Sentiment Analysis Model
Analyzes sentiment of news articles, market reports, and user feedback
"""
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Any
import numpy as np


class SentimentAnalysisModel:
    """
    Sentiment analysis model using pre-trained transformers
    Supports multi-class sentiment: positive, negative, neutral
    """

    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Initialize sentiment analysis model

        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

        # Sentiment labels
        self.label_map = {
            0: "negative",
            1: "neutral",
            2: "positive"
        }

    def predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Predict sentiment for list of texts

        Args:
            texts: List of text strings to analyze

        Returns:
            List of dicts with sentiment, confidence, scores
        """
        results = []

        for text in texts:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)

            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)[0]
                predicted_class = torch.argmax(probabilities).item()

            # Map to sentiment
            sentiment = self.label_map.get(predicted_class, "neutral")
            confidence = probabilities[predicted_class].item()

            results.append({
                "text": text[:100] + "..." if len(text) > 100 else text,
                "sentiment": sentiment,
                "confidence": confidence,
                "scores": {
                    "negative": probabilities[0].item(),
                    "neutral": probabilities[1].item() if len(probabilities) > 2 else 0.0,
                    "positive": probabilities[1 if len(probabilities) == 2 else 2].item()
                }
            })

        return results

    def predict_single(self, text: str) -> Dict[str, Any]:
        """
        Predict sentiment for a single text

        Args:
            text: Text string to analyze

        Returns:
            Dict with sentiment, confidence, scores
        """
        return self.predict([text])[0]


class FinancialSentimentModel(SentimentAnalysisModel):
    """
    Specialized sentiment model for financial news and reports
    Fine-tuned on financial domain data
    """

    def __init__(self):
        # Use financial sentiment model
        super().__init__(model_name="ProsusAI/finbert")

        # Financial sentiment labels
        self.label_map = {
            0: "negative",
            1: "neutral",
            2: "positive"
        }

    def analyze_market_impact(self, text: str) -> Dict[str, Any]:
        """
        Analyze market impact of news/report

        Args:
            text: News article or market report

        Returns:
            Dict with sentiment and market impact score
        """
        sentiment_result = self.predict_single(text)

        # Calculate market impact score (-1 to +1)
        impact_score = 0.0
        if sentiment_result["sentiment"] == "positive":
            impact_score = sentiment_result["confidence"]
        elif sentiment_result["sentiment"] == "negative":
            impact_score = -sentiment_result["confidence"]

        return {
            **sentiment_result,
            "market_impact_score": impact_score,
            "impact_level": self._classify_impact(abs(impact_score))
        }

    def _classify_impact(self, score: float) -> str:
        """Classify impact level"""
        if score > 0.8:
            return "high"
        elif score > 0.5:
            return "medium"
        else:
            return "low"


class PolicySentimentModel(SentimentAnalysisModel):
    """
    Specialized model for analyzing policy sentiment
    Determines if policy is favorable/unfavorable for businesses
    """

    def analyze_policy_impact(self, policy_text: str, business_type: str) -> Dict[str, Any]:
        """
        Analyze policy impact on specific business type

        Args:
            policy_text: Policy document text
            business_type: Type of business (e.g., "startup", "SME", "enterprise")

        Returns:
            Dict with impact analysis
        """
        # Combine policy text with business context
        context_text = f"For {business_type} businesses: {policy_text}"

        sentiment_result = self.predict_single(context_text)

        # Calculate favorability score
        favorability = 0.0
        if sentiment_result["sentiment"] == "positive":
            favorability = sentiment_result["confidence"]
        elif sentiment_result["sentiment"] == "negative":
            favorability = -sentiment_result["confidence"]

        return {
            **sentiment_result,
            "business_type": business_type,
            "favorability_score": favorability,
            "recommendation": self._get_recommendation(favorability)
        }

    def _get_recommendation(self, favorability: float) -> str:
        """Get recommendation based on favorability"""
        if favorability > 0.5:
            return "Leverage this policy for business advantage"
        elif favorability < -0.5:
            return "Review compliance requirements and potential risks"
        else:
            return "Monitor for updates and assess impact"


# Export models
__all__ = [
    "SentimentAnalysisModel",
    "FinancialSentimentModel",
    "PolicySentimentModel"
]
