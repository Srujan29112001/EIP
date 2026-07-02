"""
Kafka Consumers
Consumes messages from Kafka topics and processes them in real-time
"""
import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ConsumedMessage:
    """Represents a consumed Kafka message"""
    topic: str
    key: str
    value: Dict[str, Any]
    timestamp: datetime
    partition: int
    offset: int


class KafkaConsumerBase:
    """
    Base Kafka Consumer class
    """

    def __init__(
        self,
        topic: str,
        group_id: str,
        bootstrap_servers: str = None,
        auto_offset_reset: str = "earliest"
    ):
        """
        Initialize Kafka consumer

        Args:
            topic: Kafka topic to consume from
            group_id: Consumer group ID
            bootstrap_servers: Kafka broker addresses
            auto_offset_reset: Offset reset policy ('earliest' or 'latest')
        """
        try:
            from kafka import KafkaConsumer
        except ImportError:
            raise ImportError("Please install kafka-python: pip install kafka-python")

        self.topic = topic
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "localhost:9092"
        )

        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda m: m.decode('utf-8') if m else None
        )

        self.running = False
        self.message_handlers: List[Callable] = []

    def add_handler(self, handler: Callable):
        """
        Add a message handler function

        Args:
            handler: Async function that processes messages
        """
        self.message_handlers.append(handler)

    async def process_message(self, message: ConsumedMessage):
        """
        Process a consumed message

        Args:
            message: Consumed message

        Override this method in subclasses for custom processing
        """
        # Call all registered handlers
        for handler in self.message_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                print(f"Handler error: {e}")

    async def start(self):
        """Start consuming messages"""
        self.running = True
        print(f"Starting consumer for topic: {self.topic}, group: {self.group_id}")

        try:
            for kafka_message in self.consumer:
                if not self.running:
                    break

                # Convert to ConsumedMessage
                message = ConsumedMessage(
                    topic=kafka_message.topic,
                    key=kafka_message.key,
                    value=kafka_message.value,
                    timestamp=datetime.fromtimestamp(kafka_message.timestamp / 1000),
                    partition=kafka_message.partition,
                    offset=kafka_message.offset
                )

                # Process message
                await self.process_message(message)

        except KeyboardInterrupt:
            print("Consumer interrupted by user")
        finally:
            self.stop()

    def stop(self):
        """Stop consuming messages"""
        self.running = False
        self.consumer.close()
        print(f"Consumer stopped for topic: {self.topic}")


class NewsConsumer(KafkaConsumerBase):
    """
    Consumer for news stream
    Processes real-time news articles and stores them in the database
    """

    def __init__(
        self,
        bootstrap_servers: str = None,
        db_connection: Optional[Any] = None
    ):
        """
        Initialize News Consumer

        Args:
            bootstrap_servers: Kafka broker addresses
            db_connection: Database connection for storing news
        """
        super().__init__(
            topic="news_stream",
            group_id="news_consumer_group",
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="latest"  # Only consume new news
        )
        self.db_connection = db_connection
        self.processed_count = 0

    async def process_message(self, message: ConsumedMessage):
        """
        Process news message

        Args:
            message: News message from Kafka
        """
        try:
            news_data = message.value

            # Extract news fields
            title = news_data.get('title', '')
            content = news_data.get('content', '')
            url = news_data.get('url', '')
            source = news_data.get('source', '')
            published_at = news_data.get('published_at', '')

            # Perform sentiment analysis
            sentiment = await self._analyze_sentiment(content)

            # Extract entities
            entities = await self._extract_entities(content)

            # Store in database
            if self.db_connection:
                await self._store_news(
                    title=title,
                    content=content,
                    url=url,
                    source=source,
                    published_at=published_at,
                    sentiment=sentiment,
                    entities=entities
                )

            # Store in vector store for RAG
            await self._index_for_rag(
                content=f"{title}\n{content}",
                metadata={
                    'title': title,
                    'url': url,
                    'source': source,
                    'date': published_at,
                    'type': 'news',
                    'sentiment': sentiment
                }
            )

            self.processed_count += 1

            if self.processed_count % 10 == 0:
                print(f"Processed {self.processed_count} news articles")

            # Call parent handlers
            await super().process_message(message)

        except Exception as e:
            print(f"Error processing news message: {e}")

    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of news content"""
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            prompt = f"""Analyze the sentiment of this news article.

            Text: "{text[:500]}..."

            Return ONLY a JSON object:
            {{"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0, "key_topics": ["topic1", "topic2"]}}
            """

            response = await llm.generate(prompt=prompt, temperature=0.2, max_tokens=100)

            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

        except Exception as e:
            print(f"Sentiment analysis failed: {e}")

        return {"sentiment": "neutral", "confidence": 0.5, "key_topics": []}

    async def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from news content"""
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            prompt = f"""Extract key entities (companies, people, products, locations) from this text.

            Text: "{text[:500]}..."

            Return ONLY a comma-separated list (max 10 entities).
            """

            response = await llm.generate(prompt=prompt, temperature=0.2, max_tokens=100)
            entities = [e.strip() for e in response.split(',') if e.strip()]

            return entities[:10]

        except Exception as e:
            print(f"Entity extraction failed: {e}")
            return []

    async def _store_news(
        self,
        title: str,
        content: str,
        url: str,
        source: str,
        published_at: str,
        sentiment: Dict[str, Any],
        entities: List[str]
    ):
        """Store news in database"""
        # In production, implement actual database storage
        # For now, just log
        print(f"Storing news: {title[:50]}... (sentiment: {sentiment.get('sentiment', 'unknown')})")

    async def _index_for_rag(self, content: str, metadata: Dict[str, Any]):
        """Index news content in vector store for RAG retrieval"""
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.rag_service import RAGService, VectorStoreProvider

            rag = RAGService(provider=VectorStoreProvider.CHROMA)

            await rag.add_documents(
                collection_name="news",
                documents=[{
                    "content": content,
                    "metadata": metadata
                }]
            )

        except Exception as e:
            print(f"RAG indexing failed: {e}")


class MarketDataConsumer(KafkaConsumerBase):
    """
    Consumer for market data stream
    Processes real-time market data (stock prices, economic indicators)
    """

    def __init__(
        self,
        bootstrap_servers: str = None,
        db_connection: Optional[Any] = None
    ):
        """
        Initialize Market Data Consumer

        Args:
            bootstrap_servers: Kafka broker addresses
            db_connection: Database connection for storing market data
        """
        super().__init__(
            topic="market_stream",
            group_id="market_consumer_group",
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="latest"
        )
        self.db_connection = db_connection
        self.processed_count = 0

    async def process_message(self, message: ConsumedMessage):
        """
        Process market data message

        Args:
            message: Market data message from Kafka
        """
        try:
            market_data = message.value

            data_type = market_data.get('type', 'unknown')  # stock, forex, crypto, indicator
            symbol = market_data.get('symbol', '')
            price = market_data.get('price', 0.0)
            volume = market_data.get('volume', 0)
            timestamp = market_data.get('timestamp', '')

            # Store in database
            if self.db_connection:
                await self._store_market_data(
                    data_type=data_type,
                    symbol=symbol,
                    price=price,
                    volume=volume,
                    timestamp=timestamp
                )

            # Detect significant price movements
            alert = await self._check_for_price_alert(symbol, price)
            if alert:
                await self._send_price_alert(alert)

            self.processed_count += 1

            if self.processed_count % 100 == 0:
                print(f"Processed {self.processed_count} market data points")

            # Call parent handlers
            await super().process_message(message)

        except Exception as e:
            print(f"Error processing market data message: {e}")

    async def _store_market_data(
        self,
        data_type: str,
        symbol: str,
        price: float,
        volume: int,
        timestamp: str
    ):
        """Store market data in time-series database"""
        print(f"Storing market data: {symbol} = ${price:.2f} @ {timestamp}")

    async def _check_for_price_alert(self, symbol: str, price: float) -> Optional[Dict[str, Any]]:
        """Check if price movement warrants an alert"""
        # Implement price change detection logic
        # For now, return None (no alert)
        return None

    async def _send_price_alert(self, alert: Dict[str, Any]):
        """Send price alert to users"""
        print(f"PRICE ALERT: {alert}")


class PolicyConsumer(KafkaConsumerBase):
    """
    Consumer for policy updates stream
    Processes government policy changes and regulatory updates
    """

    def __init__(
        self,
        bootstrap_servers: str = None,
        db_connection: Optional[Any] = None,
        graphrag_service: Optional[Any] = None
    ):
        """
        Initialize Policy Consumer

        Args:
            bootstrap_servers: Kafka broker addresses
            db_connection: Database connection
            graphrag_service: GraphRAG service for knowledge graph updates
        """
        super().__init__(
            topic="policy_stream",
            group_id="policy_consumer_group",
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="earliest"  # Don't miss any policy updates
        )
        self.db_connection = db_connection
        self.graphrag_service = graphrag_service
        self.processed_count = 0

    async def process_message(self, message: ConsumedMessage):
        """
        Process policy update message

        Args:
            message: Policy message from Kafka
        """
        try:
            policy_data = message.value

            title = policy_data.get('title', '')
            description = policy_data.get('description', '')
            category = policy_data.get('category', '')
            effective_date = policy_data.get('effective_date', '')
            source_url = policy_data.get('source_url', '')
            affected_sectors = policy_data.get('affected_sectors', [])

            # Analyze policy impact
            impact_analysis = await self._analyze_policy_impact(
                title=title,
                description=description,
                affected_sectors=affected_sectors
            )

            # Store in database
            if self.db_connection:
                await self._store_policy(
                    title=title,
                    description=description,
                    category=category,
                    effective_date=effective_date,
                    source_url=source_url,
                    affected_sectors=affected_sectors,
                    impact_analysis=impact_analysis
                )

            # Add to knowledge graph
            if self.graphrag_service:
                await self._add_to_knowledge_graph(
                    title=title,
                    description=description,
                    category=category,
                    affected_sectors=affected_sectors
                )

            # Index in vector store
            await self._index_for_rag(
                content=f"{title}\n{description}",
                metadata={
                    'title': title,
                    'category': category,
                    'effective_date': effective_date,
                    'url': source_url,
                    'type': 'policy',
                    'sectors': affected_sectors
                }
            )

            self.processed_count += 1
            print(f"Processed policy: {title[:50]}... (Total: {self.processed_count})")

            # Call parent handlers
            await super().process_message(message)

        except Exception as e:
            print(f"Error processing policy message: {e}")

    async def _analyze_policy_impact(
        self,
        title: str,
        description: str,
        affected_sectors: List[str]
    ) -> Dict[str, Any]:
        """Analyze policy impact using LLM"""
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            prompt = f"""Analyze the impact of this policy update.

            Title: {title}
            Description: {description}
            Affected Sectors: {', '.join(affected_sectors)}

            Return ONLY a JSON object:
            {{
                "impact_level": "high|medium|low",
                "opportunities": ["opportunity1", "opportunity2"],
                "risks": ["risk1", "risk2"],
                "action_required": true|false
            }}
            """

            response = await llm.generate(prompt=prompt, temperature=0.3, max_tokens=300)

            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

        except Exception as e:
            print(f"Policy impact analysis failed: {e}")

        return {
            "impact_level": "medium",
            "opportunities": [],
            "risks": [],
            "action_required": False
        }

    async def _store_policy(
        self,
        title: str,
        description: str,
        category: str,
        effective_date: str,
        source_url: str,
        affected_sectors: List[str],
        impact_analysis: Dict[str, Any]
    ):
        """Store policy in database"""
        print(f"Storing policy: {title[:50]}... (Impact: {impact_analysis.get('impact_level', 'unknown')})")

    async def _add_to_knowledge_graph(
        self,
        title: str,
        description: str,
        category: str,
        affected_sectors: List[str]
    ):
        """Add policy to Neo4j knowledge graph"""
        if not self.graphrag_service:
            return

        try:
            # Add policy node
            policy_id = await self.graphrag_service.add_node(
                label="Policy",
                properties={
                    "title": title,
                    "description": description,
                    "category": category,
                    "date": datetime.now().isoformat()
                }
            )

            print(f"Added policy to knowledge graph: {title[:50]}...")

        except Exception as e:
            print(f"Knowledge graph update failed: {e}")

    async def _index_for_rag(self, content: str, metadata: Dict[str, Any]):
        """Index policy in vector store"""
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.rag_service import RAGService, VectorStoreProvider

            rag = RAGService(provider=VectorStoreProvider.CHROMA)

            await rag.add_documents(
                collection_name="policies",
                documents=[{
                    "content": content,
                    "metadata": metadata
                }]
            )

        except Exception as e:
            print(f"RAG indexing failed: {e}")


# Consumer Manager
class ConsumerManager:
    """
    Manages multiple Kafka consumers
    """

    def __init__(self):
        """Initialize consumer manager"""
        self.consumers: List[KafkaConsumerBase] = []

    def add_consumer(self, consumer: KafkaConsumerBase):
        """Add a consumer to the manager"""
        self.consumers.append(consumer)

    async def start_all(self):
        """Start all consumers concurrently"""
        tasks = [consumer.start() for consumer in self.consumers]
        await asyncio.gather(*tasks)

    def stop_all(self):
        """Stop all consumers"""
        for consumer in self.consumers:
            consumer.stop()


# Example usage
async def main():
    """Example of running all consumers"""

    # Initialize consumers
    news_consumer = NewsConsumer()
    market_consumer = MarketDataConsumer()
    policy_consumer = PolicyConsumer()

    # Create manager and add consumers
    manager = ConsumerManager()
    manager.add_consumer(news_consumer)
    manager.add_consumer(market_consumer)
    manager.add_consumer(policy_consumer)

    # Start all consumers
    print("Starting all Kafka consumers...")
    try:
        await manager.start_all()
    except KeyboardInterrupt:
        print("\nShutting down consumers...")
        manager.stop_all()


if __name__ == "__main__":
    asyncio.run(main())
