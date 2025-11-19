"""
Mutual Fund Analyzer Agent - Retail Investment Fund Analysis
Analyzes mutual funds, compares options, and provides investment recommendations
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import sys; import os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..")); from base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MutualFundAnalyzerAgent(BaseAgent):
    """
    Comprehensive agent for analyzing mutual funds
    Provides fund comparison, selection, and portfolio construction for retail investors
    """

    def __init__(self):
        super().__init__(
            name="Mutual Fund Analyzer Agent",
            description="Analyzes mutual funds and provides investment recommendations",
            capabilities=[
                "fund_comparison",
                "expense_ratio_analysis",
                "performance_evaluation",
                "risk_assessment",
                "asset_allocation",
                "tax_efficiency_analysis"
            ]
        )

        # Mutual fund database
        self.mutual_funds = self._initialize_fund_database()

        # Asset classes
        self.asset_classes = self._initialize_asset_classes()

        # Investment strategies
        self.strategies = self._initialize_investment_strategies()

    def _initialize_fund_database(self) -> List[Dict[str, Any]]:
        """Initialize mutual fund database"""
        return [
            {
                "ticker": "VTSAX",
                "name": "Vanguard Total Stock Market Index Fund Admiral Shares",
                "fund_family": "Vanguard",
                "category": "Large Blend",
                "asset_class": "US Equity",
                "expense_ratio": 0.04,
                "minimum_investment": 3000,
                "aum": 318000000000,  # $318B
                "inception_date": "2000-11-13",
                "performance": {
                    "ytd": 24.2,
                    "1_year": 26.3,
                    "3_year": 9.8,
                    "5_year": 15.1,
                    "10_year": 12.6,
                    "since_inception": 8.1
                },
                "risk_metrics": {
                    "std_dev": 18.2,
                    "sharpe_ratio": 0.88,
                    "beta": 1.00,
                    "alpha": 0.02,
                    "max_drawdown": -33.5
                },
                "holdings_count": 3863,
                "top_holdings": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
                "turnover_rate": 4,
                "tax_efficiency": "high",
                "morningstar_rating": 5,
                "load": None,
                "best_for": ["Long-term growth", "Core holding", "Index investors"]
            },
            {
                "ticker": "VFIAX",
                "name": "Vanguard 500 Index Fund Admiral Shares",
                "fund_family": "Vanguard",
                "category": "Large Blend",
                "asset_class": "US Equity",
                "expense_ratio": 0.04,
                "minimum_investment": 3000,
                "aum": 470000000000,  # $470B
                "inception_date": "2000-11-13",
                "performance": {
                    "ytd": 26.5,
                    "1_year": 28.3,
                    "3_year": 10.5,
                    "5_year": 15.8,
                    "10_year": 12.9,
                    "since_inception": 8.4
                },
                "risk_metrics": {
                    "std_dev": 17.9,
                    "sharpe_ratio": 0.91,
                    "beta": 1.00,
                    "alpha": 0.00,
                    "max_drawdown": -33.8
                },
                "holdings_count": 503,
                "top_holdings": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
                "turnover_rate": 3,
                "tax_efficiency": "high",
                "morningstar_rating": 5,
                "load": None,
                "best_for": ["S&P 500 exposure", "Core holding", "Simplicity"]
            },
            {
                "ticker": "VBTLX",
                "name": "Vanguard Total Bond Market Index Fund Admiral Shares",
                "fund_family": "Vanguard",
                "category": "Intermediate Core Bond",
                "asset_class": "US Fixed Income",
                "expense_ratio": 0.05,
                "minimum_investment": 3000,
                "aum": 305000000000,  # $305B
                "inception_date": "2001-12-11",
                "performance": {
                    "ytd": 3.8,
                    "1_year": 4.2,
                    "3_year": -3.1,
                    "5_year": 0.2,
                    "10_year": 1.4,
                    "since_inception": 3.9
                },
                "risk_metrics": {
                    "std_dev": 5.8,
                    "sharpe_ratio": 0.12,
                    "beta": -0.05,
                    "alpha": 0.01,
                    "max_drawdown": -13.0
                },
                "holdings_count": 11420,
                "top_holdings": ["US Treasury bonds", "Mortgage-backed securities"],
                "turnover_rate": 42,
                "tax_efficiency": "medium",
                "morningstar_rating": 4,
                "load": None,
                "best_for": ["Income", "Capital preservation", "Diversification"]
            },
            {
                "ticker": "VTIAX",
                "name": "Vanguard Total International Stock Index Fund Admiral",
                "fund_family": "Vanguard",
                "category": "Foreign Large Blend",
                "asset_class": "International Equity",
                "expense_ratio": 0.11,
                "minimum_investment": 3000,
                "aum": 92000000000,  # $92B
                "inception_date": "2010-11-29",
                "performance": {
                    "ytd": 12.8,
                    "1_year": 14.2,
                    "3_year": 2.1,
                    "5_year": 7.8,
                    "10_year": 5.2,
                    "since_inception": 6.1
                },
                "risk_metrics": {
                    "std_dev": 17.5,
                    "sharpe_ratio": 0.42,
                    "beta": 0.88,
                    "alpha": -0.51,
                    "max_drawdown": -35.2
                },
                "holdings_count": 8154,
                "top_holdings": ["Nestle", "ASML", "Samsung", "LVMH", "Novo Nordisk"],
                "turnover_rate": 5,
                "tax_efficiency": "medium",
                "morningstar_rating": 4,
                "load": None,
                "best_for": ["International diversification", "Global exposure"]
            },
            {
                "ticker": "FXAIX",
                "name": "Fidelity 500 Index Fund",
                "fund_family": "Fidelity",
                "category": "Large Blend",
                "asset_class": "US Equity",
                "expense_ratio": 0.015,
                "minimum_investment": 0,
                "aum": 536000000000,  # $536B
                "inception_date": "1988-02-17",
                "performance": {
                    "ytd": 26.4,
                    "1_year": 28.2,
                    "3_year": 10.4,
                    "5_year": 15.7,
                    "10_year": 12.8,
                    "since_inception": 10.9
                },
                "risk_metrics": {
                    "std_dev": 17.9,
                    "sharpe_ratio": 0.90,
                    "beta": 1.00,
                    "alpha": -0.01,
                    "max_drawdown": -33.9
                },
                "holdings_count": 507,
                "top_holdings": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
                "turnover_rate": 3,
                "tax_efficiency": "high",
                "morningstar_rating": 5,
                "load": None,
                "best_for": ["No minimum investment", "Ultra-low fees", "Fidelity clients"]
            },
            {
                "ticker": "PRGFX",
                "name": "T. Rowe Price Growth Stock Fund",
                "fund_family": "T. Rowe Price",
                "category": "Large Growth",
                "asset_class": "US Equity",
                "expense_ratio": 0.67,
                "minimum_investment": 2500,
                "aum": 70000000000,  # $70B
                "inception_date": "1950-04-11",
                "performance": {
                    "ytd": 32.1,
                    "1_year": 34.8,
                    "3_year": 8.2,
                    "5_year": 18.5,
                    "10_year": 14.2,
                    "since_inception": 11.4
                },
                "risk_metrics": {
                    "std_dev": 19.8,
                    "sharpe_ratio": 0.93,
                    "beta": 1.08,
                    "alpha": 1.85,
                    "max_drawdown": -36.2
                },
                "holdings_count": 103,
                "top_holdings": ["MSFT", "AMZN", "NVDA", "META", "GOOGL"],
                "turnover_rate": 25,
                "tax_efficiency": "medium",
                "morningstar_rating": 5,
                "load": None,
                "best_for": ["Active management", "Growth investors", "Long track record"]
            },
            {
                "ticker": "DODGX",
                "name": "Dodge & Cox Stock Fund",
                "fund_family": "Dodge & Cox",
                "category": "Large Value",
                "asset_class": "US Equity",
                "expense_ratio": 0.52,
                "minimum_investment": 2500,
                "aum": 91000000000,  # $91B
                "inception_date": "1965-01-04",
                "performance": {
                    "ytd": 18.5,
                    "1_year": 20.2,
                    "3_year": 11.8,
                    "5_year": 13.5,
                    "10_year": 11.2,
                    "since_inception": 11.8
                },
                "risk_metrics": {
                    "std_dev": 18.5,
                    "sharpe_ratio": 0.72,
                    "beta": 1.12,
                    "alpha": 0.82,
                    "max_drawdown": -42.1
                },
                "holdings_count": 78,
                "top_holdings": ["BRK.B", "BAC", "WFC", "GOOG", "HD"],
                "turnover_rate": 18,
                "tax_efficiency": "medium",
                "morningstar_rating": 5,
                "load": None,
                "best_for": ["Value investing", "Contrarian approach", "Patient investors"]
            },
            {
                "ticker": "VWIUX",
                "name": "Vanguard International Growth Fund Admiral",
                "fund_family": "Vanguard",
                "category": "Foreign Large Growth",
                "asset_class": "International Equity",
                "expense_ratio": 0.32,
                "minimum_investment": 50000,
                "aum": 48000000000,  # $48B
                "inception_date": "2009-12-21",
                "performance": {
                    "ytd": 18.2,
                    "1_year": 19.8,
                    "3_year": 1.5,
                    "5_year": 10.2,
                    "10_year": 7.8,
                    "since_inception": 9.1
                },
                "risk_metrics": {
                    "std_dev": 18.9,
                    "sharpe_ratio": 0.52,
                    "beta": 0.95,
                    "alpha": 1.21,
                    "max_drawdown": -38.5
                },
                "holdings_count": 342,
                "top_holdings": ["ASML", "Novo Nordisk", "LVMH", "SAP", "AstraZeneca"],
                "turnover_rate": 32,
                "tax_efficiency": "low",
                "morningstar_rating": 4,
                "load": None,
                "best_for": ["International growth", "Active management", "High net worth"]
            }
        ]

    def _initialize_asset_classes(self) -> Dict[str, Any]:
        """Initialize asset class information"""
        return {
            "US Equity": {
                "description": "Stocks of US companies",
                "typical_allocation": "40-70%",
                "risk_level": "high",
                "time_horizon": "10+ years",
                "correlation_bonds": -0.1
            },
            "International Equity": {
                "description": "Stocks of non-US companies",
                "typical_allocation": "20-40%",
                "risk_level": "high",
                "time_horizon": "10+ years",
                "correlation_bonds": -0.05
            },
            "US Fixed Income": {
                "description": "US government and corporate bonds",
                "typical_allocation": "20-40%",
                "risk_level": "low",
                "time_horizon": "3-5 years",
                "correlation_stocks": -0.1
            },
            "International Fixed Income": {
                "description": "Non-US bonds",
                "typical_allocation": "0-10%",
                "risk_level": "medium",
                "time_horizon": "3-5 years",
                "correlation_stocks": -0.05
            },
            "Real Estate": {
                "description": "REITs and real estate securities",
                "typical_allocation": "5-15%",
                "risk_level": "medium-high",
                "time_horizon": "7-10 years",
                "correlation_stocks": 0.6
            },
            "Commodities": {
                "description": "Gold, oil, agricultural products",
                "typical_allocation": "0-10%",
                "risk_level": "high",
                "time_horizon": "5+ years",
                "correlation_stocks": 0.2
            }
        }

    def _initialize_investment_strategies(self) -> Dict[str, Any]:
        """Initialize investment strategies"""
        return {
            "Three-Fund Portfolio": {
                "description": "Simple, diversified portfolio with three funds",
                "allocation": {
                    "US Equity": 60,
                    "International Equity": 20,
                    "US Fixed Income": 20
                },
                "rebalancing": "Annual",
                "complexity": "low",
                "best_for": "Simplicity, low maintenance"
            },
            "Age-Based Allocation": {
                "description": "Bond allocation = your age (e.g., 30 years old = 30% bonds)",
                "formula": "bonds_percent = age",
                "rebalancing": "Annual",
                "complexity": "low",
                "best_for": "Automatic risk reduction over time"
            },
            "60/40 Portfolio": {
                "description": "Classic balanced portfolio",
                "allocation": {
                    "US Equity": 60,
                    "US Fixed Income": 40
                },
                "rebalancing": "Quarterly",
                "complexity": "low",
                "best_for": "Balanced risk/return"
            },
            "All-Weather Portfolio": {
                "description": "Ray Dalio's risk parity approach",
                "allocation": {
                    "US Equity": 30,
                    "Long-term Bonds": 40,
                    "Intermediate Bonds": 15,
                    "Commodities": 7.5,
                    "Gold": 7.5
                },
                "rebalancing": "Quarterly",
                "complexity": "medium",
                "best_for": "All market conditions"
            },
            "Aggressive Growth": {
                "description": "Maximum growth potential",
                "allocation": {
                    "US Equity": 70,
                    "International Equity": 30
                },
                "rebalancing": "Annual",
                "complexity": "low",
                "best_for": "Young investors, high risk tolerance"
            }
        }

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process mutual fund analysis request

        Args:
            query: User query about mutual funds
            context: Additional context (investor profile, goals, etc.)

        Returns:
            Dict with fund analysis, comparisons, and recommendations
        """
        try:
            logger.info(f"Processing mutual fund analysis query: {query[:100]}...")

            # Extract investor profile from context
            age = context.get("age", 35) if context else 35
            risk_tolerance = context.get("risk_tolerance", "moderate") if context else "moderate"
            time_horizon = context.get("time_horizon", 10) if context else 10
            investment_amount = context.get("investment_amount", 10000) if context else 10000
            goal = context.get("goal", "retirement") if context else "retirement"

            # Analyze investor profile
            investor_analysis = await self._analyze_investor_profile(
                age, risk_tolerance, time_horizon, goal
            )

            # Screen funds based on criteria
            eligible_funds = await self._screen_funds(
                investment_amount, risk_tolerance, investor_analysis
            )

            # Compare top funds
            fund_comparison = await self._compare_funds(eligible_funds[:5])

            # Generate portfolio recommendation
            portfolio_recommendation = await self._generate_portfolio(
                investor_analysis, eligible_funds, investment_amount
            )

            # Analyze costs and tax efficiency
            cost_analysis = await self._analyze_costs(portfolio_recommendation)

            # Generate monitoring plan
            monitoring_plan = await self._generate_monitoring_plan(portfolio_recommendation)

            response = {
                "status": "success",
                "query": query,
                "investor_profile": investor_analysis,
                "eligible_funds": eligible_funds,
                "fund_comparison": fund_comparison,
                "portfolio_recommendation": portfolio_recommendation,
                "cost_analysis": cost_analysis,
                "monitoring_plan": monitoring_plan,
                "key_insights": self._generate_key_insights(portfolio_recommendation),
                "next_steps": self._generate_next_steps(portfolio_recommendation),
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully analyzed {len(eligible_funds)} mutual funds")
            return response

        except Exception as e:
            logger.error(f"Error in mutual fund analysis: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _analyze_investor_profile(
        self,
        age: int,
        risk_tolerance: str,
        time_horizon: int,
        goal: str
    ) -> Dict[str, Any]:
        """Analyze investor profile and determine suitable strategy"""
        # Calculate suggested bond allocation
        if risk_tolerance == "low":
            suggested_bond_allocation = min(age + 10, 70)
        elif risk_tolerance == "moderate":
            suggested_bond_allocation = age
        else:  # high
            suggested_bond_allocation = max(age - 10, 10)

        suggested_equity_allocation = 100 - suggested_bond_allocation

        # Determine strategy
        if time_horizon < 5:
            strategy = "Conservative"
        elif time_horizon < 10:
            strategy = "Moderate"
        else:
            strategy = "Aggressive Growth" if risk_tolerance == "high" else "Balanced"

        return {
            "age": age,
            "risk_tolerance": risk_tolerance,
            "time_horizon": time_horizon,
            "goal": goal,
            "suggested_equity_allocation": suggested_equity_allocation,
            "suggested_bond_allocation": suggested_bond_allocation,
            "recommended_strategy": strategy,
            "rebalancing_frequency": "Annual" if time_horizon > 10 else "Quarterly"
        }

    async def _screen_funds(
        self,
        investment_amount: float,
        risk_tolerance: str,
        investor_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Screen funds based on criteria"""
        eligible = []

        equity_allocation = investor_analysis["suggested_equity_allocation"]

        for fund in self.mutual_funds:
            # Minimum investment check
            if investment_amount < fund.get("minimum_investment", 0):
                continue

            # Risk tolerance check
            if risk_tolerance == "low" and fund["asset_class"] in ["US Equity", "International Equity"]:
                continue

            eligible.append(fund)

        # Add screening score
        for fund in eligible:
            fund["screening_score"] = self._calculate_fund_score(fund)

        # Sort by score
        eligible.sort(key=lambda x: x["screening_score"], reverse=True)

        return eligible

    def _calculate_fund_score(self, fund: Dict[str, Any]) -> float:
        """Calculate overall fund score"""
        score = 0

        # Low expense ratio is good (higher weight for passive funds)
        expense_ratio = fund.get("expense_ratio", 1.0)
        score += max(0, (1.0 - expense_ratio) * 20)

        # Performance (5-year returns)
        perf_5y = fund["performance"].get("5_year", 0)
        score += perf_5y

        # Sharpe ratio
        sharpe = fund["risk_metrics"].get("sharpe_ratio", 0)
        score += sharpe * 10

        # Morningstar rating
        rating = fund.get("morningstar_rating", 3)
        score += rating * 3

        # Tax efficiency
        tax_eff = fund.get("tax_efficiency", "medium")
        if tax_eff == "high":
            score += 5
        elif tax_eff == "medium":
            score += 2

        # AUM (larger is generally better for stability)
        aum = fund.get("aum", 0)
        if aum > 50_000_000_000:  # > $50B
            score += 5

        return score

    async def _compare_funds(self, funds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare funds side-by-side"""
        if not funds:
            return {}

        comparison = {
            "funds": [],
            "winner": {
                "lowest_expense_ratio": None,
                "best_5y_performance": None,
                "best_sharpe_ratio": None,
                "highest_tax_efficiency": None
            }
        }

        lowest_er = float('inf')
        best_5y = float('-inf')
        best_sharpe = float('-inf')

        for fund in funds:
            comparison["funds"].append({
                "ticker": fund["ticker"],
                "name": fund["name"],
                "expense_ratio": fund["expense_ratio"],
                "5y_return": fund["performance"]["5_year"],
                "sharpe_ratio": fund["risk_metrics"]["sharpe_ratio"],
                "morningstar_rating": fund["morningstar_rating"],
                "min_investment": fund["minimum_investment"]
            })

            # Track winners
            if fund["expense_ratio"] < lowest_er:
                lowest_er = fund["expense_ratio"]
                comparison["winner"]["lowest_expense_ratio"] = fund["ticker"]

            if fund["performance"]["5_year"] > best_5y:
                best_5y = fund["performance"]["5_year"]
                comparison["winner"]["best_5y_performance"] = fund["ticker"]

            if fund["risk_metrics"]["sharpe_ratio"] > best_sharpe:
                best_sharpe = fund["risk_metrics"]["sharpe_ratio"]
                comparison["winner"]["best_sharpe_ratio"] = fund["ticker"]

        return comparison

    async def _generate_portfolio(
        self,
        investor_analysis: Dict[str, Any],
        funds: List[Dict[str, Any]],
        investment_amount: float
    ) -> Dict[str, Any]:
        """Generate portfolio recommendation"""
        equity_pct = investor_analysis["suggested_equity_allocation"]
        bond_pct = investor_analysis["suggested_bond_allocation"]

        # Select best funds by category
        us_equity_fund = next((f for f in funds if f["asset_class"] == "US Equity"), None)
        intl_equity_fund = next((f for f in funds if f["asset_class"] == "International Equity"), None)
        bond_fund = next((f for f in funds if f["asset_class"] == "US Fixed Income"), None)

        allocations = []

        if us_equity_fund:
            us_allocation = equity_pct * 0.7 / 100  # 70% of equity allocation
            allocations.append({
                "ticker": us_equity_fund["ticker"],
                "name": us_equity_fund["name"],
                "asset_class": "US Equity",
                "allocation_pct": us_allocation * 100,
                "allocation_amount": investment_amount * us_allocation,
                "expense_ratio": us_equity_fund["expense_ratio"]
            })

        if intl_equity_fund and equity_pct > 20:
            intl_allocation = equity_pct * 0.3 / 100  # 30% of equity allocation
            allocations.append({
                "ticker": intl_equity_fund["ticker"],
                "name": intl_equity_fund["name"],
                "asset_class": "International Equity",
                "allocation_pct": intl_allocation * 100,
                "allocation_amount": investment_amount * intl_allocation,
                "expense_ratio": intl_equity_fund["expense_ratio"]
            })

        if bond_fund:
            bond_allocation = bond_pct / 100
            allocations.append({
                "ticker": bond_fund["ticker"],
                "name": bond_fund["name"],
                "asset_class": "US Fixed Income",
                "allocation_pct": bond_allocation * 100,
                "allocation_amount": investment_amount * bond_allocation,
                "expense_ratio": bond_fund["expense_ratio"]
            })

        # Calculate portfolio metrics
        weighted_expense_ratio = sum(
            alloc["allocation_pct"] / 100 * alloc["expense_ratio"]
            for alloc in allocations
        )

        return {
            "strategy": investor_analysis["recommended_strategy"],
            "allocations": allocations,
            "portfolio_metrics": {
                "total_funds": len(allocations),
                "weighted_expense_ratio": round(weighted_expense_ratio, 3),
                "equity_allocation": equity_pct,
                "bond_allocation": bond_pct,
                "expected_return": self._estimate_portfolio_return(allocations),
                "expected_volatility": self._estimate_portfolio_volatility(allocations)
            },
            "rebalancing_strategy": {
                "frequency": investor_analysis["rebalancing_frequency"],
                "threshold": "5% deviation from target",
                "tax_consideration": "Rebalance in tax-advantaged accounts first"
            }
        }

    def _estimate_portfolio_return(self, allocations: List[Dict[str, Any]]) -> float:
        """Estimate portfolio expected return"""
        # Use historical 5-year returns as proxy
        weighted_return = 0
        for alloc in allocations:
            # Get fund details
            fund = next((f for f in self.mutual_funds if f["ticker"] == alloc["ticker"]), None)
            if fund:
                weight = alloc["allocation_pct"] / 100
                return_5y = fund["performance"]["5_year"]
                weighted_return += weight * return_5y

        return round(weighted_return, 2)

    def _estimate_portfolio_volatility(self, allocations: List[Dict[str, Any]]) -> float:
        """Estimate portfolio volatility"""
        weighted_vol = 0
        for alloc in allocations:
            fund = next((f for f in self.mutual_funds if f["ticker"] == alloc["ticker"]), None)
            if fund:
                weight = alloc["allocation_pct"] / 100
                std_dev = fund["risk_metrics"]["std_dev"]
                weighted_vol += weight * std_dev

        # Adjust for diversification benefit
        return round(weighted_vol * 0.85, 2)

    async def _analyze_costs(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze portfolio costs"""
        allocations = portfolio.get("allocations", [])
        total_amount = sum(alloc["allocation_amount"] for alloc in allocations)

        annual_fee = sum(
            alloc["allocation_amount"] * alloc["expense_ratio"] / 100
            for alloc in allocations
        )

        # Calculate cost over time
        cost_10y = annual_fee * 10
        cost_20y = annual_fee * 20
        cost_30y = annual_fee * 30

        return {
            "weighted_expense_ratio": portfolio["portfolio_metrics"]["weighted_expense_ratio"],
            "annual_cost": round(annual_fee, 2),
            "cost_projections": {
                "10_years": round(cost_10y, 2),
                "20_years": round(cost_20y, 2),
                "30_years": round(cost_30y, 2)
            },
            "cost_comparison": "Your portfolio costs are in the bottom 10% (excellent) - index funds save ~1% annually vs active funds",
            "tax_efficiency": "High - index funds generate minimal capital gains"
        }

    async def _generate_monitoring_plan(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """Generate portfolio monitoring plan"""
        return {
            "review_frequency": "Quarterly",
            "rebalancing_frequency": portfolio["rebalancing_strategy"]["frequency"],
            "metrics_to_track": [
                "Total portfolio value",
                "Current allocation vs target",
                "YTD returns",
                "Expense ratio changes",
                "Tax implications"
            ],
            "alerts": [
                "Allocation drift > 5% from target",
                "Expense ratio increases",
                "Fund manager changes",
                "Strategy changes"
            ],
            "annual_review_checklist": [
                "Review investment goals and time horizon",
                "Assess risk tolerance (life changes?)",
                "Check fund performance vs benchmarks",
                "Consider tax-loss harvesting opportunities",
                "Update beneficiaries if needed"
            ]
        }

    def _generate_key_insights(self, portfolio: Dict[str, Any]) -> List[str]:
        """Generate key insights"""
        insights = []

        expense_ratio = portfolio["portfolio_metrics"]["weighted_expense_ratio"]
        if expense_ratio < 0.1:
            insights.append("Excellent cost efficiency - your expense ratio is ultra-low")

        equity_pct = portfolio["portfolio_metrics"]["equity_allocation"]
        if equity_pct > 80:
            insights.append("Aggressive portfolio - suitable for long time horizons (10+ years)")
        elif equity_pct < 40:
            insights.append("Conservative portfolio - focus on capital preservation")
        else:
            insights.append("Balanced portfolio - reasonable risk/return profile")

        num_funds = portfolio["portfolio_metrics"]["total_funds"]
        if num_funds <= 3:
            insights.append("Simple portfolio - easy to manage and monitor")

        return insights

    def _generate_next_steps(self, portfolio: Dict[str, Any]) -> List[str]:
        """Generate actionable next steps"""
        steps = []

        allocations = portfolio.get("allocations", [])

        steps.append(f"Open account with {allocations[0]['name'].split()[0]} or a brokerage that offers these funds")
        steps.append("Set up automatic monthly investments to dollar-cost average")
        steps.append(f"Set calendar reminder for {portfolio['rebalancing_strategy']['frequency'].lower()} rebalancing")
        steps.append("Consider tax-advantaged accounts (401k, IRA) first")
        steps.append("Ensure emergency fund (3-6 months expenses) before investing")

        return steps

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self.capabilities

    def get_fund_database_stats(self) -> Dict[str, Any]:
        """Return statistics about the fund database"""
        return {
            "total_funds": len(self.mutual_funds),
            "asset_classes": len(self.asset_classes),
            "investment_strategies": len(self.strategies),
            "avg_expense_ratio": round(sum(f["expense_ratio"] for f in self.mutual_funds) / len(self.mutual_funds), 3)
        }
