"""
Enhanced AI Agents for EIP Platform - Phase 2, 3 & 4
Comprehensive specialized agents for complete business intelligence coverage
Total: 30 Enhanced Agents (12 Phase 2 + 15 Phase 3 + 3 Phase 4)
"""

# Phase 2 Agents (Original 10)
from .business_model_agent import BusinessModelAgent
from .stock_analysis_agent import StockAnalysisAgent
from .competitor_intelligence_agent import CompetitorIntelligenceAgent
from .subsidies_agent import SubsidiesAnalyzerAgent
from .business_model_recommender_agent import BusinessModelRecommenderAgent
from .loophole_predictor_agent import LoopholePredictorAgent
from .hedge_fund_agent import HedgeFundAnalyzerAgent
from .mutual_fund_agent import MutualFundAnalyzerAgent
from .industry_expert_agent import IndustryDomainExpertAgent
from .enhanced_news_agent import EnhancedNewsAgent
from .macroeconomics_agent import MacroeconomicsAgent
from .international_markets_agent import InternationalMarketsAgent

# Phase 3 Agents (New 17 - Complete 100%)
from .real_estate_agent import RealEstateAnalysisAgent
from .marketing_strategy_agent import MarketingStrategyAgent
from .hft_analysis_agent import HFTAnalysisAgent
from .business_strategy_agent import BusinessStrategyAgent
from .hr_analytics_agent import HRAnalyticsAgent
from .schemes_monitoring_agent import SchemesMonitoringAgent
from .regulator_analysis_agent import RegulatorAnalysisAgent
from .human_behaviour_agent import HumanBehaviourAgent
from .human_needs_agent import HumanNeedsAgent
from .esg_environmental_agent import ESGEnvironmentalAgent
from .philosophy_ethics_agent import PhilosophyEthicsAgent
from .money_happiness_agent import MoneyHappinessAgent
from .ngo_nonprofit_agent import NGONonProfitAgent
from .philanthropy_impact_agent import PhilanthropyImpactAgent
from .connecting_dots_agent import ConnectingDotsAgent

# Phase 4 Agents (NEW: 3)
from .geopolitics_agent import GeopoliticsAgent
from .trends_analysis_agent import TrendsAnalysisAgent
from .risk_analysis_agent import RiskAnalysisAgent

__all__ = [
    # Phase 2 Agents (12)
    "BusinessModelAgent",
    "StockAnalysisAgent",
    "CompetitorIntelligenceAgent",
    "SubsidiesAnalyzerAgent",
    "BusinessModelRecommenderAgent",
    "LoopholePredictorAgent",
    "HedgeFundAnalyzerAgent",
    "MutualFundAnalyzerAgent",
    "IndustryDomainExpertAgent",
    "EnhancedNewsAgent",
    "MacroeconomicsAgent",
    "InternationalMarketsAgent",
    # Phase 3 Agents (15 - NEW!)
    "RealEstateAnalysisAgent",
    "MarketingStrategyAgent",
    "HFTAnalysisAgent",
    "BusinessStrategyAgent",
    "HRAnalyticsAgent",
    "SchemesMonitoringAgent",
    "RegulatorAnalysisAgent",
    "HumanBehaviourAgent",
    "HumanNeedsAgent",
    "ESGEnvironmentalAgent",
    "PhilosophyEthicsAgent",
    "MoneyHappinessAgent",
    "NGONonProfitAgent",
    "PhilanthropyImpactAgent",
    "ConnectingDotsAgent",
    # Phase 4 Agents (3 - NEW!)
    "GeopoliticsAgent",
    "TrendsAnalysisAgent",
    "RiskAnalysisAgent",
]
