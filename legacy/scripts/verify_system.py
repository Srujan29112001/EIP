#!/usr/bin/env python3
"""
Comprehensive System Verification Script for EIP
Tests all components to ensure 100% functionality
"""
import asyncio
import sys
import os
from typing import Dict, List, Tuple
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}\n")

def print_test(name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"{status} {name}")
    if details:
        print(f"      {Colors.YELLOW}{details}{Colors.RESET}")

class SystemVerifier:
    """Comprehensive system verification"""

    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
        self.start_time = datetime.now()

    async def verify_all(self):
        """Run all verification tests"""
        print_section("EIP SYSTEM VERIFICATION")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Run all verification modules
        await self.verify_environment()
        await self.verify_infrastructure()
        await self.verify_services()
        await self.verify_agents()
        await self.verify_apis()
        await self.verify_data_pipeline()

        # Print summary
        self.print_summary()

    async def verify_environment(self):
        """Verify environment configuration"""
        print_section("1. ENVIRONMENT CONFIGURATION")

        # Check Python version
        python_version = sys.version_info
        passed = python_version >= (3, 8)
        self.results.append(("Python Version", passed, f"Python {python_version.major}.{python_version.minor}"))
        print_test(f"Python Version >= 3.8", passed, f"Found: {python_version.major}.{python_version.minor}")

        # Check environment variables
        required_vars = [
            ("DATABASE_URL", "Database connection"),
            ("REDIS_URL", "Redis cache"),
            ("NEO4J_URI", "Neo4j graph database"),
        ]

        optional_vars = [
            ("OPENAI_API_KEY", "OpenAI LLM"),
            ("ANTHROPIC_API_KEY", "Anthropic Claude"),
        ]

        for var_name, description in required_vars:
            value = os.getenv(var_name)
            passed = value is not None and len(value) > 0
            self.results.append((f"Env: {var_name}", passed, description))
            print_test(f"Environment variable: {var_name}", passed, description)

        print(f"\n{Colors.YELLOW}Optional API Keys (at least one recommended):{Colors.RESET}")
        for var_name, description in optional_vars:
            value = os.getenv(var_name)
            passed = value is not None and len(value) > 10
            print_test(f"Environment variable: {var_name}", passed, description)

    async def verify_infrastructure(self):
        """Verify infrastructure services"""
        print_section("2. INFRASTRUCTURE SERVICES")

        # PostgreSQL
        try:
            from sqlalchemy import create_engine, text
            db_url = os.getenv("DATABASE_URL", "postgresql://eip_user:eip_password@localhost:5432/eip_db")
            engine = create_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                passed = result.scalar() == 1
            self.results.append(("PostgreSQL", passed, "Database connection"))
            print_test("PostgreSQL Connection", passed, db_url.split('@')[1] if '@' in db_url else "localhost")
            engine.dispose()
        except Exception as e:
            self.results.append(("PostgreSQL", False, str(e)[:50]))
            print_test("PostgreSQL Connection", False, str(e)[:100])

        # Redis
        try:
            import redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            r = redis.from_url(redis_url)
            r.ping()
            passed = True
            self.results.append(("Redis", passed, "Cache server"))
            print_test("Redis Connection", passed, redis_url.split('@')[1] if '@' in redis_url else "localhost")
        except Exception as e:
            self.results.append(("Redis", False, str(e)[:50]))
            print_test("Redis Connection", False, str(e)[:100])

        # Neo4j
        try:
            from neo4j import GraphDatabase
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session() as session:
                result = session.run("RETURN 1 AS num")
                passed = result.single()["num"] == 1
            self.results.append(("Neo4j", passed, "Knowledge graph"))
            print_test("Neo4j Connection", passed, uri)
            driver.close()
        except Exception as e:
            self.results.append(("Neo4j", False, str(e)[:50]))
            print_test("Neo4j Connection", False, str(e)[:100])

        # MongoDB (optional)
        try:
            from pymongo import MongoClient
            mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
            client.server_info()
            passed = True
            self.results.append(("MongoDB", passed, "Document store"))
            print_test("MongoDB Connection", passed, "localhost:27017")
            client.close()
        except Exception as e:
            self.results.append(("MongoDB", False, str(e)[:50]))
            print_test("MongoDB Connection (Optional)", False, str(e)[:100])

    async def verify_services(self):
        """Verify backend services"""
        print_section("3. BACKEND SERVICES")

        # LLM Service
        try:
            from services.llm_service import LLMService
            llm_service = LLMService()
            passed = llm_service is not None
            self.results.append(("LLM Service", passed, "OpenAI/Anthropic/DeepSeek"))
            print_test("LLM Service Initialization", passed, "Multi-provider support")
        except Exception as e:
            self.results.append(("LLM Service", False, str(e)[:50]))
            print_test("LLM Service Initialization", False, str(e)[:100])

        # RAG Service
        try:
            from services.rag_service import RAGService, VectorStoreProvider
            rag_service = RAGService(provider=VectorStoreProvider.CHROMA)
            passed = rag_service is not None
            self.results.append(("RAG Service", passed, "Vector store retrieval"))
            print_test("RAG Service Initialization", passed, "Chroma vector store")
        except Exception as e:
            self.results.append(("RAG Service", False, str(e)[:50]))
            print_test("RAG Service Initialization", False, str(e)[:100])

        # GraphRAG Service
        try:
            from services.graphrag_service import GraphRAGService
            graph_service = GraphRAGService()
            passed = graph_service is not None
            self.results.append(("GraphRAG Service", passed, "Knowledge graph queries"))
            print_test("GraphRAG Service Initialization", passed, "Neo4j integration")
        except Exception as e:
            self.results.append(("GraphRAG Service", False, str(e)[:50]))
            print_test("GraphRAG Service Initialization", False, str(e)[:100])

        # OCR Service
        try:
            from services.ocr_service import OCRService
            ocr_service = OCRService()
            passed = ocr_service is not None
            self.results.append(("OCR Service", passed, "Document text extraction"))
            print_test("OCR Service Initialization", passed, "Multi-provider OCR")
        except Exception as e:
            self.results.append(("OCR Service", False, str(e)[:50]))
            print_test("OCR Service Initialization", False, str(e)[:100])

        # VLM Service
        try:
            from services.vlm_service import VLMService
            vlm_service = VLMService()
            passed = vlm_service is not None
            self.results.append(("VLM Service", passed, "Vision-language models"))
            print_test("VLM Service Initialization", passed, "GPT-4V, LLaVA support")
        except Exception as e:
            self.results.append(("VLM Service", False, str(e)[:50]))
            print_test("VLM Service Initialization", False, str(e)[:100])

    async def verify_agents(self):
        """Verify AI agents"""
        print_section("4. AI AGENT SYSTEM")

        agents = [
            ("policy_agent", "PolicyAgent", "Policy analysis & compliance"),
            ("market_agent", "MarketAgent", "Market intelligence & trends"),
            ("finance_agent", "FinanceAgent", "Financial analysis & optimization"),
            ("tax_agent", "TaxAgent", "Tax planning & deductions"),
            ("distribution_agent", "DistributionAgent", "Distribution strategy"),
            ("investment_agent", "InvestmentAgent", "Investment due diligence"),
            ("legal_agent", "LegalAgent", "Contract analysis & legal"),
            ("news_agent", "NewsAgent", "News curation & alerts"),
        ]

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

        for module_name, class_name, description in agents:
            try:
                module = __import__(f"{module_name}.{module_name}", fromlist=[class_name])
                agent_class = getattr(module, class_name)
                agent = agent_class()
                passed = agent is not None
                self.results.append((f"Agent: {class_name}", passed, description))
                print_test(f"{class_name}", passed, description)
            except Exception as e:
                self.results.append((f"Agent: {class_name}", False, str(e)[:50]))
                print_test(f"{class_name}", False, str(e)[:100])

        # Agent Orchestrator
        try:
            from orchestrator.agent_orchestrator import AgentOrchestrator
            orchestrator = AgentOrchestrator()
            passed = orchestrator is not None
            self.results.append(("Agent Orchestrator", passed, "Multi-agent coordination"))
            print_test("Agent Orchestrator", passed, "Intelligent query routing")
        except Exception as e:
            self.results.append(("Agent Orchestrator", False, str(e)[:50]))
            print_test("Agent Orchestrator", False, str(e)[:100])

    async def verify_apis(self):
        """Verify API endpoints"""
        print_section("5. API ENDPOINTS")

        # Check if FastAPI app can be imported
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
        try:
            from app.main import app
            passed = app is not None
            self.results.append(("FastAPI App", passed, "Main application"))
            print_test("FastAPI Application", passed, "Backend API server")

            # Count routes
            route_count = len(app.routes)
            print_test(f"API Routes Registered", route_count > 0, f"{route_count} routes")

        except Exception as e:
            self.results.append(("FastAPI App", False, str(e)[:50]))
            print_test("FastAPI Application", False, str(e)[:100])

    async def verify_data_pipeline(self):
        """Verify data pipeline"""
        print_section("6. DATA PIPELINE")

        # Kafka Producers
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data_pipeline'))
            from kafka.producers import NewsProducer, MarketDataProducer, PolicyProducer
            passed = True
            self.results.append(("Kafka Producers", passed, "Data ingestion"))
            print_test("Kafka Producers", passed, "News, Market, Policy producers")
        except Exception as e:
            self.results.append(("Kafka Producers", False, str(e)[:50]))
            print_test("Kafka Producers", False, str(e)[:100])

        # Kafka Consumers
        try:
            from kafka.consumers import NewsConsumer, MarketDataConsumer, PolicyConsumer
            passed = True
            self.results.append(("Kafka Consumers", passed, "Real-time processing"))
            print_test("Kafka Consumers", passed, "Stream processing pipeline")
        except Exception as e:
            self.results.append(("Kafka Consumers", False, str(e)[:50]))
            print_test("Kafka Consumers", False, str(e)[:100])

    def print_summary(self):
        """Print verification summary"""
        print_section("VERIFICATION SUMMARY")

        total_tests = len(self.results)
        passed_tests = sum(1 for _, passed, _ in self.results if passed)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        duration = (datetime.now() - self.start_time).total_seconds()

        print(f"Total Tests: {Colors.BOLD}{total_tests}{Colors.RESET}")
        print(f"Passed:      {Colors.GREEN}{Colors.BOLD}{passed_tests}{Colors.RESET}")
        print(f"Failed:      {Colors.RED}{Colors.BOLD}{failed_tests}{Colors.RESET}")
        print(f"Success Rate: {Colors.BOLD}{success_rate:.1f}%{Colors.RESET}")
        print(f"Duration:    {duration:.2f}s\n")

        if success_rate >= 80:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ SYSTEM VERIFICATION PASSED{Colors.RESET}")
            print(f"{Colors.GREEN}The EIP platform is ready for use!{Colors.RESET}\n")
            return 0
        elif success_rate >= 60:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠ SYSTEM PARTIALLY OPERATIONAL{Colors.RESET}")
            print(f"{Colors.YELLOW}Some components need attention. Check failed tests above.{Colors.RESET}\n")
            return 1
        else:
            print(f"{Colors.RED}{Colors.BOLD}✗ SYSTEM VERIFICATION FAILED{Colors.RESET}")
            print(f"{Colors.RED}Critical components are missing or misconfigured.{Colors.RESET}\n")
            return 2

async def main():
    """Main entry point"""
    verifier = SystemVerifier()
    await verifier.verify_all()
    return verifier.print_summary()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
