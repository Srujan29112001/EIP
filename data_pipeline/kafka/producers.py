"""
Kafka Producers for real-time data streaming
Produces news, market data, policy updates, and user events
"""
from typing import Dict, Any, Optional
from kafka import KafkaProducer
import json
import os
from datetime import datetime
from enum import Enum


class KafkaTopic(str, Enum):
    """Kafka topic names"""
    NEWS_STREAM = "news_stream"
    MARKET_STREAM = "market_stream"
    POLICY_STREAM = "policy_stream"
    USER_EVENTS = "user_events"
    AGENT_LOGS = "agent_logs"


class EIPKafkaProducer:
    """Base Kafka producer for EIP platform"""

    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        client_id: str = "eip_producer"
    ):
        """
        Initialize Kafka producer

        Args:
            bootstrap_servers: Kafka bootstrap servers
            client_id: Client identifier
        """
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "localhost:9092"
        )
        self.client_id = client_id

        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers.split(','),
            client_id=self.client_id,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # Wait for all replicas
            retries=3,
            compression_type='snappy'
        )

    def send_message(
        self,
        topic: KafkaTopic,
        message: Dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """
        Send message to Kafka topic

        Args:
            topic: Kafka topic
            message: Message payload
            key: Optional message key for partitioning

        Returns:
            Success status
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in message:
                message['timestamp'] = datetime.utcnow().isoformat()

            # Send message
            future = self.producer.send(
                topic.value,
                value=message,
                key=key
            )

            # Wait for send to complete
            future.get(timeout=10)
            return True

        except Exception as e:
            print(f"Error sending message to {topic.value}: {e}")
            return False

    def close(self):
        """Close producer connection"""
        self.producer.flush()
        self.producer.close()


class NewsProducer(EIPKafkaProducer):
    """Producer for news data"""

    def __init__(self):
        super().__init__(client_id="news_producer")

    def publish_news(
        self,
        title: str,
        content: str,
        source: str,
        url: str,
        category: str = "general",
        sentiment: Optional[str] = None
    ) -> bool:
        """
        Publish news article to Kafka

        Args:
            title: News title
            content: News content
            source: News source
            url: Article URL
            category: News category
            sentiment: Sentiment (positive/negative/neutral)

        Returns:
            Success status
        """
        message = {
            "type": "news_article",
            "title": title,
            "content": content,
            "source": source,
            "url": url,
            "category": category,
            "sentiment": sentiment,
            "published_at": datetime.utcnow().isoformat()
        }

        return self.send_message(
            topic=KafkaTopic.NEWS_STREAM,
            message=message,
            key=url  # Use URL as key for deduplication
        )


class MarketDataProducer(EIPKafkaProducer):
    """Producer for market data"""

    def __init__(self):
        super().__init__(client_id="market_data_producer")

    def publish_stock_price(
        self,
        symbol: str,
        price: float,
        volume: int,
        change_percent: float,
        market: str = "NSE"
    ) -> bool:
        """
        Publish stock price update

        Args:
            symbol: Stock symbol
            price: Current price
            volume: Trading volume
            change_percent: Percentage change
            market: Market identifier

        Returns:
            Success status
        """
        message = {
            "type": "stock_price",
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "change_percent": change_percent,
            "market": market
        }

        return self.send_message(
            topic=KafkaTopic.MARKET_STREAM,
            message=message,
            key=symbol
        )

    def publish_economic_indicator(
        self,
        indicator_name: str,
        value: float,
        country: str = "India",
        unit: str = "%"
    ) -> bool:
        """
        Publish economic indicator update

        Args:
            indicator_name: Indicator name (e.g., 'GDP', 'Inflation')
            value: Indicator value
            country: Country
            unit: Unit of measurement

        Returns:
            Success status
        """
        message = {
            "type": "economic_indicator",
            "indicator": indicator_name,
            "value": value,
            "country": country,
            "unit": unit
        }

        return self.send_message(
            topic=KafkaTopic.MARKET_STREAM,
            message=message,
            key=f"{country}_{indicator_name}"
        )


class PolicyProducer(EIPKafkaProducer):
    """Producer for policy updates"""

    def __init__(self):
        super().__init__(client_id="policy_producer")

    def publish_policy_update(
        self,
        policy_id: str,
        title: str,
        description: str,
        category: str,
        effective_date: str,
        impact_level: str = "medium",
        affected_sectors: Optional[list] = None
    ) -> bool:
        """
        Publish policy update

        Args:
            policy_id: Unique policy identifier
            title: Policy title
            description: Policy description
            category: Policy category
            effective_date: Effective date (ISO format)
            impact_level: Impact level (high/medium/low)
            affected_sectors: List of affected sectors

        Returns:
            Success status
        """
        message = {
            "type": "policy_update",
            "policy_id": policy_id,
            "title": title,
            "description": description,
            "category": category,
            "effective_date": effective_date,
            "impact_level": impact_level,
            "affected_sectors": affected_sectors or []
        }

        return self.send_message(
            topic=KafkaTopic.POLICY_STREAM,
            message=message,
            key=policy_id
        )


class UserEventProducer(EIPKafkaProducer):
    """Producer for user events"""

    def __init__(self):
        super().__init__(client_id="user_event_producer")

    def log_user_query(
        self,
        user_id: str,
        query: str,
        agent_used: str,
        response_time_ms: int,
        success: bool = True
    ) -> bool:
        """
        Log user query event

        Args:
            user_id: User identifier
            query: User query
            agent_used: Agent that handled query
            response_time_ms: Response time in milliseconds
            success: Whether query was successful

        Returns:
            Success status
        """
        message = {
            "type": "user_query",
            "user_id": user_id,
            "query": query,
            "agent_used": agent_used,
            "response_time_ms": response_time_ms,
            "success": success
        }

        return self.send_message(
            topic=KafkaTopic.USER_EVENTS,
            message=message,
            key=user_id
        )

    def log_user_action(
        self,
        user_id: str,
        action_type: str,
        action_details: Dict[str, Any]
    ) -> bool:
        """
        Log generic user action

        Args:
            user_id: User identifier
            action_type: Type of action
            action_details: Action details

        Returns:
            Success status
        """
        message = {
            "type": "user_action",
            "user_id": user_id,
            "action_type": action_type,
            "details": action_details
        }

        return self.send_message(
            topic=KafkaTopic.USER_EVENTS,
            message=message,
            key=user_id
        )


# Factory functions
def create_news_producer() -> NewsProducer:
    """Create news producer"""
    return NewsProducer()


def create_market_producer() -> MarketDataProducer:
    """Create market data producer"""
    return MarketDataProducer()


def create_policy_producer() -> PolicyProducer:
    """Create policy producer"""
    return PolicyProducer()


def create_user_event_producer() -> UserEventProducer:
    """Create user event producer"""
    return UserEventProducer()


# Example usage
if __name__ == "__main__":
    # Example: Publish news
    news_producer = create_news_producer()
    news_producer.publish_news(
        title="New Startup Policy Announced",
        content="Government announces new benefits for startups...",
        source="Economic Times",
        url="https://example.com/news/1",
        category="policy",
        sentiment="positive"
    )
    news_producer.close()

    # Example: Publish market data
    market_producer = create_market_producer()
    market_producer.publish_stock_price(
        symbol="INFY",
        price=1450.50,
        volume=1000000,
        change_percent=2.5
    )
    market_producer.close()
