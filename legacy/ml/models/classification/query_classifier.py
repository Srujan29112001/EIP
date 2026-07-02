"""
Query Classification Model
Classifies user queries to route to appropriate agents
"""
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Any, Tuple
import numpy as np
import json


class QueryClassifier:
    """
    Classifies user queries into agent categories
    Uses fine-tuned BERT model for multi-label classification
    """

    # Agent categories
    AGENT_CATEGORIES = [
        "policy",
        "market",
        "finance",
        "tax",
        "distribution",
        "investment",
        "legal",
        "news"
    ]

    def __init__(self, model_path: str = None):
        """
        Initialize query classifier

        Args:
            model_path: Path to fine-tuned model (if None, uses base model)
        """
        if model_path:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_path,
                num_labels=len(self.AGENT_CATEGORIES)
            )
        else:
            # Use base model
            model_name = "distilbert-base-uncased"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=len(self.AGENT_CATEGORIES)
            )

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def classify(self, query: str, threshold: float = 0.3) -> Dict[str, Any]:
        """
        Classify query to determine relevant agents

        Args:
            query: User query string
            threshold: Confidence threshold for multi-label classification

        Returns:
            Dict with primary agent, secondary agents, and scores
        """
        # Tokenize
        inputs = self.tokenizer(
            query,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=True
        ).to(self.device)

        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits[0]
            probabilities = torch.sigmoid(logits)  # Multi-label

        # Get scores for each category
        scores = {
            category: prob.item()
            for category, prob in zip(self.AGENT_CATEGORIES, probabilities)
        }

        # Determine primary agent (highest score)
        primary_agent = max(scores, key=scores.get)
        primary_score = scores[primary_agent]

        # Determine secondary agents (above threshold, excluding primary)
        secondary_agents = [
            agent for agent, score in scores.items()
            if score > threshold and agent != primary_agent
        ]
        secondary_agents.sort(key=lambda x: scores[x], reverse=True)

        return {
            "query": query,
            "primary_agent": primary_agent,
            "primary_confidence": primary_score,
            "secondary_agents": secondary_agents,
            "all_scores": scores,
            "requires_multi_agent": len(secondary_agents) > 0
        }

    def classify_batch(self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Classify multiple queries in batch

        Args:
            queries: List of query strings

        Returns:
            List of classification results
        """
        return [self.classify(query) for query in queries]


class IntentClassifier:
    """
    Classifies user intent (question, command, analysis request, etc.)
    """

    INTENT_CATEGORIES = [
        "question",           # User asking a question
        "analysis_request",   # User wants analysis
        "recommendation",     # User wants recommendation
        "data_request",       # User wants data/reports
        "action_request",     # User wants to perform action
        "clarification",      # User seeking clarification
        "feedback",           # User providing feedback
        "other"              # Other intents
    ]

    def __init__(self):
        """Initialize intent classifier"""
        # Use zero-shot classification for intents
        from transformers import pipeline
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )

    def classify(self, query: str) -> Dict[str, Any]:
        """
        Classify user intent

        Args:
            query: User query

        Returns:
            Dict with intent and confidence
        """
        result = self.classifier(
            query,
            candidate_labels=self.INTENT_CATEGORIES,
            multi_label=False
        )

        return {
            "query": query,
            "intent": result["labels"][0],
            "confidence": result["scores"][0],
            "all_intents": {
                label: score
                for label, score in zip(result["labels"], result["scores"])
            }
        }


class UrgencyClassifier:
    """
    Classifies urgency level of user queries
    """

    URGENCY_LEVELS = [
        "critical",   # Immediate action required
        "high",       # Should be addressed soon
        "medium",     # Normal priority
        "low"         # Can be deferred
    ]

    CRITICAL_KEYWORDS = [
        "urgent", "asap", "immediately", "emergency", "critical",
        "deadline", "expiring", "last day", "today", "now"
    ]

    HIGH_KEYWORDS = [
        "soon", "quick", "fast", "this week", "important",
        "priority", "need", "required"
    ]

    def classify(self, query: str) -> Dict[str, Any]:
        """
        Classify urgency of query

        Args:
            query: User query

        Returns:
            Dict with urgency level and reasoning
        """
        query_lower = query.lower()

        # Check for critical keywords
        if any(keyword in query_lower for keyword in self.CRITICAL_KEYWORDS):
            return {
                "urgency": "critical",
                "score": 1.0,
                "reasoning": "Contains urgent/critical keywords"
            }

        # Check for high priority keywords
        if any(keyword in query_lower for keyword in self.HIGH_KEYWORDS):
            return {
                "urgency": "high",
                "score": 0.75,
                "reasoning": "Contains high priority keywords"
            }

        # Check query patterns
        if "?" in query and len(query.split()) < 10:
            # Short questions are usually medium priority
            return {
                "urgency": "medium",
                "score": 0.5,
                "reasoning": "Short, direct question"
            }

        # Default to low priority
        return {
            "urgency": "low",
            "score": 0.25,
            "reasoning": "No urgency indicators detected"
        }


# Export classifiers
__all__ = [
    "QueryClassifier",
    "IntentClassifier",
    "UrgencyClassifier"
]
