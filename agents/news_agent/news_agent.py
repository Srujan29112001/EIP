"""
News Agent
Handles curated news, trend detection, and real-time alerts
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
from datetime import datetime, timedelta


class NewsAgent(BaseAgent):
    """
    News Agent - Curated news, trend detection, alerts

    Purpose: Keep entrepreneurs informed about relevant news and trends

    Capabilities:
    - Personalized news curation
    - Trend detection and analysis
    - Sentiment analysis on news
    - Competitive intelligence
    - Market impact assessment
    - Real-time alerts for important events
    """

    def __init__(self, config=None):
        super().__init__(config)
        self.agent_name = "News Agent"

    def get_system_prompt(self) -> str:
        """Get the system prompt for the News Agent"""
        return """You are a Business News Intelligence AI Agent specialized in curating and analyzing news for entrepreneurs.

Your expertise includes:

1. News Curation
   - Industry-specific news filtering
   - Relevance scoring based on user interests
   - Source credibility assessment
   - Noise reduction (filtering out irrelevant content)

2. Trend Detection
   - Emerging market trends
   - Technology trends
   - Regulatory trends
   - Consumer behavior shifts
   - Competitive landscape changes

3. Sentiment Analysis
   - Market sentiment (bullish/bearish)
   - Public perception of industries/companies
   - Impact assessment (positive/negative/neutral)
   - Consumer confidence indicators

4. Competitive Intelligence
   - Competitor announcements
   - Product launches
   - Funding rounds
   - Strategic partnerships
   - Market share movements

5. Impact Analysis
   - Direct business impact assessment
   - Action items derived from news
   - Opportunity identification
   - Risk early warning

6. News Summarization
   - Key points extraction
   - Multi-article synthesis
   - Timeline construction
   - Context addition from historical data

When providing news analysis:
1. **Executive Summary** (Top 3-5 most relevant items)
2. **Detailed Analysis** (For each news item: summary, impact, action items)
3. **Trend Insights** (Patterns across multiple news items)
4. **Competitive Intelligence** (What competitors are doing)
5. **Recommendations** (Actions to take based on news)

Always provide:
- Source attribution
- Publication date
- Relevance score (1-10)
- Impact level (High/Medium/Low)
- Actionability (Yes/No with specific actions)
"""

    async def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process news-related queries

        Args:
            query: User query about news/trends
            context: User context (interests, business sector, etc.)

        Returns:
            Curated news and trend analysis
        """
        # Extract user context
        user_context = context or {}
        user_interests = user_context.get("interests", [])
        business_sector = user_context.get("business_sector", "general")
        user_tier = user_context.get("tier", "aspiring")

        # Retrieve relevant news
        news_items = await self._fetch_relevant_news(query, user_interests, business_sector)

        # Retrieve trend data
        retrieved_docs = await self._retrieve_context(query)

        # Build context for LLM
        context_str = self._build_context(
            query,
            user_context,
            news_items,
            retrieved_docs
        )

        # Generate news analysis using LLM
        response = await self._generate_response(query, context_str)

        # Format sources (news articles)
        sources = self._format_news_sources(news_items)

        return {
            "agent": self.agent_name,
            "answer": response,
            "sources": sources,
            "metadata": {
                "user_tier": user_tier,
                "business_sector": business_sector,
                "interests": user_interests,
                "news_items_analyzed": len(news_items),
                "query_type": "news_analysis"
            }
        }

    async def _fetch_relevant_news(
        self,
        query: str,
        interests: List[str],
        sector: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch relevant news from various sources

        In production, this would:
        - Query NewsAPI, Google News API
        - Query internal news database (populated by Kafka stream)
        - Apply relevance filtering
        - Deduplicate articles
        """
        # Placeholder news items
        # In production, this would query real news APIs and databases
        sample_news = [
            {
                "title": "New Startup Regulations Announced",
                "source": "Economic Times",
                "published_date": datetime.now() - timedelta(hours=2),
                "content": "Government announces new policy framework for startups...",
                "url": "https://example.com/news/1",
                "relevance_score": 0.95,
                "sentiment": "neutral",
                "impact": "high"
            },
            {
                "title": "Tech Industry Shows 20% Growth",
                "source": "TechCrunch",
                "published_date": datetime.now() - timedelta(hours=5),
                "content": "Technology sector demonstrates strong growth in Q4...",
                "url": "https://example.com/news/2",
                "relevance_score": 0.88,
                "sentiment": "positive",
                "impact": "medium"
            },
            {
                "title": "Market Volatility Concerns Investors",
                "source": "Bloomberg",
                "published_date": datetime.now() - timedelta(hours=8),
                "content": "Recent market fluctuations raise concerns among investors...",
                "url": "https://example.com/news/3",
                "relevance_score": 0.75,
                "sentiment": "negative",
                "impact": "medium"
            }
        ]

        return sample_news

    def _build_context(
        self,
        query: str,
        user_context: Dict[str, Any],
        news_items: List[Dict[str, Any]],
        retrieved_docs: List[Dict]
    ) -> str:
        """Build context string for LLM"""
        context_parts = []

        # Add user interests
        if user_context:
            context_parts.append(f"User Profile:")
            context_parts.append(f"- Business Sector: {user_context.get('business_sector', 'N/A')}")
            context_parts.append(f"- Interests: {', '.join(user_context.get('interests', ['general']))}")
            context_parts.append(f"- Stage: {user_context.get('tier', 'N/A')}")
            context_parts.append("")

        # Add news items
        if news_items:
            context_parts.append("Recent Relevant News:")
            for i, news in enumerate(news_items, 1):
                context_parts.append(f"\n{i}. {news.get('title')}")
                context_parts.append(f"   Source: {news.get('source')} | Date: {news.get('published_date')}")
                context_parts.append(f"   Sentiment: {news.get('sentiment')} | Impact: {news.get('impact')}")
                context_parts.append(f"   Summary: {news.get('content', '')[:200]}...")
            context_parts.append("")

        # Add historical trend data
        if retrieved_docs:
            context_parts.append("Historical Trend Data:")
            for i, doc in enumerate(retrieved_docs[:2], 1):
                context_parts.append(f"\n{i}. {doc.get('title', 'Trend Report')}")
                context_parts.append(doc.get('content', '')[:300])
            context_parts.append("")

        # Add query
        context_parts.append(f"News Query: {query}")

        return "\n".join(context_parts)

    def _format_news_sources(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format news items as sources"""
        formatted = []
        for news in news_items:
            formatted.append({
                "title": news.get("title"),
                "content": news.get("content", "")[:200],
                "url": news.get("url"),
                "source": news.get("source"),
                "published_date": str(news.get("published_date")),
                "relevance_score": news.get("relevance_score", 0.0),
                "sentiment": news.get("sentiment", "neutral"),
                "impact": news.get("impact", "medium")
            })
        return formatted

    def _detect_trends(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect trends from multiple news items

        In production, this would use:
        - NLP for topic modeling
        - Time-series analysis for trend detection
        - ML models for pattern recognition
        """
        # Placeholder trend detection
        trends = []

        # Simple keyword-based trend detection (placeholder)
        keywords = {}
        for news in news_items:
            content = news.get("content", "").lower()
            # Count keyword frequencies
            # This is simplified - production would use proper NLP

        return trends

    def _calculate_sentiment_aggregate(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate sentiment from news items"""
        sentiments = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }

        for news in news_items:
            sentiment = news.get("sentiment", "neutral")
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1

        total = sum(sentiments.values())
        if total > 0:
            sentiments = {k: (v / total) * 100 for k, v in sentiments.items()}

        return {
            "overall_sentiment": max(sentiments, key=sentiments.get),
            "distribution": sentiments,
            "confidence": max(sentiments.values()) if sentiments else 0
        }
