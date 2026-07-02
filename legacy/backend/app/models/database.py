"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from pymongo import MongoClient
from redis import Redis
from neo4j import GraphDatabase
from ..core.config import settings

# PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# MongoDB
mongo_client = MongoClient(settings.MONGODB_URL)
mongodb = mongo_client[settings.MONGODB_DB_NAME]


def get_mongodb():
    """MongoDB dependency"""
    return mongodb


# Redis
redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)


def get_redis():
    """Redis dependency"""
    return redis_client


# Neo4j
class Neo4jConnection:
    """Neo4j connection manager"""

    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        if self.driver:
            self.driver.close()

    def query(self, cypher_query: str, parameters: dict = None):
        """Execute a Cypher query"""
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters)
            return [record.data() for record in result]

    def write(self, cypher_query: str, parameters: dict = None):
        """Execute a write transaction"""
        with self.driver.session() as session:
            result = session.write_transaction(
                lambda tx: tx.run(cypher_query, parameters)
            )
            return result


neo4j_conn = Neo4jConnection()


def get_neo4j():
    """Neo4j dependency"""
    return neo4j_conn
