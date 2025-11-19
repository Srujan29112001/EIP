"""
ML Model Inference Server
Serves trained ML models via REST API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os
import torch

# Add ML models to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from models.sentiment.sentiment_model import (
    SentimentAnalysisModel,
    FinancialSentimentModel,
    PolicySentimentModel
)
from models.classification.query_classifier import (
    QueryClassifier,
    IntentClassifier,
    UrgencyClassifier
)
from models.financial_forecasting.forecaster import FinancialForecaster
import pandas as pd

# Initialize FastAPI app
app = FastAPI(
    title="EIP ML Model Server",
    description="Inference server for EIP ML models",
    version="1.0.0"
)

# Initialize models (lazy loading)
models = {
    "sentiment": None,
    "financial_sentiment": None,
    "policy_sentiment": None,
    "query_classifier": None,
    "intent_classifier": None,
    "urgency_classifier": None,
    "financial_forecaster": None
}


# Request/Response models
class SentimentRequest(BaseModel):
    texts: List[str]


class SentimentResponse(BaseModel):
    results: List[Dict[str, Any]]


class QueryClassificationRequest(BaseModel):
    query: str
    threshold: float = 0.3


class QueryClassificationResponse(BaseModel):
    query: str
    primary_agent: str
    primary_confidence: float
    secondary_agents: List[str]
    all_scores: Dict[str, float]
    requires_multi_agent: bool


class IntentClassificationRequest(BaseModel):
    query: str


class UrgencyClassificationRequest(BaseModel):
    query: str


class ForecastRequest(BaseModel):
    historical_data: List[Dict[str, Any]]  # List of {date, revenue, ...}
    periods_ahead: int = 6


class RunwayRequest(BaseModel):
    current_cash: float
    monthly_burn_rate: float
    historical_revenue: List[Dict[str, Any]]


# Helper functions
def get_model(model_name: str):
    """Lazy load models"""
    if models[model_name] is None:
        if model_name == "sentiment":
            models[model_name] = SentimentAnalysisModel()
        elif model_name == "financial_sentiment":
            models[model_name] = FinancialSentimentModel()
        elif model_name == "policy_sentiment":
            models[model_name] = PolicySentimentModel()
        elif model_name == "query_classifier":
            models[model_name] = QueryClassifier()
        elif model_name == "intent_classifier":
            models[model_name] = IntentClassifier()
        elif model_name == "urgency_classifier":
            models[model_name] = UrgencyClassifier()
        elif model_name == "financial_forecaster":
            models[model_name] = FinancialForecaster()

    return models[model_name]


# Health check
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "EIP ML Model Server",
        "version": "1.0.0",
        "status": "running",
        "available_models": list(models.keys())
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Sentiment Analysis Endpoints
@app.post("/predict/sentiment", response_model=SentimentResponse)
def predict_sentiment(request: SentimentRequest):
    """
    Predict sentiment for texts

    Args:
        request: SentimentRequest with list of texts

    Returns:
        SentimentResponse with predictions
    """
    try:
        model = get_model("sentiment")
        results = model.predict(request.texts)
        return SentimentResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/financial-sentiment")
def predict_financial_sentiment(request: SentimentRequest):
    """Predict sentiment for financial news"""
    try:
        model = get_model("financial_sentiment")
        results = []
        for text in request.texts:
            result = model.analyze_market_impact(text)
            results.append(result)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/policy-sentiment")
def predict_policy_sentiment(
    policy_text: str,
    business_type: str = "startup"
):
    """Predict policy sentiment and impact"""
    try:
        model = get_model("policy_sentiment")
        result = model.analyze_policy_impact(policy_text, business_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Query Classification Endpoints
@app.post("/classify/query", response_model=QueryClassificationResponse)
def classify_query(request: QueryClassificationRequest):
    """
    Classify user query to determine agent routing

    Args:
        request: QueryClassificationRequest

    Returns:
        QueryClassificationResponse with classification
    """
    try:
        model = get_model("query_classifier")
        result = model.classify(request.query, request.threshold)
        return QueryClassificationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify/intent")
def classify_intent(request: IntentClassificationRequest):
    """Classify user intent"""
    try:
        model = get_model("intent_classifier")
        result = model.classify(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify/urgency")
def classify_urgency(request: UrgencyClassificationRequest):
    """Classify query urgency"""
    try:
        model = get_model("urgency_classifier")
        result = model.classify(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Financial Forecasting Endpoints
@app.post("/forecast/revenue")
def forecast_revenue(request: ForecastRequest):
    """Forecast future revenue"""
    try:
        model = get_model("financial_forecaster")

        # Convert to DataFrame
        df = pd.DataFrame(request.historical_data)

        result = model.forecast_revenue(df, request.periods_ahead)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/forecast/runway")
def forecast_runway(request: RunwayRequest):
    """Forecast cash runway"""
    try:
        model = get_model("financial_forecaster")

        # Convert to DataFrame
        df = pd.DataFrame(request.historical_revenue)

        result = model.forecast_runway(
            request.current_cash,
            request.monthly_burn_rate,
            df
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Model Management Endpoints
@app.post("/models/load/{model_name}")
def load_model(model_name: str):
    """Preload a specific model"""
    try:
        if model_name not in models:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

        get_model(model_name)
        return {"status": "loaded", "model": model_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/unload/{model_name}")
def unload_model(model_name: str):
    """Unload a model to free memory"""
    try:
        if model_name in models:
            models[model_name] = None
            # Force garbage collection
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        return {"status": "unloaded", "model": model_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/status")
def get_models_status():
    """Get status of all models"""
    status = {}
    for name, model in models.items():
        status[name] = "loaded" if model is not None else "not_loaded"
    return status


# Batch prediction endpoint
@app.post("/batch/classify-queries")
def batch_classify_queries(queries: List[str]):
    """Batch classify multiple queries"""
    try:
        model = get_model("query_classifier")
        results = model.classify_batch(queries)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "model_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
