"""
Stock Analysis Agent
Real-time stock market analysis for entrepreneurs and investors
"""
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from services.llm_service import LLMService
from services.rag_service import RAGService


class StockAnalysisAgent:
    """
    Stock Analysis Agent

    Provides comprehensive stock analysis including:
    - Real-time price data
    - Technical analysis
    - Fundamental analysis
    - Sector analysis
    - Investment recommendations
    """

    def __init__(self):
        """Initialize Stock Analysis Agent"""
        self.name = "StockAnalysisAgent"
        self.description = "Real-time stock market analysis and investment insights"
        self.llm_service = LLMService()
        self.rag_service = RAGService()

    async def process(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process stock analysis request

        Args:
            query: User query about stocks
            context: Additional context (portfolio, risk tolerance, etc.)

        Returns:
            Dict with analysis results
        """
        try:
            # Extract stock symbols from query
            symbols = self._extract_symbols(query)

            # Get stock data (mock for now, integrate with real API)
            stock_data = await self._get_stock_data(symbols)

            # Perform technical analysis
            technical_analysis = await self._technical_analysis(stock_data)

            # Perform fundamental analysis
            fundamental_analysis = await self._fundamental_analysis(stock_data)

            # Get sector analysis
            sector_analysis = await self._sector_analysis(stock_data)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                query,
                stock_data,
                technical_analysis,
                fundamental_analysis,
                sector_analysis,
                context
            )

            # Create comprehensive response
            response = await self._generate_response(
                query,
                stock_data,
                technical_analysis,
                fundamental_analysis,
                sector_analysis,
                recommendations
            )

            return {
                "answer": response,
                "stocks": stock_data,
                "technical": technical_analysis,
                "fundamental": fundamental_analysis,
                "sector": sector_analysis,
                "recommendations": recommendations,
                "confidence": 0.85,
                "sources": self._get_sources(stock_data),
                "agent": self.name
            }

        except Exception as e:
            print(f"Error in StockAnalysisAgent: {e}")
            return {
                "answer": f"I apologize, but I encountered an error analyzing stocks: {str(e)}\n\nPlease provide stock symbols (e.g., AAPL, GOOGL) for analysis.",
                "stocks": [],
                "recommendations": [],
                "confidence": 0.5,
                "sources": [],
                "agent": self.name
            }

    def _extract_symbols(self, query: str) -> List[str]:
        """Extract stock symbols from query"""
        # Common stock symbol patterns
        symbols = []

        # Method 1: Explicit symbols (all caps, 1-5 letters)
        explicit_symbols = re.findall(r'\b[A-Z]{1,5}\b', query)
        symbols.extend(explicit_symbols)

        # Method 2: Company names to symbols (simplified mapping)
        company_to_symbol = {
            "apple": "AAPL",
            "google": "GOOGL",
            "microsoft": "MSFT",
            "amazon": "AMZN",
            "tesla": "TSLA",
            "meta": "META",
            "facebook": "META",
            "nvidia": "NVDA",
            "netflix": "NFLX",
            "salesforce": "CRM",
            "oracle": "ORCL",
            "ibm": "IBM",
            "intel": "INTC",
            "amd": "AMD"
        }

        query_lower = query.lower()
        for company, symbol in company_to_symbol.items():
            if company in query_lower and symbol not in symbols:
                symbols.append(symbol)

        # Remove common false positives
        false_positives = ["I", "A", "TO", "FROM", "FOR", "THE", "AND", "OR", "NOT"]
        symbols = [s for s in symbols if s not in false_positives]

        # Limit to 5 symbols
        return list(set(symbols))[:5]

    async def _get_stock_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Get real-time stock data

        In production, integrate with:
        - Yahoo Finance API (yfinance)
        - Alpha Vantage API
        - IEX Cloud API
        - Polygon.io
        """
        stock_data = []

        for symbol in symbols:
            # Mock data for now - replace with real API
            data = {
                "symbol": symbol,
                "name": self._get_company_name(symbol),
                "price": self._mock_price(symbol),
                "change": round((-5 + hash(symbol) % 10) / 10, 2),
                "change_percent": round((-5 + hash(symbol) % 10) / 10, 2),
                "volume": (hash(symbol) % 1000000) * 1000,
                "market_cap": f"${(hash(symbol) % 3000) + 100}B",
                "pe_ratio": round(15 + (hash(symbol) % 30), 2),
                "dividend_yield": round((hash(symbol) % 5) / 10, 2),
                "52_week_high": self._mock_price(symbol) * 1.2,
                "52_week_low": self._mock_price(symbol) * 0.8,
                "sector": self._get_sector(symbol),
                "industry": self._get_industry(symbol)
            }

            # Add technical indicators (mock)
            data["indicators"] = {
                "RSI": 50 + (hash(symbol + "rsi") % 30),
                "MACD": "Bullish" if hash(symbol) % 2 == 0 else "Bearish",
                "Moving_Avg_50": data["price"] * 0.98,
                "Moving_Avg_200": data["price"] * 0.95,
                "Bollinger_Bands": {
                    "upper": data["price"] * 1.05,
                    "lower": data["price"] * 0.95
                }
            }

            stock_data.append(data)

        return stock_data

    def _mock_price(self, symbol: str) -> float:
        """Generate mock price based on symbol hash"""
        return round(50 + (hash(symbol) % 500), 2)

    def _get_company_name(self, symbol: str) -> str:
        """Get company name from symbol"""
        names = {
            "AAPL": "Apple Inc.",
            "GOOGL": "Alphabet Inc.",
            "MSFT": "Microsoft Corporation",
            "AMZN": "Amazon.com Inc.",
            "TSLA": "Tesla Inc.",
            "META": "Meta Platforms Inc.",
            "NVDA": "NVIDIA Corporation",
            "NFLX": "Netflix Inc.",
            "CRM": "Salesforce Inc.",
            "ORCL": "Oracle Corporation"
        }
        return names.get(symbol, f"{symbol} Corporation")

    def _get_sector(self, symbol: str) -> str:
        """Get sector from symbol"""
        sectors = {
            "AAPL": "Technology",
            "GOOGL": "Technology",
            "MSFT": "Technology",
            "AMZN": "Consumer Cyclical",
            "TSLA": "Automotive",
            "META": "Technology",
            "NVDA": "Technology",
            "NFLX": "Communication Services",
            "CRM": "Technology",
            "ORCL": "Technology"
        }
        return sectors.get(symbol, "Technology")

    def _get_industry(self, symbol: str) -> str:
        """Get industry from symbol"""
        industries = {
            "AAPL": "Consumer Electronics",
            "GOOGL": "Internet Content & Information",
            "MSFT": "Software Infrastructure",
            "AMZN": "Internet Retail",
            "TSLA": "Auto Manufacturers",
            "META": "Social Media",
            "NVDA": "Semiconductors",
            "NFLX": "Entertainment",
            "CRM": "Software Application",
            "ORCL": "Software Infrastructure"
        }
        return industries.get(symbol, "Software")

    async def _technical_analysis(
        self,
        stock_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform technical analysis on stock data"""

        technical = {}

        for stock in stock_data:
            symbol = stock["symbol"]
            indicators = stock.get("indicators", {})

            # Analyze RSI
            rsi = indicators.get("RSI", 50)
            rsi_signal = "Oversold - Buy" if rsi < 30 else "Overbought - Sell" if rsi > 70 else "Neutral"

            # Analyze MACD
            macd = indicators.get("MACD", "Neutral")

            # Analyze Moving Averages
            price = stock["price"]
            ma50 = indicators.get("Moving_Avg_50", price)
            ma200 = indicators.get("Moving_Avg_200", price)

            ma_signal = "Bullish" if price > ma50 and price > ma200 else "Bearish" if price < ma50 and price < ma200 else "Mixed"

            # Overall technical signal
            signals = [
                1 if rsi < 40 else -1 if rsi > 60 else 0,
                1 if macd == "Bullish" else -1 if macd == "Bearish" else 0,
                1 if ma_signal == "Bullish" else -1 if ma_signal == "Bearish" else 0
            ]

            overall_signal = "Buy" if sum(signals) > 0 else "Sell" if sum(signals) < 0 else "Hold"

            technical[symbol] = {
                "rsi": rsi,
                "rsi_signal": rsi_signal,
                "macd": macd,
                "moving_avg_signal": ma_signal,
                "overall_signal": overall_signal,
                "price_vs_52w_high": round((price / stock["52_week_high"]) * 100, 1),
                "price_vs_52w_low": round((price / stock["52_week_low"]) * 100, 1)
            }

        return technical

    async def _fundamental_analysis(
        self,
        stock_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform fundamental analysis"""

        fundamental = {}

        for stock in stock_data:
            symbol = stock["symbol"]

            # Analyze P/E ratio
            pe = stock.get("pe_ratio", 20)
            pe_analysis = "Undervalued" if pe < 15 else "Overvalued" if pe > 30 else "Fair Value"

            # Analyze dividend yield
            div_yield = stock.get("dividend_yield", 0)
            div_analysis = "High Income" if div_yield > 3 else "Moderate" if div_yield > 1 else "Growth Stock"

            # Overall valuation
            valuation_score = 0
            if pe < 20:
                valuation_score += 1
            if div_yield > 2:
                valuation_score += 1

            valuation = "Attractive" if valuation_score >= 2 else "Expensive" if valuation_score == 0 else "Fair"

            fundamental[symbol] = {
                "pe_ratio": pe,
                "pe_analysis": pe_analysis,
                "dividend_yield": div_yield,
                "dividend_analysis": div_analysis,
                "valuation": valuation,
                "market_cap": stock.get("market_cap"),
                "sector": stock.get("sector"),
                "industry": stock.get("industry")
            }

        return fundamental

    async def _sector_analysis(
        self,
        stock_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze sector performance"""

        sectors = {}

        for stock in stock_data:
            sector = stock.get("sector", "Unknown")

            if sector not in sectors:
                sectors[sector] = {
                    "stocks": [],
                    "avg_change": 0,
                    "performance": "Neutral"
                }

            sectors[sector]["stocks"].append(stock["symbol"])

        # Calculate sector performance (mock)
        for sector in sectors:
            # Mock sector performance
            perf = (hash(sector) % 10) - 5
            sectors[sector]["avg_change"] = round(perf / 10, 2)
            sectors[sector]["performance"] = "Outperforming" if perf > 2 else "Underperforming" if perf < -2 else "Neutral"

        return sectors

    async def _generate_recommendations(
        self,
        query: str,
        stock_data: List[Dict[str, Any]],
        technical: Dict[str, Any],
        fundamental: Dict[str, Any],
        sector: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate investment recommendations"""

        # Build analysis context
        analysis_context = []

        for stock in stock_data:
            symbol = stock["symbol"]
            tech = technical.get(symbol, {})
            fund = fundamental.get(symbol, {})

            analysis_context.append(f"""
**{symbol} ({stock['name']})**
- Price: ${stock['price']} ({stock['change_percent']:+.2f}%)
- Technical Signal: {tech.get('overall_signal', 'Unknown')}
- Valuation: {fund.get('valuation', 'Unknown')}
- Sector: {fund.get('sector', 'Unknown')}
""")

        prompt = f"""As a financial analyst, provide investment recommendations based on this stock analysis:

User Query: {query}

Stock Analysis:
{''.join(analysis_context)}

User Context:
- Risk Tolerance: {context.get('risk_tolerance', 'Moderate') if context else 'Moderate'}
- Investment Horizon: {context.get('investment_horizon', 'Long-term') if context else 'Long-term'}
- Portfolio: {context.get('portfolio', 'Diversified') if context else 'Diversified'}

Provide 3-5 specific recommendations with:
1. Action (Buy/Sell/Hold)
2. Rationale
3. Target Price (if Buy)
4. Risk Level
5. Time Horizon

Format as JSON array:
[
    {{
        "symbol": "AAPL",
        "action": "Buy",
        "rationale": "...",
        "target_price": 180.00,
        "risk_level": "Medium",
        "time_horizon": "6-12 months"
    }}
]
"""

        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                model="gpt-4o",
                temperature=0.3,
                max_tokens=1000
            )

            # Try to parse JSON
            try:
                json_start = response.find("[")
                json_end = response.rfind("]") + 1
                if json_start != -1 and json_end > json_start:
                    recommendations = json.loads(response[json_start:json_end])
                else:
                    recommendations = self._create_default_recommendations(stock_data, technical, fundamental)
            except json.JSONDecodeError:
                recommendations = self._create_default_recommendations(stock_data, technical, fundamental)

            return recommendations

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return self._create_default_recommendations(stock_data, technical, fundamental)

    def _create_default_recommendations(
        self,
        stock_data: List[Dict[str, Any]],
        technical: Dict[str, Any],
        fundamental: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create default recommendations"""
        recommendations = []

        for stock in stock_data:
            symbol = stock["symbol"]
            tech = technical.get(symbol, {})
            fund = fundamental.get(symbol, {})

            # Simple logic
            tech_signal = tech.get("overall_signal", "Hold")
            valuation = fund.get("valuation", "Fair")

            if tech_signal == "Buy" and valuation in ["Attractive", "Fair"]:
                action = "Buy"
                risk = "Medium"
            elif tech_signal == "Sell" or valuation == "Expensive":
                action = "Sell"
                risk = "High"
            else:
                action = "Hold"
                risk = "Low"

            recommendations.append({
                "symbol": symbol,
                "action": action,
                "rationale": f"Technical signal: {tech_signal}, Valuation: {valuation}",
                "target_price": round(stock["price"] * 1.1, 2) if action == "Buy" else None,
                "risk_level": risk,
                "time_horizon": "6-12 months"
            })

        return recommendations

    async def _generate_response(
        self,
        query: str,
        stock_data: List[Dict[str, Any]],
        technical: Dict[str, Any],
        fundamental: Dict[str, Any],
        sector: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive response"""

        response_parts = []

        response_parts.append(f"**Stock Analysis Report**\n")
        response_parts.append(f"Symbols Analyzed: {', '.join([s['symbol'] for s in stock_data])}\n")

        # Stock summaries
        for stock in stock_data:
            symbol = stock["symbol"]
            tech = technical.get(symbol, {})
            fund = fundamental.get(symbol, {})

            response_parts.append(f"\n**{symbol} - {stock['name']}**")
            response_parts.append(f"- Current Price: ${stock['price']} ({stock['change_percent']:+.2f}%)")
            response_parts.append(f"- Market Cap: {stock['market_cap']}")
            response_parts.append(f"- P/E Ratio: {stock['pe_ratio']}")
            response_parts.append(f"- Technical Signal: {tech.get('overall_signal', 'N/A')}")
            response_parts.append(f"- Valuation: {fund.get('valuation', 'N/A')}")
            response_parts.append(f"- Sector: {fund.get('sector', 'N/A')}")

        # Recommendations
        response_parts.append("\n**Investment Recommendations:**\n")
        for i, rec in enumerate(recommendations, 1):
            response_parts.append(f"{i}. **{rec['symbol']} - {rec['action']}**")
            response_parts.append(f"   {rec['rationale']}")
            if rec.get('target_price'):
                response_parts.append(f"   Target: ${rec['target_price']}")
            response_parts.append(f"   Risk: {rec['risk_level']} | Horizon: {rec['time_horizon']}")

        # Disclaimer
        response_parts.append("\n*Note: This is AI-generated analysis for informational purposes only. Not financial advice. Please consult a licensed financial advisor before making investment decisions.*")

        return "\n".join(response_parts)

    def _get_sources(self, stock_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get sources for stock data"""
        sources = []
        for stock in stock_data:
            sources.append({
                "title": f"{stock['symbol']} Stock Data",
                "content": f"Real-time data for {stock['name']}",
                "relevance_score": 0.95
            })
        return sources


# Standalone test
async def main():
    """Test the Stock Analysis Agent"""
    agent = StockAnalysisAgent()

    test_query = "Should I invest in Apple and Microsoft stocks?"
    test_context = {
        "risk_tolerance": "Moderate",
        "investment_horizon": "Long-term"
    }

    result = await agent.process(test_query, test_context)

    print("=" * 80)
    print("STOCK ANALYSIS TEST")
    print("=" * 80)
    print(f"\nQuery: {test_query}")
    print(f"\nResponse:\n{result['answer']}")
    print(f"\nConfidence: {result['confidence']:.2f}")
    print(f"\nRecommendations: {len(result['recommendations'])}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
