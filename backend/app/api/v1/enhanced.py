"""
Enhanced API Endpoints for Phase 2 Agents
Exposes all new agent capabilities via REST API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys
import os

# Add agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'agents'))

from enhanced.business_model_agent import BusinessModelAgent
from enhanced.stock_analysis_agent import StockAnalysisAgent
from enhanced.competitor_intelligence_agent import CompetitorIntelligenceAgent
from enhanced.subsidies_agent import SubsidiesAnalyzerAgent
from enhanced.business_model_recommender_agent import BusinessModelRecommenderAgent
from enhanced.loophole_predictor_agent import LoopholePredictorAgent
from enhanced.hedge_fund_agent import HedgeFundAnalyzerAgent
from enhanced.mutual_fund_agent import MutualFundAnalyzerAgent
from enhanced.industry_expert_agent import IndustryDomainExpertAgent
from enhanced.enhanced_news_agent import EnhancedNewsAgent

router = APIRouter()

# Initialize agents (singleton pattern for efficiency)
_agents = {
    "business_model": BusinessModelAgent(),
    "business_model_recommender": BusinessModelRecommenderAgent(),
    "stock_analysis": StockAnalysisAgent(),
    "competitor": CompetitorIntelligenceAgent(),
    "subsidies": SubsidiesAnalyzerAgent(),
    "loophole_predictor": LoopholePredictorAgent(),
    "hedge_fund": HedgeFundAnalyzerAgent(),
    "mutual_fund": MutualFundAnalyzerAgent(),
    "industry_expert": IndustryDomainExpertAgent(),
    "enhanced_news": EnhancedNewsAgent()
}


# Request/Response Models
class BusinessModelRequest(BaseModel):
    description: str
    industry: Optional[str] = None
    stage: Optional[str] = "seed"
    metrics: Optional[Dict[str, Any]] = None


class BusinessModelRecommenderRequest(BaseModel):
    idea: str
    industry: Optional[str] = None
    target_market: Optional[str] = "B2B"
    resources: Optional[str] = "Medium"
    timeline: Optional[str] = "18-24 months"


class StockAnalysisRequest(BaseModel):
    query: str
    symbols: Optional[List[str]] = None
    risk_tolerance: Optional[str] = "Moderate"
    investment_horizon: Optional[str] = "Long-term"


class CompetitorTrackingRequest(BaseModel):
    query: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    product: Optional[str] = None


class SubsidiesSearchRequest(BaseModel):
    query: str
    industry: Optional[str] = None
    country: Optional[str] = "India"
    stage: Optional[str] = "seed"
    entity_type: Optional[str] = None


# Business Model Analysis Endpoint
@router.post("/business-model/analyze")
async def analyze_business_model(request: BusinessModelRequest):
    """
    Analyze a business model using Business Model Canvas framework

    Returns comprehensive analysis with scores and recommendations.
    """
    try:
        agent = _agents["business_model"]

        context = {
            "industry": request.industry,
            "stage": request.stage,
            "metrics": request.metrics
        }

        result = await agent.process(request.description, context)

        return {
            "success": True,
            "data": {
                "canvas": result.get("canvas", {}),
                "scores": result.get("scores", {}),
                "recommendations": result.get("recommendations", []),
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0)
            },
            "metadata": {
                "agent": result.get("agent"),
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing business model: {str(e)}"
        )


# Business Model Recommender Endpoint
@router.post("/business-model/recommend")
async def recommend_business_model(request: BusinessModelRecommenderRequest):
    """
    Recommend optimal business models for a startup idea

    Returns top 3-5 recommended models with implementation roadmap.
    """
    try:
        agent = _agents["business_model_recommender"]

        context = {
            "industry": request.industry,
            "target_market": request.target_market,
            "resources": request.resources,
            "timeline": request.timeline
        }

        result = await agent.process(request.idea, context)

        return {
            "success": True,
            "data": {
                "recommendations": result.get("recommendations", []),
                "roadmap": result.get("roadmap", {}),
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0)
            },
            "metadata": {
                "agent": result.get("agent"),
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recommending business model: {str(e)}"
        )


# Stock Analysis Endpoint
@router.post("/stocks/analyze")
async def analyze_stocks(request: StockAnalysisRequest):
    """
    Analyze stocks with technical and fundamental analysis

    Returns comprehensive analysis with buy/sell/hold recommendations.
    """
    try:
        agent = _agents["stock_analysis"]

        context = {
            "risk_tolerance": request.risk_tolerance,
            "investment_horizon": request.investment_horizon
        }

        result = await agent.process(request.query, context)

        return {
            "success": True,
            "data": {
                "stocks": result.get("stocks", []),
                "technical": result.get("technical", {}),
                "fundamental": result.get("fundamental", {}),
                "recommendations": result.get("recommendations", []),
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0)
            },
            "metadata": {
                "agent": result.get("agent"),
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing stocks: {str(e)}"
        )


# Competitor Intelligence Endpoint
@router.post("/competitors/track")
async def track_competitors(request: CompetitorTrackingRequest):
    """
    Track and analyze competitors

    Returns competitor profiles, landscape analysis, and strategic recommendations.
    """
    try:
        agent = _agents["competitor"]

        context = {
            "company_name": request.company_name,
            "industry": request.industry,
            "product": request.product
        }

        result = await agent.process(request.query, context)

        return {
            "success": True,
            "data": {
                "competitors": result.get("competitors", []),
                "landscape": result.get("landscape", {}),
                "recent_moves": result.get("recent_moves", []),
                "strategy": result.get("strategy", {}),
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0)
            },
            "metadata": {
                "agent": result.get("agent"),
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking competitors: {str(e)}"
        )


# Subsidies Search Endpoint
@router.post("/subsidies/search")
async def search_subsidies(request: SubsidiesSearchRequest):
    """
    Search for eligible government subsidies and grants

    Returns eligible subsidies with application strategy.
    """
    try:
        agent = _agents["subsidies"]

        context = {
            "industry": request.industry,
            "country": request.country,
            "stage": request.stage,
            "entity_type": request.entity_type
        }

        result = await agent.process(request.query, context)

        return {
            "success": True,
            "data": {
                "subsidies": result.get("subsidies", []),
                "total_potential_funding": result.get("total_potential_funding", "₹0"),
                "application_strategy": result.get("application_strategy", {}),
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0)
            },
            "metadata": {
                "agent": result.get("agent"),
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching subsidies: {str(e)}"
        )


# Get Eligible Subsidies (simplified endpoint)
@router.get("/subsidies/eligible")
async def get_eligible_subsidies(
    industry: str,
    country: str = "India",
    stage: str = "seed"
):
    """
    Get eligible subsidies based on business criteria

    Query parameters:
    - industry: Business industry (Technology, Manufacturing, etc.)
    - country: Country (India, USA, etc.)
    - stage: Business stage (idea, seed, growth, expansion)
    """
    try:
        agent = _agents["subsidies"]

        query = f"What subsidies are available for {industry} businesses in {country}?"
        context = {
            "industry": industry,
            "country": country,
            "stage": stage
        }

        result = await agent.process(query, context)

        return {
            "success": True,
            "data": {
                "subsidies": result.get("subsidies", []),
                "total_potential_funding": result.get("total_potential_funding", "₹0"),
                "count": len(result.get("subsidies", []))
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching subsidies: {str(e)}"
        )


# ============================================================================
# NEW AGENTS - Phase 2 Complete
# ============================================================================

class LoopholePredictorRequest(BaseModel):
    query: str
    jurisdiction: Optional[str] = "USA"
    industry: Optional[str] = None
    revenue: Optional[float] = 0
    structure: Optional[str] = "LLC"


class HedgeFundRequest(BaseModel):
    query: str
    investment_amount: Optional[float] = 1000000
    risk_tolerance: Optional[str] = "moderate"


class MutualFundRequest(BaseModel):
    query: str
    age: Optional[int] = 35
    risk_tolerance: Optional[str] = "moderate"
    investment_amount: Optional[float] = 10000
    goal: Optional[str] = "retirement"


class IndustryExpertRequest(BaseModel):
    query: str
    industry: Optional[str] = None


class EnhancedNewsRequest(BaseModel):
    query: str
    topics: Optional[List[str]] = []
    timeframe: Optional[str] = "24h"
    max_articles: Optional[int] = 20


# Loophole Predictor Endpoint
@router.post("/tax/loopholes")
async def predict_tax_loopholes(request: LoopholePredictorRequest):
    """
    Identify legal tax optimization opportunities

    Returns eligible optimizations, structure recommendations, and compliance strategy.
    """
    try:
        agent = _agents["loophole_predictor"]

        context = {
            "jurisdiction": request.jurisdiction,
            "business_info": {
                "industry": request.industry,
                "revenue": request.revenue,
                "structure": request.structure
            }
        }

        result = await agent.process(request.query, context)

        return {
            "success": True,
            "data": {
                "applicable_optimizations": result.get("applicable_optimizations", []),
                "structure_recommendations": result.get("structure_recommendations", {}),
                "savings_analysis": result.get("savings_analysis", {}),
                "compliance_strategy": result.get("compliance_strategy", {}),
                "implementation_plan": result.get("implementation_plan", []),
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0)
            },
            "metadata": {
                "agent": "loophole_predictor",
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting loopholes: {str(e)}"
        )


# Hedge Fund Analyzer Endpoint
@router.post("/investments/hedge-funds")
async def analyze_hedge_funds(request: HedgeFundRequest):
    """
    Analyze hedge fund investment opportunities

    Returns fund analysis, portfolio recommendations, and risk assessment.
    """
    try:
        agent = _agents["hedge_fund"]

        context = {
            "investor_profile": {},
            "investment_amount": request.investment_amount,
            "risk_tolerance": request.risk_tolerance
        }

        result = await agent.process(request.query, context)

        return {
            "success": True,
            "data": {
                "eligible_funds": result.get("eligible_funds", []),
                "portfolio_recommendation": result.get("portfolio_recommendation", {}),
                "performance_analysis": result.get("performance_analysis", {}),
                "risk_assessment": result.get("risk_assessment", {}),
                "due_diligence": result.get("due_diligence", {}),
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0)
            },
            "metadata": {
                "agent": "hedge_fund",
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing hedge funds: {str(e)}"
        )


# Mutual Fund Analyzer Endpoint
@router.post("/investments/mutual-funds")
async def analyze_mutual_funds(request: MutualFundRequest):
    """
    Analyze and recommend mutual funds

    Returns fund comparison, portfolio allocation, and cost analysis.
    """
    try:
        agent = _agents["mutual_fund"]

        context = {
            "age": request.age,
            "risk_tolerance": request.risk_tolerance,
            "investment_amount": request.investment_amount,
            "goal": request.goal,
            "time_horizon": 10  # Default
        }

        result = await agent.process(request.query, context)

        return {
            "success": True,
            "data": {
                "eligible_funds": result.get("eligible_funds", []),
                "fund_comparison": result.get("fund_comparison", {}),
                "portfolio_recommendation": result.get("portfolio_recommendation", {}),
                "cost_analysis": result.get("cost_analysis", {}),
                "monitoring_plan": result.get("monitoring_plan", {}),
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0)
            },
            "metadata": {
                "agent": "mutual_fund",
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing mutual funds: {str(e)}"
        )


# Industry Expert Endpoint
@router.post("/industry/expertise")
async def get_industry_expertise(request: IndustryExpertRequest):
    """
    Get deep industry expertise and analysis

    Returns industry analysis, trends, competitive landscape, and entry strategy.
    """
    try:
        agent = _agents["industry_expert"]

        context = {
            "industry": request.industry
        }

        result = await agent.process(request.query, context)

        return {
            "success": True,
            "data": {
                "industry_analysis": result.get("industry_analysis", {}),
                "relevant_trends": result.get("relevant_trends", []),
                "competitive_analysis": result.get("competitive_analysis", {}),
                "entry_strategy": result.get("entry_strategy", {}),
                "success_roadmap": result.get("success_roadmap", {}),
                "risks_and_opportunities": result.get("risks_and_opportunities", {}),
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0)
            },
            "metadata": {
                "agent": "industry_expert",
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting industry expertise: {str(e)}"
        )


# Get available industries
@router.get("/industry/list")
async def list_industries():
    """Get list of available industries"""
    try:
        agent = _agents["industry_expert"]
        industries = agent.get_available_industries()

        return {
            "success": True,
            "industries": industries,
            "count": len(industries)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing industries: {str(e)}"
        )


# Enhanced News Endpoint
@router.post("/news/aggregated")
async def get_aggregated_news(request: EnhancedNewsRequest):
    """
    Get aggregated and analyzed news

    Returns news articles, sentiment analysis, trending topics, and market impact.
    """
    try:
        agent = _agents["enhanced_news"]

        context = {
            "topics": request.topics,
            "timeframe": request.timeframe,
            "max_articles": request.max_articles
        }

        result = await agent.process(request.query, context)

        return {
            "success": True,
            "data": {
                "articles": result.get("articles", []),
                "sentiment_analysis": result.get("sentiment_analysis", {}),
                "trending_topics": result.get("trending_topics", []),
                "market_impact": result.get("market_impact", {}),
                "article_clusters": result.get("article_clusters", []),
                "total_articles": result.get("total_articles", 0),
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0.0)
            },
            "metadata": {
                "agent": "enhanced_news",
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error aggregating news: {str(e)}"
        )


# Health check endpoint for enhanced agents
@router.get("/health")
async def health_check():
    """Check if all enhanced agents are operational"""
    try:
        agent_status = {}
        for name, agent in _agents.items():
            agent_status[name] = {
                "status": "operational",
                "agent_name": agent.name if hasattr(agent, 'name') else name
            }

        return {
            "success": True,
            "agents": agent_status,
            "total_agents": len(_agents),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
