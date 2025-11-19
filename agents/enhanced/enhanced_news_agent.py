"""
Enhanced News Agent - Real-time News Aggregation and Analysis
Aggregates news from multiple sources, performs sentiment analysis, and delivers personalized insights
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

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))  # noqa
from base_agent import BaseAgent

logger = logging.getLogger(__name__)


class EnhancedNewsAgent(BaseAgent):
    """
    Advanced news aggregation and analysis agent
    Provides real-time news updates, sentiment analysis, and personalized feeds
    """

    def __init__(self):
        super().__init__(
            name="Enhanced News Agent",
            description="Real-time news aggregation with sentiment analysis and personalized insights",
            capabilities=[
                "news_aggregation",
                "sentiment_analysis",
                "trend_detection",
                "topic_clustering",
                "personalized_feed",
                "market_impact_analysis"
            ]
        )

        # News sources
        self.news_sources = self._initialize_news_sources()

        # Topic categories
        self.categories = self._initialize_categories()

        # Sentiment keywords
        self.sentiment_keywords = self._initialize_sentiment_keywords()

    def _initialize_news_sources(self) -> List[Dict[str, Any]]:
        """Initialize news source configurations"""
        return [
            {
                "source_id": "techcrunch",
                "name": "TechCrunch",
                "type": "tech_news",
                "reliability_score": 0.92,
                "update_frequency": "hourly",
                "topics": ["startups", "technology", "venture_capital", "product_launches"]
            },
            {
                "source_id": "bloomberg",
                "name": "Bloomberg",
                "type": "financial_news",
                "reliability_score": 0.95,
                "update_frequency": "real_time",
                "topics": ["markets", "economy", "companies", "politics"]
            },
            {
                "source_id": "reuters",
                "name": "Reuters",
                "type": "general_news",
                "reliability_score": 0.94,
                "update_frequency": "real_time",
                "topics": ["world", "business", "technology", "markets"]
            },
            {
                "source_id": "wsj",
                "name": "Wall Street Journal",
                "type": "financial_news",
                "reliability_score": 0.93,
                "update_frequency": "hourly",
                "topics": ["business", "markets", "economy", "real_estate"]
            },
            {
                "source_id": "cnbc",
                "name": "CNBC",
                "type": "financial_news",
                "reliability_score": 0.88,
                "update_frequency": "real_time",
                "topics": ["markets", "investing", "business", "personal_finance"]
            },
            {
                "source_id": "hacker_news",
                "name": "Hacker News",
                "type": "tech_community",
                "reliability_score": 0.85,
                "update_frequency": "continuous",
                "topics": ["technology", "startups", "programming", "science"]
            },
            {
                "source_id": "financial_times",
                "name": "Financial Times",
                "type": "financial_news",
                "reliability_score": 0.94,
                "update_frequency": "hourly",
                "topics": ["global_economy", "markets", "companies", "opinion"]
            },
            {
                "source_id": "the_information",
                "name": "The Information",
                "type": "tech_news",
                "reliability_score": 0.91,
                "update_frequency": "daily",
                "topics": ["tech_industry", "venture_capital", "startups", "big_tech"]
            }
        ]

    def _initialize_categories(self) -> Dict[str, Any]:
        """Initialize news categories"""
        return {
            "Market_Updates": {
                "description": "Stock market movements, indices, trading activity",
                "keywords": ["stock", "market", "trading", "index", "dow", "nasdaq", "s&p"],
                "importance": "high",
                "update_frequency": "real_time"
            },
            "Startup_News": {
                "description": "Startup funding, launches, pivots, exits",
                "keywords": ["startup", "funding", "seed", "series", "vc", "launch", "exit"],
                "importance": "high",
                "update_frequency": "daily"
            },
            "Economic_Indicators": {
                "description": "GDP, unemployment, inflation, interest rates",
                "keywords": ["gdp", "inflation", "unemployment", "fed", "interest rate", "cpi"],
                "importance": "high",
                "update_frequency": "monthly"
            },
            "Technology_Trends": {
                "description": "Emerging technologies, product launches, tech trends",
                "keywords": ["ai", "blockchain", "cloud", "saas", "mobile", "iot", "5g"],
                "importance": "medium",
                "update_frequency": "daily"
            },
            "Regulatory_Changes": {
                "description": "New regulations, policy changes, compliance updates",
                "keywords": ["regulation", "policy", "compliance", "law", "sec", "ftc"],
                "importance": "high",
                "update_frequency": "weekly"
            },
            "Industry_Analysis": {
                "description": "Industry reports, market analysis, competitive insights",
                "keywords": ["industry", "market share", "competition", "trends", "forecast"],
                "importance": "medium",
                "update_frequency": "weekly"
            },
            "Company_News": {
                "description": "Corporate announcements, earnings, M&A, leadership changes",
                "keywords": ["earnings", "merger", "acquisition", "ceo", "layoffs", "partnership"],
                "importance": "medium",
                "update_frequency": "daily"
            },
            "Product_Launches": {
                "description": "New product releases, feature updates, beta programs",
                "keywords": ["launch", "release", "unveil", "announce", "beta", "feature"],
                "importance": "medium",
                "update_frequency": "daily"
            }
        }

    def _initialize_sentiment_keywords(self) -> Dict[str, List[str]]:
        """Initialize sentiment analysis keywords"""
        return {
            "positive": [
                "surges", "soars", "rallies", "gains", "breakthrough", "success", "growth",
                "profit", "innovation", "bullish", "optimistic", "strong", "beat expectations",
                "record", "milestone", "wins", "expands", "launches", "partnership"
            ],
            "negative": [
                "plunges", "crashes", "falls", "losses", "failure", "decline", "bearish",
                "pessimistic", "weak", "misses expectations", "layoffs", "bankruptcy",
                "scandal", "fraud", "investigation", "lawsuit", "risks", "concerns"
            ],
            "neutral": [
                "announces", "reports", "states", "updates", "releases", "publishes",
                "confirms", "maintains", "continues", "plans", "expects"
            ]
        }

    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process news request

        Args:
            query: User query about news
            context: Additional context (topics, timeframe, sources, etc.)

        Returns:
            Dict with news articles, sentiment analysis, and insights
        """
        try:
            logger.info(f"Processing news query: {query[:100]}...")

            # Extract parameters from context
            topics = context.get("topics", []) if context else []
            timeframe = context.get("timeframe", "24h") if context else "24h"
            sources = context.get("sources", []) if context else []
            max_articles = context.get("max_articles", 20) if context else 20

            # Identify relevant categories
            relevant_categories = await self._identify_categories(query, topics)

            # Fetch and aggregate news
            articles = await self._fetch_news(
                categories=relevant_categories,
                timeframe=timeframe,
                sources=sources,
                max_articles=max_articles
            )

            # Perform sentiment analysis
            sentiment_analysis = await self._analyze_sentiment(articles)

            # Detect trends
            trending_topics = await self._detect_trends(articles)

            # Cluster related articles
            article_clusters = await self._cluster_articles(articles)

            # Analyze market impact
            market_impact = await self._analyze_market_impact(articles)

            # Generate personalized feed
            personalized_feed = await self._generate_personalized_feed(
                articles, sentiment_analysis, context
            )

            response = {
                "status": "success",
                "query": query,
                "timeframe": timeframe,
                "total_articles": len(articles),
                "articles": articles[:max_articles],
                "sentiment_analysis": sentiment_analysis,
                "trending_topics": trending_topics,
                "article_clusters": article_clusters,
                "market_impact": market_impact,
                "personalized_feed": personalized_feed,
                "sources_used": self._get_sources_summary(articles),
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Successfully aggregated {len(articles)} news articles")
            return response

        except Exception as e:
            logger.error(f"Error in news aggregation: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _identify_categories(self, query: str, topics: List[str]) -> List[str]:
        """Identify relevant news categories"""
        relevant = []
        query_lower = query.lower()

        for category_name, category_data in self.categories.items():
            keywords = category_data["keywords"]

            # Check if any keyword matches
            if any(keyword in query_lower for keyword in keywords):
                relevant.append(category_name)

            # Check explicit topics
            if any(topic.lower() in category_name.lower() for topic in topics):
                relevant.append(category_name)

        # Default categories if none found
        if not relevant:
            relevant = ["Market_Updates", "Startup_News", "Technology_Trends"]

        return list(set(relevant))

    async def _fetch_news(
        self,
        categories: List[str],
        timeframe: str,
        sources: List[str],
        max_articles: int
    ) -> List[Dict[str, Any]]:
        """Fetch news from various sources"""
        # In production, this would call actual news APIs
        # For now, generate realistic mock data

        articles = []
        num_articles = min(max_articles * 2, 50)  # Generate more for filtering

        for i in range(num_articles):
            article = self._generate_mock_article(categories, sources)
            articles.append(article)

        # Filter by timeframe
        cutoff_time = self._calculate_cutoff_time(timeframe)
        articles = [a for a in articles if a["published_at"] >= cutoff_time]

        # Sort by relevance and recency
        articles.sort(key=lambda x: (x["relevance_score"], x["published_at"]), reverse=True)

        return articles

    def _generate_mock_article(self, categories: List[str], sources: List[str]) -> Dict[str, Any]:
        """Generate mock news article (simulates real API)"""
        # Select random category
        category = random.choice(categories) if categories else random.choice(list(self.categories.keys()))

        # Select random source
        source = random.choice(self.news_sources) if not sources else random.choice(
            [s for s in self.news_sources if s["source_id"] in sources] or self.news_sources
        )

        # Generate realistic title based on category
        titles = self._get_sample_titles(category)
        title = random.choice(titles)

        # Generate timestamp (within last 48 hours)
        hours_ago = random.randint(1, 48)
        published_at = datetime.utcnow() - timedelta(hours=hours_ago)

        return {
            "article_id": f"art_{random.randint(100000, 999999)}",
            "title": title,
            "source": source["name"],
            "source_id": source["source_id"],
            "category": category,
            "published_at": published_at.isoformat(),
            "url": f"https://{source['source_id']}.com/article/{random.randint(100000, 999999)}",
            "summary": self._generate_summary(title, category),
            "relevance_score": random.uniform(0.6, 0.99),
            "sentiment": self._quick_sentiment(title),
            "keywords": self._extract_keywords(title, category),
            "author": f"Author {random.randint(1, 50)}"
        }

    def _get_sample_titles(self, category: str) -> List[str]:
        """Get sample titles for category"""
        titles_by_category = {
            "Market_Updates": [
                "S&P 500 rallies 2% as tech stocks surge on strong earnings",
                "Dow Jones falls 150 points amid inflation concerns",
                "Nasdaq hits record high driven by AI stock momentum",
                "Treasury yields climb as Fed signals hawkish stance",
                "Oil prices surge 5% on OPEC production cuts"
            ],
            "Startup_News": [
                "AI startup raises $50M Series B led by Sequoia Capital",
                "Y Combinator announces W24 batch with record 300 startups",
                "Fintech unicorn files confidentially for IPO",
                "SaaS startup reaches $10M ARR in 18 months",
                "Healthcare startup acquired for $200M by major pharma"
            ],
            "Economic_Indicators": [
                "US GDP grows 2.4% in Q4, beating expectations",
                "Unemployment rate holds steady at 3.7%",
                "Inflation cools to 3.2% in latest CPI reading",
                "Fed keeps interest rates unchanged at 5.25-5.50%",
                "Consumer confidence index rises to 18-month high"
            ],
            "Technology_Trends": [
                "GPT-5 rumors surface as OpenAI hints at major announcement",
                "Apple announces Vision Pro 2 with improved AR capabilities",
                "Google releases Gemini Ultra with breakthrough reasoning",
                "Meta unveils new AI chip to reduce Nvidia dependence",
                "Tesla Full Self-Driving achieves Level 4 autonomy in testing"
            ],
            "Regulatory_Changes": [
                "SEC approves Bitcoin ETF applications from major firms",
                "EU passes comprehensive AI regulation framework",
                "FTC proposes new merger guidelines for tech companies",
                "California enacts strict data privacy law affecting tech giants",
                "IRS issues guidance on cryptocurrency tax reporting"
            ],
            "Industry_Analysis": [
                "SaaS market projected to reach $300B by 2026",
                "E-commerce penetration hits 20% of total retail sales",
                "Cloud infrastructure spending up 25% year-over-year",
                "Fintech funding rebounds with $12B invested in Q4",
                "Healthcare IT adoption accelerates post-pandemic"
            ],
            "Company_News": [
                "Microsoft beats earnings expectations with 18% revenue growth",
                "Amazon announces 10,000 layoffs in cost-cutting move",
                "Tesla CEO Elon Musk steps down as Twitter CEO",
                "Apple announces $90B stock buyback program",
                "Google and Anthropic announce strategic partnership"
            ],
            "Product_Launches": [
                "ChatGPT Enterprise launches with enhanced security features",
                "Slack introduces AI-powered meeting summaries",
                "Notion announces Notion AI for all users",
                "Zoom releases Zoom AI Companion for free",
                "GitHub Copilot X launches with GPT-4 integration"
            ]
        }

        return titles_by_category.get(category, [
            "Breaking: Major development in technology sector",
            "Industry experts predict significant market shifts",
            "New research reveals surprising trends"
        ])

    def _generate_summary(self, title: str, category: str) -> str:
        """Generate article summary"""
        summaries = [
            f"This {category.replace('_', ' ').lower()} article discusses {title.lower()}. Industry experts weigh in on the implications for businesses and investors.",
            f"Analysis of recent developments in {category.replace('_', ' ').lower()}, focusing on key trends and market dynamics.",
            f"Detailed coverage of {title.lower()}, with insights from leading analysts and market participants."
        ]
        return random.choice(summaries)

    def _quick_sentiment(self, title: str) -> str:
        """Quick sentiment analysis of title"""
        title_lower = title.lower()

        positive_count = sum(1 for word in self.sentiment_keywords["positive"] if word in title_lower)
        negative_count = sum(1 for word in self.sentiment_keywords["negative"] if word in title_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _extract_keywords(self, title: str, category: str) -> List[str]:
        """Extract keywords from title"""
        category_keywords = self.categories.get(category, {}).get("keywords", [])
        title_words = title.lower().split()

        keywords = [word for word in category_keywords if word in title.lower()]
        keywords.extend([word for word in title_words if len(word) > 5])

        return list(set(keywords))[:5]

    def _calculate_cutoff_time(self, timeframe: str) -> datetime:
        """Calculate cutoff time based on timeframe"""
        now = datetime.utcnow()

        if timeframe == "1h":
            return now - timedelta(hours=1)
        elif timeframe == "6h":
            return now - timedelta(hours=6)
        elif timeframe == "24h":
            return now - timedelta(hours=24)
        elif timeframe == "7d":
            return now - timedelta(days=7)
        elif timeframe == "30d":
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=24)  # Default to 24h

    async def _analyze_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform sentiment analysis on articles"""
        if not articles:
            return {}

        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

        for article in articles:
            sentiment = article.get("sentiment", "neutral")
            sentiment_counts[sentiment] += 1

        total = len(articles)
        sentiment_distribution = {
            k: round(v / total * 100, 1) for k, v in sentiment_counts.items()
        }

        # Calculate overall sentiment score (-1 to 1)
        sentiment_score = (
            sentiment_counts["positive"] - sentiment_counts["negative"]
        ) / total

        return {
            "sentiment_distribution": sentiment_distribution,
            "overall_sentiment": self._classify_overall_sentiment(sentiment_score),
            "sentiment_score": round(sentiment_score, 2),
            "positive_articles": sentiment_counts["positive"],
            "negative_articles": sentiment_counts["negative"],
            "neutral_articles": sentiment_counts["neutral"]
        }

    def _classify_overall_sentiment(self, score: float) -> str:
        """Classify overall sentiment"""
        if score > 0.3:
            return "Very Positive"
        elif score > 0.1:
            return "Positive"
        elif score < -0.3:
            return "Very Negative"
        elif score < -0.1:
            return "Negative"
        else:
            return "Neutral"

    async def _detect_trends(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect trending topics from articles"""
        # Count keyword frequencies
        keyword_counts = {}

        for article in articles:
            for keyword in article.get("keywords", []):
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

        # Get top trending keywords
        trending = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return [
            {
                "topic": keyword,
                "mention_count": count,
                "trend_strength": "high" if count > 5 else "medium" if count > 2 else "low"
            }
            for keyword, count in trending
        ]

    async def _cluster_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cluster related articles"""
        # Group by category
        clusters = {}

        for article in articles:
            category = article.get("category", "Uncategorized")
            if category not in clusters:
                clusters[category] = []
            clusters[category].append(article["article_id"])

        return [
            {
                "cluster_name": category,
                "article_count": len(article_ids),
                "article_ids": article_ids[:5]  # Top 5 per cluster
            }
            for category, article_ids in clusters.items()
        ]

    async def _analyze_market_impact(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze potential market impact of news"""
        high_impact_categories = ["Market_Updates", "Economic_Indicators", "Regulatory_Changes"]

        high_impact_articles = [
            a for a in articles if a.get("category") in high_impact_categories
        ]

        market_sentiment = "neutral"
        if high_impact_articles:
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            for article in high_impact_articles:
                sentiment_counts[article.get("sentiment", "neutral")] += 1

            if sentiment_counts["positive"] > sentiment_counts["negative"]:
                market_sentiment = "positive"
            elif sentiment_counts["negative"] > sentiment_counts["positive"]:
                market_sentiment = "negative"

        return {
            "high_impact_articles_count": len(high_impact_articles),
            "market_sentiment": market_sentiment,
            "key_market_movers": [
                {
                    "title": a["title"],
                    "sentiment": a["sentiment"],
                    "source": a["source"]
                }
                for a in high_impact_articles[:5]
            ],
            "impact_level": "high" if len(high_impact_articles) > 5 else "moderate" if len(high_impact_articles) > 2 else "low"
        }

    async def _generate_personalized_feed(
        self,
        articles: List[Dict[str, Any]],
        sentiment_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate personalized news feed"""
        preferences = context.get("preferences", {}) if context else {}
        favorite_topics = preferences.get("favorite_topics", [])
        favorite_sources = preferences.get("favorite_sources", [])

        # Score articles based on preferences
        scored_articles = []
        for article in articles:
            score = article.get("relevance_score", 0.5)

            # Boost score for favorite topics
            if article.get("category") in favorite_topics:
                score += 0.2

            # Boost score for favorite sources
            if article.get("source_id") in favorite_sources:
                score += 0.1

            scored_articles.append({**article, "personalized_score": min(score, 1.0)})

        # Sort by personalized score
        scored_articles.sort(key=lambda x: x["personalized_score"], reverse=True)

        return {
            "top_articles": scored_articles[:10],
            "personalization_applied": bool(favorite_topics or favorite_sources),
            "feed_strategy": "personalized" if (favorite_topics or favorite_sources) else "general"
        }

    def _get_sources_summary(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get summary of sources used"""
        source_counts = {}
        for article in articles:
            source = article.get("source", "Unknown")
            source_counts[source] = source_counts.get(source, 0) + 1

        return source_counts

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return self.capabilities

    def get_news_sources(self) -> List[Dict[str, Any]]:
        """Return configured news sources"""
        return self.news_sources

    def get_categories(self) -> List[str]:
        """Return available news categories"""
        return list(self.categories.keys())
