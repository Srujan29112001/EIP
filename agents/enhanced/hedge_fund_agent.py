"""
Hedge Fund Analyzer Agent - Alternative Investment Strategy Analysis
Analyzes hedge fund strategies, performance metrics, and provides investment insights
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import random

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agents.base.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class HedgeFundAnalyzerAgent(BaseAgent):
    """
    Sophisticated agent for analyzing hedge fund strategies and performance
    Provides insights on alternative investment opportunities for entrepreneurs
    """

    def __init__(self):
        super().__init__(
            name="Hedge Fund Analyzer Agent",
            description="Analyzes hedge fund strategies, performance, and alternative investments",
            capabilities=[
                "hedge_fund_strategy_analysis",
                "performance_evaluation",
                "risk_adjusted_returns",
                "manager_due_diligence",
                "portfolio_construction",
                "alternative_investment_screening"
            ]
        )

        # Hedge fund database
        self.hedge_funds = self._initialize_hedge_fund_database()

        # Strategy classifications
        self.strategies = self._initialize_strategy_types()

        # Performance benchmarks
        self.benchmarks = self._initialize_benchmarks()

    def _initialize_hedge_fund_database(self) -> List[Dict[str, Any]]:
        """Initialize database of notable hedge funds"""
        return [
            {
                "fund_name": "Bridgewater Associates - Pure Alpha",
                "manager": "Bridgewater Associates",
                "aum": 140000000000,  # $140B
                "strategy": "Global Macro",
                "sub_strategy": "Systematic Macro",
                "inception_year": 1975,
                "minimum_investment": 5000000,
                "performance": {
                    "1_year": 5.2,
                    "3_year": 8.1,
                    "5_year": 7.8,
                    "10_year": 9.2,
                    "since_inception": 12.1
                },
                "volatility": 12.5,
                "sharpe_ratio": 1.12,
                "max_drawdown": -15.3,
                "correlation_sp500": 0.21,
                "fees": {"management": 2.0, "performance": 20.0},
                "liquidity": "Quarterly with 90 days notice",
                "key_personnel": ["Ray Dalio", "Greg Jensen"],
                "investment_process": "Systematic, rules-based approach using economic principles",
                "risk_factors": ["Model risk", "Leverage", "Liquidity"]
            },
            {
                "fund_name": "Renaissance Technologies - Medallion Fund",
                "manager": "Renaissance Technologies",
                "aum": 10000000000,  # $10B (closed to new investors)
                "strategy": "Quantitative/Statistical Arbitrage",
                "sub_strategy": "High-Frequency Trading",
                "inception_year": 1988,
                "minimum_investment": None,  # Closed
                "performance": {
                    "1_year": 45.2,  # Historically exceptional
                    "3_year": 39.1,
                    "5_year": 42.3,
                    "10_year": 38.5,
                    "since_inception": 66.1
                },
                "volatility": 15.2,
                "sharpe_ratio": 4.21,
                "max_drawdown": -8.7,
                "correlation_sp500": 0.08,
                "fees": {"management": 5.0, "performance": 44.0},
                "liquidity": "Closed to external investors",
                "key_personnel": ["Jim Simons (founder)", "Peter Brown"],
                "investment_process": "Quantitative models based on statistical patterns",
                "risk_factors": ["Model risk", "Technology risk", "Market microstructure changes"]
            },
            {
                "fund_name": "Elliott Management",
                "manager": "Elliott Management",
                "aum": 55000000000,  # $55B
                "strategy": "Multi-Strategy",
                "sub_strategy": "Activist/Event-Driven",
                "inception_year": 1977,
                "minimum_investment": 5000000,
                "performance": {
                    "1_year": 12.3,
                    "3_year": 10.8,
                    "5_year": 11.2,
                    "10_year": 13.1,
                    "since_inception": 14.2
                },
                "volatility": 9.8,
                "sharpe_ratio": 1.35,
                "max_drawdown": -11.2,
                "correlation_sp500": 0.35,
                "fees": {"management": 2.0, "performance": 20.0},
                "liquidity": "Annual with 90 days notice",
                "key_personnel": ["Paul Singer"],
                "investment_process": "Fundamental analysis with activist engagement",
                "risk_factors": ["Concentration risk", "Litigation risk", "Activist campaign execution"]
            },
            {
                "fund_name": "Citadel Wellington",
                "manager": "Citadel",
                "aum": 43000000000,  # $43B
                "strategy": "Multi-Strategy",
                "sub_strategy": "Market Neutral/Relative Value",
                "inception_year": 1990,
                "minimum_investment": 10000000,
                "performance": {
                    "1_year": 15.8,
                    "3_year": 12.1,
                    "5_year": 13.5,
                    "10_year": 11.8,
                    "since_inception": 19.2
                },
                "volatility": 8.3,
                "sharpe_ratio": 1.62,
                "max_drawdown": -9.1,
                "correlation_sp500": 0.28,
                "fees": {"management": 2.0, "performance": 20.0},
                "liquidity": "Quarterly with 60 days notice",
                "key_personnel": ["Ken Griffin"],
                "investment_process": "Quantitative and fundamental, multi-strategy pods",
                "risk_factors": ["Manager turnover", "Leverage", "Strategy crowding"]
            },
            {
                "fund_name": "Two Sigma Absolute Return",
                "manager": "Two Sigma",
                "aum": 58000000000,  # $58B
                "strategy": "Quantitative",
                "sub_strategy": "Machine Learning/AI",
                "inception_year": 2001,
                "minimum_investment": 5000000,
                "performance": {
                    "1_year": 18.2,
                    "3_year": 14.5,
                    "5_year": 15.1,
                    "10_year": 16.3,
                    "since_inception": 17.8
                },
                "volatility": 11.2,
                "sharpe_ratio": 1.45,
                "max_drawdown": -12.3,
                "correlation_sp500": 0.19,
                "fees": {"management": 2.5, "performance": 25.0},
                "liquidity": "Quarterly with 90 days notice",
                "key_personnel": ["John Overdeck", "David Siegel"],
                "investment_process": "Machine learning models on vast datasets",
                "risk_factors": ["Model overfitting", "Data quality", "Technology infrastructure"]
            },
            {
                "fund_name": "Pershing Square Holdings",
                "manager": "Pershing Square",
                "aum": 16000000000,  # $16B
                "strategy": "Long/Short Equity",
                "sub_strategy": "Concentrated Value/Activist",
                "inception_year": 2004,
                "minimum_investment": None,  # Publicly traded vehicle
                "performance": {
                    "1_year": 24.5,
                    "3_year": 18.7,
                    "5_year": 22.3,
                    "10_year": 15.2,
                    "since_inception": 16.8
                },
                "volatility": 22.1,
                "sharpe_ratio": 1.02,
                "max_drawdown": -31.5,
                "correlation_sp500": 0.62,
                "fees": {"management": 1.5, "performance": 16.0},
                "liquidity": "Daily (publicly traded)",
                "key_personnel": ["Bill Ackman"],
                "investment_process": "Concentrated positions in 8-12 high-conviction ideas",
                "risk_factors": ["Concentration risk", "High volatility", "Activist execution risk"]
            }
        ]

    def _initialize_strategy_types(self) -> Dict[str, Any]:
        """Initialize hedge fund strategy classifications"""
        return {
            "Equity Long/Short": {
                "description": "Long positions in undervalued stocks, short overvalued",
                "typical_returns": "8-12% annually",
                "volatility": "8-15%",
                "market_correlation": "0.4-0.7",
                "liquidity": "Monthly to Quarterly",
                "key_risks": ["Market risk", "Short squeeze", "Sector concentration"],
                "best_for": "Moderate risk tolerance, equity market exposure"
            },
            "Global Macro": {
                "description": "Top-down analysis of economic trends, currencies, rates",
                "typical_returns": "7-15% annually",
                "volatility": "10-18%",
                "market_correlation": "0.1-0.3",
                "liquidity": "Monthly to Quarterly",
                "key_risks": ["Policy shifts", "Leverage", "Model risk"],
                "best_for": "Diversification, inflation protection"
            },
            "Event-Driven": {
                "description": "M&A arbitrage, restructurings, special situations",
                "typical_returns": "8-14% annually",
                "volatility": "6-12%",
                "market_correlation": "0.3-0.5",
                "liquidity": "Quarterly to Annual",
                "key_risks": ["Deal breaks", "Regulatory", "Financing risk"],
                "best_for": "Moderate returns with lower volatility"
            },
            "Relative Value": {
                "description": "Exploit pricing inefficiencies between related securities",
                "typical_returns": "6-10% annually",
                "volatility": "4-8%",
                "market_correlation": "0.1-0.3",
                "liquidity": "Monthly to Quarterly",
                "key_risks": ["Basis risk", "Liquidity", "Model risk"],
                "best_for": "Stable returns, portfolio ballast"
            },
            "Quantitative": {
                "description": "Systematic strategies using algorithms and models",
                "typical_returns": "10-20% annually",
                "volatility": "8-16%",
                "market_correlation": "0.1-0.4",
                "liquidity": "Monthly to Quarterly",
                "key_risks": ["Model overfitting", "Technology", "Crowding"],
                "best_for": "High Sharpe ratio, diversification"
            },
            "Multi-Strategy": {
                "description": "Diversified across multiple hedge fund strategies",
                "typical_returns": "8-12% annually",
                "volatility": "6-10%",
                "market_correlation": "0.2-0.4",
                "liquidity": "Quarterly",
                "key_risks": ["Complexity", "Fee drag", "Cross-strategy risks"],
                "best_for": "One-stop-shop diversification"
            }
        }

    def _initialize_benchmarks(self) -> Dict[str, Any]:
        """Initialize performance benchmarks"""
        return {
            "HFRI Fund Weighted Composite": {
                "1_year": 7.2,
                "3_year": 6.8,
                "5_year": 7.1,
                "10_year": 6.5
            },
            "S&P 500": {
                "1_year": 26.3,
                "3_year": 12.1,
                "5_year": 15.8,
                "10_year": 12.9
            },
            "60/40 Portfolio": {
                "1_year": 17.2,
                "3_year": 8.5,
                "5_year": 10.2,
                "10_year": 9.1
            },
            "Risk-Free Rate": {
                "current": 4.5
            }
        }

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process hedge fund analysis request

        Args:
            query: User query about hedge funds
            context: Additional context (investor profile, strategy preferences, etc.)

        Returns:
            Dict with fund analysis, recommendations, and insights
        """
        try:
            logger.info(f"Processing hedge fund analysis query: {query[:100]}...")

            # Extract investor profile from context
            investor_profile = context.get("investor_profile", {}) if context else {}
            investment_amount = context.get("investment_amount", 1000000) if context else 1000000
            risk_tolerance = context.get("risk_tolerance", "moderate") if context else "moderate"

            # Analyze strategy suitability
            strategy_analysis = await self._analyze_strategy_suitability(
                investor_profile, risk_tolerance
            )

            # Screen eligible funds
            eligible_funds = await self._screen_funds(
                investment_amount, risk_tolerance, investor_profile
            )

            # Perform due diligence
            due_diligence = await self._perform_due_diligence(eligible_funds)

            # Construct portfolio recommendation
            portfolio_recommendation = await self._construct_portfolio(
                eligible_funds, investment_amount, risk_tolerance
            )

            # Performance attribution analysis
            performance_analysis = await self._analyze_performance(eligible_funds)

            # Risk assessment
            risk_assessment = await self._assess_risk(eligible_funds, portfolio_recommendation)

            response = {
                "status": "success",
                "query": query,
                "investor_profile": {
                    "investment_amount": investment_amount,
                    "risk_tolerance": risk_tolerance
                },
                "strategy_analysis": strategy_analysis,
                "eligible_funds": eligible_funds,
                "due_diligence": due_diligence,
                "portfolio_recommendation": portfolio_recommendation,
                "performance_analysis": performance_analysis,
                "risk_assessment": risk_assessment,
                "key_considerations": self._generate_key_considerations(eligible_funds),
                "next_steps": self._generate_next_steps(eligible_funds),
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully analyzed {len(eligible_funds)} hedge funds")
            return response

        except Exception as e:
            logger.error(f"Error in hedge fund analysis: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _analyze_strategy_suitability(
        self,
        investor_profile: Dict[str, Any],
        risk_tolerance: str
    ) -> Dict[str, Any]:
        """Analyze which hedge fund strategies are suitable"""
        suitable_strategies = []

        for strategy_name, strategy_info in self.strategies.items():
            # Risk tolerance matching
            volatility_range = strategy_info["volatility"]
            correlation_range = strategy_info["market_correlation"]

            suitability_score = 0

            # Low risk tolerance: prefer low volatility, low correlation
            if risk_tolerance == "low":
                if "4-8%" in volatility_range:
                    suitability_score += 3
                if "0.1-0.3" in correlation_range:
                    suitability_score += 2

            # Moderate risk tolerance: balanced
            elif risk_tolerance == "moderate":
                if any(x in volatility_range for x in ["6-12%", "8-15%", "8-16%"]):
                    suitability_score += 3
                suitability_score += 2

            # High risk tolerance: can handle higher volatility
            else:
                suitability_score += 2

            suitable_strategies.append({
                "strategy": strategy_name,
                "suitability_score": suitability_score,
                "info": strategy_info
            })

        # Sort by suitability score
        suitable_strategies.sort(key=lambda x: x["suitability_score"], reverse=True)

        return {
            "ranked_strategies": suitable_strategies[:3],
            "recommendation": suitable_strategies[0]["strategy"],
            "rationale": suitable_strategies[0]["info"]["best_for"]
        }

    async def _screen_funds(
        self,
        investment_amount: float,
        risk_tolerance: str,
        investor_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Screen funds based on investment criteria"""
        eligible = []

        for fund in self.hedge_funds:
            # Minimum investment check
            min_investment = fund.get("minimum_investment")
            if min_investment and investment_amount < min_investment:
                continue

            # Skip closed funds
            if fund.get("liquidity") == "Closed to external investors":
                continue

            # Risk tolerance check
            volatility = fund.get("volatility", 0)
            if risk_tolerance == "low" and volatility > 12:
                continue
            if risk_tolerance == "moderate" and volatility > 18:
                continue

            eligible.append(fund)

        # Add screening metadata
        for fund in eligible:
            fund["screening_score"] = self._calculate_screening_score(fund, risk_tolerance)

        # Sort by screening score
        eligible.sort(key=lambda x: x["screening_score"], reverse=True)

        return eligible

    def _calculate_screening_score(self, fund: Dict[str, Any], risk_tolerance: str) -> float:
        """Calculate screening score for fund"""
        score = 0

        # Sharpe ratio (higher is better)
        sharpe = fund.get("sharpe_ratio", 0)
        score += sharpe * 20

        # Lower fees better
        fees = fund.get("fees", {})
        total_fees = fees.get("management", 0) + fees.get("performance", 0) / 5
        score -= total_fees * 2

        # Track record length (older is better)
        inception = fund.get("inception_year", 2020)
        years_operating = 2024 - inception
        score += min(years_operating, 30)

        # Lower drawdown better
        max_dd = abs(fund.get("max_drawdown", 0))
        score -= max_dd / 2

        # Liquidity preference
        liquidity = fund.get("liquidity", "")
        if "Daily" in liquidity or "Monthly" in liquidity:
            score += 5

        return score

    async def _perform_due_diligence(self, funds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform due diligence on shortlisted funds"""
        diligence_summary = []

        for fund in funds[:5]:  # Top 5 funds
            red_flags = []
            green_flags = []

            # Check performance consistency
            perf = fund.get("performance", {})
            if perf.get("1_year", 0) < 0:
                red_flags.append("Negative 1-year performance")
            if perf.get("5_year", 0) > 10:
                green_flags.append("Strong 5-year track record (>10%)")

            # Check Sharpe ratio
            sharpe = fund.get("sharpe_ratio", 0)
            if sharpe > 1.5:
                green_flags.append(f"Excellent risk-adjusted returns (Sharpe: {sharpe})")
            elif sharpe < 0.5:
                red_flags.append(f"Poor risk-adjusted returns (Sharpe: {sharpe})")

            # Check fees
            fees = fund.get("fees", {})
            total_fee_rate = fees.get("management", 0) + fees.get("performance", 0) / 5
            if total_fee_rate > 5:
                red_flags.append("Above-average fee structure")
            else:
                green_flags.append("Reasonable fee structure")

            # Check correlation
            correlation = fund.get("correlation_sp500", 0)
            if correlation < 0.3:
                green_flags.append("Low correlation to equities (good diversification)")

            # Check liquidity
            liquidity = fund.get("liquidity", "")
            if "Annual" in liquidity or "90 days" in liquidity:
                red_flags.append("Limited liquidity")

            diligence_summary.append({
                "fund_name": fund["fund_name"],
                "overall_rating": len(green_flags) - len(red_flags),
                "green_flags": green_flags,
                "red_flags": red_flags,
                "recommendation": "Strong candidate" if len(green_flags) > len(red_flags) else "Proceed with caution"
            })

        return {
            "funds_reviewed": len(diligence_summary),
            "diligence_details": diligence_summary,
            "recommended_next_steps": [
                "Request full offering memorandum",
                "Review audited financial statements",
                "Conduct operational due diligence",
                "Interview portfolio managers",
                "Check references from existing investors"
            ]
        }

    async def _construct_portfolio(
        self,
        funds: List[Dict[str, Any]],
        investment_amount: float,
        risk_tolerance: str
    ) -> Dict[str, Any]:
        """Construct optimal hedge fund portfolio"""
        if not funds:
            return {"error": "No eligible funds found"}

        # Select top funds based on strategy diversification
        selected_funds = []
        strategies_used = set()

        for fund in funds:
            strategy = fund.get("strategy")
            if strategy not in strategies_used and len(selected_funds) < 4:
                selected_funds.append(fund)
                strategies_used.add(strategy)

        # Allocate capital
        allocations = []
        if len(selected_funds) == 1:
            weights = [1.0]
        elif len(selected_funds) == 2:
            weights = [0.6, 0.4]
        elif len(selected_funds) == 3:
            weights = [0.4, 0.35, 0.25]
        else:
            weights = [0.35, 0.30, 0.20, 0.15]

        for i, fund in enumerate(selected_funds):
            allocations.append({
                "fund_name": fund["fund_name"],
                "strategy": fund["strategy"],
                "allocation_pct": weights[i] * 100,
                "allocation_amount": investment_amount * weights[i],
                "expected_return": fund["performance"]["5_year"],
                "volatility": fund["volatility"]
            })

        # Calculate portfolio metrics
        portfolio_return = sum(
            alloc["allocation_pct"] / 100 * alloc["expected_return"]
            for alloc in allocations
        )
        portfolio_volatility = sum(
            alloc["allocation_pct"] / 100 * alloc["volatility"]
            for alloc in allocations
        ) * 0.8  # Diversification benefit

        return {
            "allocations": allocations,
            "portfolio_metrics": {
                "expected_return": round(portfolio_return, 2),
                "expected_volatility": round(portfolio_volatility, 2),
                "expected_sharpe": round(portfolio_return / portfolio_volatility, 2) if portfolio_volatility > 0 else 0,
                "number_of_funds": len(allocations)
            },
            "rebalancing_frequency": "Quarterly",
            "monitoring_metrics": ["NAV", "Performance attribution", "Risk metrics", "Manager changes"]
        }

    async def _analyze_performance(self, funds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance relative to benchmarks"""
        if not funds:
            return {}

        avg_performance = {
            "1_year": sum(f["performance"]["1_year"] for f in funds) / len(funds),
            "3_year": sum(f["performance"]["3_year"] for f in funds) / len(funds),
            "5_year": sum(f["performance"]["5_year"] for f in funds) / len(funds)
        }

        # Compare to benchmarks
        vs_hfri = {
            "1_year": avg_performance["1_year"] - self.benchmarks["HFRI Fund Weighted Composite"]["1_year"],
            "3_year": avg_performance["3_year"] - self.benchmarks["HFRI Fund Weighted Composite"]["3_year"],
            "5_year": avg_performance["5_year"] - self.benchmarks["HFRI Fund Weighted Composite"]["5_year"]
        }

        vs_sp500 = {
            "1_year": avg_performance["1_year"] - self.benchmarks["S&P 500"]["1_year"],
            "3_year": avg_performance["3_year"] - self.benchmarks["S&P 500"]["3_year"],
            "5_year": avg_performance["5_year"] - self.benchmarks["S&P 500"]["5_year"]
        }

        return {
            "average_performance": avg_performance,
            "vs_hfri_index": vs_hfri,
            "vs_sp500": vs_sp500,
            "interpretation": self._interpret_performance(vs_hfri, vs_sp500)
        }

    def _interpret_performance(self, vs_hfri: Dict, vs_sp500: Dict) -> str:
        """Interpret performance vs benchmarks"""
        if vs_hfri["5_year"] > 2 and vs_sp500["5_year"] > -5:
            return "Strong performers - outperforming hedge fund index with lower volatility than equities"
        elif vs_hfri["5_year"] > 0:
            return "Above-average performers relative to hedge fund universe"
        elif vs_sp500["5_year"] > 0:
            return "Underperforming hedge fund index but providing equity-like returns with lower volatility"
        else:
            return "Below-average performers - consider whether hedge fund fees are justified"

    async def _assess_risk(
        self,
        funds: List[Dict[str, Any]],
        portfolio: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess portfolio risk"""
        if not funds:
            return {}

        # Aggregate risk metrics
        avg_volatility = sum(f["volatility"] for f in funds) / len(funds)
        avg_drawdown = sum(abs(f["max_drawdown"]) for f in funds) / len(funds)
        avg_correlation = sum(f["correlation_sp500"] for f in funds) / len(funds)

        risk_factors = []

        if avg_volatility > 15:
            risk_factors.append("High portfolio volatility")
        if avg_drawdown > 20:
            risk_factors.append("Significant drawdown potential")
        if avg_correlation > 0.6:
            risk_factors.append("High correlation to equity markets")

        # Liquidity analysis
        illiquid_funds = [f for f in funds if "Annual" in f.get("liquidity", "")]
        if illiquid_funds:
            risk_factors.append(f"{len(illiquid_funds)} funds with limited liquidity")

        return {
            "portfolio_volatility": round(avg_volatility, 1),
            "expected_max_drawdown": round(avg_drawdown, 1),
            "equity_correlation": round(avg_correlation, 2),
            "risk_factors": risk_factors,
            "risk_rating": self._calculate_risk_rating(avg_volatility, avg_drawdown),
            "stress_scenarios": {
                "market_crash_2008": "-18% to -25%",
                "covid_2020": "-8% to -15%",
                "taper_tantrum_2013": "-3% to -8%"
            }
        }

    def _calculate_risk_rating(self, volatility: float, drawdown: float) -> str:
        """Calculate overall risk rating"""
        risk_score = (volatility / 2) + (drawdown / 2)

        if risk_score < 10:
            return "Low Risk"
        elif risk_score < 15:
            return "Moderate Risk"
        else:
            return "High Risk"

    def _generate_key_considerations(self, funds: List[Dict[str, Any]]) -> List[str]:
        """Generate key considerations for investors"""
        considerations = [
            "Hedge funds are suitable for sophisticated investors with high net worth",
            f"Minimum investments typically range from ${min(f.get('minimum_investment', 1000000) for f in funds if f.get('minimum_investment')):,.0f}+",
            "Lock-up periods and redemption restrictions apply",
            "Fees are typically 2% management + 20% performance",
            "Historical performance does not guarantee future results"
        ]

        # Add specific considerations based on fund characteristics
        if any(f["strategy"] == "Quantitative" for f in funds):
            considerations.append("Quantitative strategies may face model risk and require technological sophistication")

        if any(f.get("correlation_sp500", 0) < 0.3 for f in funds):
            considerations.append("Low correlation funds provide excellent portfolio diversification")

        return considerations

    def _generate_next_steps(self, funds: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable next steps"""
        if not funds:
            return [
                "Increase investment amount to meet minimum thresholds",
                "Consider hedge fund replication strategies or liquid alternatives",
                "Build net worth through traditional investments before accessing hedge funds"
            ]

        return [
            f"Request offering memoranda for top {min(3, len(funds))} funds",
            "Engage legal counsel to review subscription documents",
            "Verify accredited investor status and complete KYC",
            "Schedule calls with investor relations teams",
            "Consider fund-of-funds for diversified exposure with lower minimums",
            "Review tax implications with accountant (K-1s, UBTI for IRAs)"
        ]

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self.capabilities

    def get_fund_database_stats(self) -> Dict[str, Any]:
        """Return statistics about the fund database"""
        return {
            "total_funds": len(self.hedge_funds),
            "total_aum": sum(f["aum"] for f in self.hedge_funds),
            "strategies_covered": len(self.strategies),
            "avg_sharpe_ratio": round(sum(f["sharpe_ratio"] for f in self.hedge_funds) / len(self.hedge_funds), 2)
        }
