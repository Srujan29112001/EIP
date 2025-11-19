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
        Process news-related queries with real-time analysis

        Args:
            query: User query about news/trends
            context: User context (interests, business sector, etc.)

        Returns:
            Curated news and trend analysis with sentiment insights
        """
        # Extract user context
        user_context = context or {}
        user_interests = user_context.get("interests", [])
        business_sector = user_context.get("business_sector", "general")
        user_tier = user_context.get("tier", "aspiring")

        # Retrieve relevant news (real-time)
        news_items = await self._fetch_relevant_news(query, user_interests, business_sector)

        # Detect trends from news items
        trends = await self._detect_trends(news_items)

        # Calculate aggregate sentiment
        sentiment_analysis = await self._calculate_sentiment_aggregate(news_items)

        # Retrieve historical trend data from RAG
        retrieved_docs = await self._retrieve_context(query)

        # Build context for LLM
        context_str = self._build_context(
            query,
            user_context,
            news_items,
            retrieved_docs
        )

        # Add trends and sentiment to context
        context_str += f"\n\n**Detected Trends:** {len(trends)} trends identified"
        context_str += f"\n**Market Sentiment:** {sentiment_analysis.get('overall_sentiment', 'neutral')}"
        context_str += f"\n**Market Mood:** {sentiment_analysis.get('market_mood', 'mixed')}"

        # Generate news analysis using LLM
        response = await self._generate_response(query, context_str)

        # Integrate trends and sentiment into response
        response = self._integrate_insights(response, trends, sentiment_analysis)

        # Format sources (news articles)
        sources = self._format_news_sources(news_items)

        # Check for real-time alerts
        alerts = await self._check_for_alerts(news_items, user_context)

        return {
            "agent": self.agent_name,
            "answer": response,
            "sources": sources,
            "trends": trends,
            "sentiment_analysis": sentiment_analysis,
            "alerts": alerts,
            "metadata": {
                "user_tier": user_tier,
                "business_sector": business_sector,
                "interests": user_interests,
                "news_items_analyzed": len(news_items),
                "trends_detected": len(trends),
                "real_time": True,
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
        Fetch relevant news from various sources with LLM-powered relevance scoring

        Implementation:
        - Retrieves news from RAG/vector database (populated by news ingestion pipeline)
        - Uses LLM to score relevance and extract sentiment
        - Applies user-specific filtering based on interests and sector
        - Deduplicates similar articles
        """
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.rag_service import RAGService, VectorStoreProvider

            # Initialize RAG service for news retrieval
            rag = RAGService(provider=VectorStoreProvider.CHROMA)

            # Build enhanced query with user context
            enhanced_query = query
            if interests:
                enhanced_query += f" interests: {', '.join(interests)}"
            if sector and sector != "general":
                enhanced_query += f" sector: {sector}"

            # Retrieve news articles from vector database
            news_results = await rag.retrieve(
                query=enhanced_query,
                collection_name="news_articles",
                top_k=10  # Get top 10 relevant articles
            )

            # Process and enrich news items with sentiment and impact analysis
            processed_news = []
            for result in news_results:
                metadata = result.get('metadata', {})
                content = result.get('content', '')

                # Use LLM to analyze sentiment and impact if not already present
                if not metadata.get('sentiment') or not metadata.get('impact'):
                    analysis = await self._analyze_news_item(
                        title=metadata.get('title', 'Untitled'),
                        content=content,
                        user_sector=sector
                    )
                    metadata.update(analysis)

                news_item = {
                    "title": metadata.get('title', 'Untitled'),
                    "source": metadata.get('source', 'Unknown'),
                    "published_date": metadata.get('published_date', datetime.now()),
                    "content": content[:500],  # Truncate for efficiency
                    "url": metadata.get('url', ''),
                    "relevance_score": result.get('score', 0.5),
                    "sentiment": metadata.get('sentiment', 'neutral'),
                    "impact": metadata.get('impact', 'medium'),
                    "category": metadata.get('category', 'general')
                }
                processed_news.append(news_item)

            # Sort by relevance score
            processed_news.sort(key=lambda x: x['relevance_score'], reverse=True)

            return processed_news[:8] if processed_news else self._get_fallback_news(sector)

        except Exception as e:
            print(f"News retrieval failed: {e}. Using fallback.")
            return self._get_fallback_news(sector)

    def _get_fallback_news(self, sector: str = "general") -> List[Dict[str, Any]]:
        """Fallback news when retrieval fails"""
        sample_news = [
            {
                "title": f"Latest {sector.title()} Industry Trends and Updates",
                "source": "Business Intelligence",
                "published_date": datetime.now() - timedelta(hours=2),
                "content": f"Recent developments in the {sector} sector show significant activity. Industry experts highlight key opportunities for entrepreneurs...",
                "url": "https://example.com/news/fallback",
                "relevance_score": 0.85,
                "sentiment": "positive",
                "impact": "medium",
                "category": sector
            },
            {
                "title": "Market Analysis: Growth Opportunities for Startups",
                "source": "Startup News",
                "published_date": datetime.now() - timedelta(hours=5),
                "content": "Analysis of current market conditions reveals several opportunities for new ventures across multiple sectors...",
                "url": "https://example.com/news/market-analysis",
                "relevance_score": 0.80,
                "sentiment": "positive",
                "impact": "medium",
                "category": "general"
            },
            {
                "title": "Regulatory Updates Affecting Business Operations",
                "source": "Business Daily",
                "published_date": datetime.now() - timedelta(hours=8),
                "content": "New regulatory frameworks announced that may impact business operations and compliance requirements...",
                "url": "https://example.com/news/regulations",
                "relevance_score": 0.75,
                "sentiment": "neutral",
                "impact": "high",
                "category": "policy"
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

    async def _detect_trends(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect trends from multiple news items using LLM-powered analysis

        Uses LLM to:
        - Identify emerging patterns across articles
        - Detect topic clusters
        - Analyze temporal patterns
        - Assess trend strength and momentum
        """
        try:
            import sys
            import os
            import json
            import re
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            # Prepare news items summary for trend analysis
            news_summary = "\n\n".join([
                f"**{news.get('title')}** ({news.get('source')}, {news.get('published_date')})\n"
                f"Sentiment: {news.get('sentiment')}, Impact: {news.get('impact')}\n"
                f"Content: {news.get('content', '')[:200]}..."
                for news in news_items[:10]  # Analyze top 10 articles
            ])

            trend_prompt = f"""Analyze these news articles and identify emerging trends, patterns, and themes.

News Articles:
{news_summary}

Identify and analyze trends:
1. **Emerging Topics**: What new themes are appearing?
2. **Momentum**: Are these trends accelerating or declining?
3. **Market Implications**: What do these trends mean for businesses?
4. **Opportunities**: What opportunities do these trends create?

Return ONLY valid JSON format:
{{
  "trends": [
    {{
      "name": "Trend name",
      "description": "Brief description",
      "strength": "emerging|growing|strong|declining",
      "sentiment": "positive|negative|neutral",
      "articles_count": <number>,
      "business_impact": "Brief impact description",
      "opportunities": ["opportunity1", "opportunity2"]
    }}
  ]
}}

Identify 3-5 key trends. Return ONLY the JSON."""

            response = await llm.generate(
                prompt=trend_prompt,
                temperature=0.4,
                max_tokens=1000
            )

            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                trend_data = json.loads(json_match.group(0))
                return trend_data.get('trends', [])
            else:
                return self._get_fallback_trends()

        except Exception as e:
            print(f"Trend detection failed: {e}. Using fallback.")
            return self._get_fallback_trends()

    def _get_fallback_trends(self) -> List[Dict[str, Any]]:
        """Fallback trends when LLM analysis fails"""
        return [
            {
                "name": "Industry Growth",
                "description": "Overall positive growth across multiple sectors",
                "strength": "growing",
                "sentiment": "positive",
                "articles_count": 3,
                "business_impact": "Favorable conditions for business expansion",
                "opportunities": ["Market entry", "Product launches"]
            }
        ]

    async def _calculate_sentiment_aggregate(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate aggregate sentiment from news items using LLM-powered analysis

        Provides nuanced sentiment analysis beyond simple positive/negative/neutral
        """
        # First calculate basic sentiment distribution
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
            sentiment_percentages = {k: (v / total) * 100 for k, v in sentiments.items()}
        else:
            sentiment_percentages = {"positive": 33.3, "neutral": 33.3, "negative": 33.3}

        # Use LLM for nuanced sentiment analysis
        try:
            import sys
            import os
            import json
            import re
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            # Prepare news headlines for analysis
            headlines = "\n".join([
                f"- {news.get('title')} (Sentiment: {news.get('sentiment')}, Impact: {news.get('impact')})"
                for news in news_items[:15]
            ])

            sentiment_prompt = f"""Analyze the overall sentiment and market mood from these news headlines.

Headlines:
{headlines}

Provide a nuanced sentiment analysis considering:
1. Overall market mood (optimistic, cautious, pessimistic)
2. Confidence level in the market
3. Key sentiment drivers
4. Actionable insights

Return ONLY valid JSON format:
{{
  "overall_sentiment": "very_positive|positive|neutral|negative|very_negative",
  "market_mood": "optimistic|cautious|pessimistic|mixed",
  "confidence_score": <0-100>,
  "sentiment_drivers": ["driver1", "driver2", "driver3"],
  "actionable_insights": "Brief recommendation based on sentiment",
  "risk_level": "low|medium|high"
}}

Return ONLY the JSON."""

            response = await llm.generate(
                prompt=sentiment_prompt,
                temperature=0.3,
                max_tokens=400
            )

            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                llm_sentiment = json.loads(json_match.group(0))

                return {
                    "overall_sentiment": llm_sentiment.get("overall_sentiment", max(sentiments, key=sentiments.get)),
                    "distribution": sentiment_percentages,
                    "market_mood": llm_sentiment.get("market_mood", "mixed"),
                    "confidence_score": llm_sentiment.get("confidence_score", 50),
                    "sentiment_drivers": llm_sentiment.get("sentiment_drivers", []),
                    "actionable_insights": llm_sentiment.get("actionable_insights", "Monitor market conditions"),
                    "risk_level": llm_sentiment.get("risk_level", "medium")
                }

        except Exception as e:
            print(f"LLM sentiment analysis failed: {e}. Using basic analysis.")

        # Fallback to basic sentiment
        return {
            "overall_sentiment": max(sentiments, key=sentiments.get),
            "distribution": sentiment_percentages,
            "market_mood": "mixed",
            "confidence_score": max(sentiment_percentages.values()) if sentiment_percentages else 0,
            "sentiment_drivers": ["Limited analysis available"],
            "actionable_insights": "Continue monitoring market trends",
            "risk_level": "medium"
        }

    async def _analyze_news_item(
        self,
        title: str,
        content: str,
        user_sector: str = "general"
    ) -> Dict[str, str]:
        """
        Analyze individual news item for sentiment and impact using LLM

        Args:
            title: News article title
            content: News article content
            user_sector: User's business sector for context

        Returns:
            Dict with sentiment and impact analysis
        """
        try:
            import sys
            import os
            import json
            import re
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            analysis_prompt = f"""Analyze this news article for sentiment and business impact.

Title: {title}
Content: {content[:500]}
User Sector: {user_sector}

Determine:
1. **Sentiment**: Overall tone (positive, negative, neutral)
2. **Impact**: Business impact level (high, medium, low)
3. **Category**: News category (technology, policy, market, finance, industry, etc.)

Return ONLY valid JSON format:
{{
  "sentiment": "positive|negative|neutral",
  "impact": "high|medium|low",
  "category": "technology|policy|market|finance|industry|general"
}}

Return ONLY the JSON."""

            response = await llm.generate(
                prompt=analysis_prompt,
                temperature=0.2,
                max_tokens=100
            )

            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group(0))
                return analysis
            else:
                return self._get_fallback_news_analysis()

        except Exception as e:
            print(f"News item analysis failed: {e}")
            return self._get_fallback_news_analysis()

    def _get_fallback_news_analysis(self) -> Dict[str, str]:
        """Fallback analysis when LLM fails"""
        return {
            "sentiment": "neutral",
            "impact": "medium",
            "category": "general"
        }

    def _integrate_insights(
        self,
        response: str,
        trends: List[Dict[str, Any]],
        sentiment_analysis: Dict[str, Any]
    ) -> str:
        """
        Integrate trend and sentiment insights into the news analysis response

        Args:
            response: LLM-generated response
            trends: Detected trends
            sentiment_analysis: Aggregate sentiment analysis

        Returns:
            Enhanced response with insights
        """
        insights_section = "\n\n## Market Intelligence Insights\n\n"

        # Add sentiment insights
        insights_section += f"### Market Sentiment\n"
        insights_section += f"**Overall Mood:** {sentiment_analysis.get('market_mood', 'mixed').title()}\n"
        insights_section += f"**Sentiment:** {sentiment_analysis.get('overall_sentiment', 'neutral').replace('_', ' ').title()}\n"
        insights_section += f"**Risk Level:** {sentiment_analysis.get('risk_level', 'medium').upper()}\n\n"

        if sentiment_analysis.get('actionable_insights'):
            insights_section += f"**Recommendation:** {sentiment_analysis['actionable_insights']}\n\n"

        # Add trend insights
        if trends:
            insights_section += f"### Emerging Trends ({len(trends)} detected)\n\n"
            for i, trend in enumerate(trends[:5], 1):  # Top 5 trends
                insights_section += f"**{i}. {trend.get('name', 'Trend')}** "
                insights_section += f"({trend.get('strength', 'emerging').title()})\n"
                insights_section += f"   - {trend.get('description', 'No description')}\n"
                insights_section += f"   - Impact: {trend.get('business_impact', 'N/A')}\n"

                if trend.get('opportunities'):
                    insights_section += f"   - Opportunities: {', '.join(trend['opportunities'][:3])}\n"
                insights_section += "\n"

        return response + insights_section

    async def _check_for_alerts(
        self,
        news_items: List[Dict[str, Any]],
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check for important real-time alerts based on news items

        Identifies high-impact news that requires immediate attention

        Args:
            news_items: List of news items
            user_context: User context for personalization

        Returns:
            List of alerts
        """
        alerts = []

        # Check for high-impact negative news
        for news in news_items:
            if news.get('impact') == 'high' and news.get('sentiment') == 'negative':
                alerts.append({
                    "type": "warning",
                    "priority": "high",
                    "title": news.get('title'),
                    "message": f"High-impact negative news detected: {news.get('title')}",
                    "action": "Review and assess potential impact on your business",
                    "source": news.get('source'),
                    "timestamp": str(news.get('published_date'))
                })

        # Check for high-impact positive news (opportunities)
        for news in news_items:
            if news.get('impact') == 'high' and news.get('sentiment') == 'positive':
                alerts.append({
                    "type": "opportunity",
                    "priority": "medium",
                    "title": news.get('title'),
                    "message": f"Opportunity alert: {news.get('title')}",
                    "action": "Explore potential opportunities from this development",
                    "source": news.get('source'),
                    "timestamp": str(news.get('published_date'))
                })

        # Use LLM for advanced alert detection if we have many news items
        if len(news_items) >= 5:
            llm_alerts = await self._detect_critical_alerts_llm(news_items, user_context)
            alerts.extend(llm_alerts)

        # Limit to top 5 most important alerts
        alerts.sort(key=lambda x: 0 if x['priority'] == 'high' else 1)
        return alerts[:5]

    async def _detect_critical_alerts_llm(
        self,
        news_items: List[Dict[str, Any]],
        user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to detect critical alerts from news items

        Args:
            news_items: List of news items
            user_context: User context

        Returns:
            List of critical alerts
        """
        try:
            import sys
            import os
            import json
            import re
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            # Prepare news summary
            news_summary = "\n".join([
                f"- {news.get('title')} (Impact: {news.get('impact')}, Sentiment: {news.get('sentiment')})"
                for news in news_items[:10]
            ])

            alert_prompt = f"""Analyze these news items and identify any critical alerts requiring immediate attention.

User Business Sector: {user_context.get('business_sector', 'general')}
User Interests: {user_context.get('interests', [])}

News Items:
{news_summary}

Identify critical alerts that:
1. Require immediate action or attention
2. Represent significant risks or opportunities
3. Could directly impact the user's business

Return ONLY valid JSON format:
{{
  "alerts": [
    {{
      "type": "warning|opportunity|regulatory|competitive",
      "priority": "high|medium",
      "title": "Alert title",
      "message": "Brief alert message",
      "action": "Recommended action"
    }}
  ]
}}

Identify 0-3 most critical alerts. Return ONLY the JSON."""

            response = await llm.generate(
                prompt=alert_prompt,
                temperature=0.2,
                max_tokens=500
            )

            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                alert_data = json.loads(json_match.group(0))
                return alert_data.get('alerts', [])

        except Exception as e:
            print(f"LLM alert detection failed: {e}")

        return []
