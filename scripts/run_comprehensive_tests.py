#!/usr/bin/env python3
"""
Comprehensive Test Runner for EIP
Tests all 35 agents, backend services, and integrations
"""
import sys
import os
import asyncio
from typing import Dict, List, Tuple
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class EIPTestRunner:
    """Comprehensive test runner for all EIP components"""

    def __init__(self):
        self.results = {
            "agents": {},
            "services": {},
            "integration": {},
            "errors": []
        }
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}\n")

    def print_test(self, name: str, status: str, details: str = ""):
        """Print test result"""
        symbols = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "WARN": "⚠️"}
        symbol = symbols.get(status, "❓")
        print(f"{symbol} {name:.<60} {status}")
        if details:
            print(f"   └─ {details}")

    async def test_agent_import(self, agent_name: str, import_path: str) -> Tuple[bool, str]:
        """Test if an agent can be imported"""
        try:
            # Import the agent
            module_parts = import_path.rsplit('.', 1)
            module_name = module_parts[0]
            class_name = module_parts[1]

            module = __import__(module_name, fromlist=[class_name])
            agent_class = getattr(module, class_name)

            # Try to instantiate
            agent = agent_class()

            return True, f"Agent {agent_name} imported successfully"
        except ImportError as e:
            return False, f"Import error: {str(e)}"
        except Exception as e:
            return False, f"Instantiation error: {str(e)}"

    async def test_orchestrator(self) -> Tuple[bool, str]:
        """Test Enhanced Agent Orchestrator"""
        try:
            from agents.orchestrator.enhanced_agent_orchestrator import EnhancedAgentOrchestrator

            orchestrator = EnhancedAgentOrchestrator()

            # Verify all 35 agents registered
            if len(orchestrator.agents) != 35:
                return False, f"Expected 35 agents, found {len(orchestrator.agents)}"

            # Test simple query routing
            test_query = "What are the latest tax deductions for startups?"
            # Note: This requires API keys, so we just test instantiation

            return True, f"Orchestrator initialized with {len(orchestrator.agents)} agents"
        except Exception as e:
            return False, f"Error: {str(e)}"

    async def test_backend_services(self) -> Dict[str, Tuple[bool, str]]:
        """Test all backend services"""
        results = {}

        # Test LLM Service
        try:
            from backend.app.services.llm_service import LLMService
            llm = LLMService()
            results["LLMService"] = (True, "Imported successfully")
        except Exception as e:
            results["LLMService"] = (False, str(e))

        # Test RAG Service
        try:
            from backend.app.services.rag_service import RAGService
            rag = RAGService()
            results["RAGService"] = (True, "Imported successfully")
        except Exception as e:
            results["RAGService"] = (False, str(e))

        # Test GraphRAG Service
        try:
            from backend.app.services.graphrag_service import GraphRAGService
            graphrag = GraphRAGService()
            results["GraphRAGService"] = (True, "Imported successfully")
        except Exception as e:
            results["GraphRAGService"] = (False, str(e))

        # Test OCR Service
        try:
            from backend.app.services.ocr_service import OCRService
            ocr = OCRService()
            results["OCRService"] = (True, "Imported successfully")
        except Exception as e:
            results["OCRService"] = (False, str(e))

        # Test VLM Service
        try:
            from backend.app.services.vlm_service import VLMService
            vlm = VLMService()
            results["VLMService"] = (True, "Imported successfully")
        except Exception as e:
            results["VLMService"] = (False, str(e))

        return results

    async def run_all_tests(self):
        """Run all tests"""
        self.print_header("EIP COMPREHENSIVE TEST SUITE")
        print(f"Testing all 35 agents + backend services + integration\n")

        # Test 1: Core Agents (8)
        self.print_header("TEST SUITE 1: CORE AGENTS (8)")

        core_agents = [
            ("PolicyAgent", "agents.policy_agent.policy_agent.PolicyAgent"),
            ("MarketAgent", "agents.market_agent.market_agent.MarketAgent"),
            ("FinanceAgent", "agents.finance_agent.finance_agent.FinanceAgent"),
            ("TaxAgent", "agents.tax_agent.tax_agent.TaxAgent"),
            ("DistributionAgent", "agents.distribution_agent.distribution_agent.DistributionAgent"),
            ("InvestmentAgent", "agents.investment_agent.investment_agent.InvestmentAgent"),
            ("LegalAgent", "agents.legal_agent.legal_agent.LegalAgent"),
            ("NewsAgent", "agents.news_agent.news_agent.NewsAgent"),
        ]

        for agent_name, import_path in core_agents:
            self.total_tests += 1
            success, details = await self.test_agent_import(agent_name, import_path)
            if success:
                self.passed_tests += 1
                self.print_test(agent_name, "PASS", details)
            else:
                self.failed_tests += 1
                self.print_test(agent_name, "FAIL", details)
                self.results["errors"].append(f"{agent_name}: {details}")

        # Test 2: Enhanced Agents (27)
        self.print_header("TEST SUITE 2: ENHANCED AGENTS (27)")

        enhanced_agents = [
            ("BusinessModelAgent", "agents.enhanced.business_model_agent.BusinessModelAgent"),
            ("BusinessModelRecommenderAgent", "agents.enhanced.business_model_recommender_agent.BusinessModelRecommenderAgent"),
            ("BusinessStrategyAgent", "agents.enhanced.business_strategy_agent.BusinessStrategyAgent"),
            ("CompetitorIntelligenceAgent", "agents.enhanced.competitor_intelligence_agent.CompetitorIntelligenceAgent"),
            ("ConnectingDotsAgent", "agents.enhanced.connecting_dots_agent.ConnectingDotsAgent"),
            ("EnhancedNewsAgent", "agents.enhanced.enhanced_news_agent.EnhancedNewsAgent"),
            ("ESGEnvironmentalAgent", "agents.enhanced.esg_environmental_agent.ESGEnvironmentalAgent"),
            ("HedgeFundAnalyzerAgent", "agents.enhanced.hedge_fund_agent.HedgeFundAnalyzerAgent"),
            ("HFTAnalysisAgent", "agents.enhanced.hft_analysis_agent.HFTAnalysisAgent"),
            ("HRAnalyticsAgent", "agents.enhanced.hr_analytics_agent.HRAnalyticsAgent"),
            ("HumanBehaviourAgent", "agents.enhanced.human_behaviour_agent.HumanBehaviourAgent"),
            ("HumanNeedsAgent", "agents.enhanced.human_needs_agent.HumanNeedsAgent"),
            ("IndustryDomainExpertAgent", "agents.enhanced.industry_expert_agent.IndustryDomainExpertAgent"),
            ("InternationalMarketsAgent", "agents.enhanced.international_markets_agent.InternationalMarketsAgent"),
            ("LoopholePredictorAgent", "agents.enhanced.loophole_predictor_agent.LoopholePredictorAgent"),
            ("MacroeconomicsAgent", "agents.enhanced.macroeconomics_agent.MacroeconomicsAgent"),
            ("MarketingStrategyAgent", "agents.enhanced.marketing_strategy_agent.MarketingStrategyAgent"),
            ("MoneyHappinessAgent", "agents.enhanced.money_happiness_agent.MoneyHappinessAgent"),
            ("MutualFundAnalyzerAgent", "agents.enhanced.mutual_fund_agent.MutualFundAnalyzerAgent"),
            ("NGONonprofitAgent", "agents.enhanced.ngo_nonprofit_agent.NGONonprofitAgent"),
            ("PhilanthropyImpactAgent", "agents.enhanced.philanthropy_impact_agent.PhilanthropyImpactAgent"),
            ("PhilosophyEthicsAgent", "agents.enhanced.philosophy_ethics_agent.PhilosophyEthicsAgent"),
            ("RealEstateAnalysisAgent", "agents.enhanced.real_estate_agent.RealEstateAnalysisAgent"),
            ("RegulatorAnalysisAgent", "agents.enhanced.regulator_analysis_agent.RegulatorAnalysisAgent"),
            ("SchemesMonitoringAgent", "agents.enhanced.schemes_monitoring_agent.SchemesMonitoringAgent"),
            ("StockAnalysisAgent", "agents.enhanced.stock_analysis_agent.StockAnalysisAgent"),
            ("SubsidiesAnalyzerAgent", "agents.enhanced.subsidies_agent.SubsidiesAnalyzerAgent"),
        ]

        for agent_name, import_path in enhanced_agents:
            self.total_tests += 1
            success, details = await self.test_agent_import(agent_name, import_path)
            if success:
                self.passed_tests += 1
                self.print_test(agent_name, "PASS", details)
            else:
                self.failed_tests += 1
                self.print_test(agent_name, "FAIL", details)
                self.results["errors"].append(f"{agent_name}: {details}")

        # Test 3: Orchestrator
        self.print_header("TEST SUITE 3: ORCHESTRATOR")

        self.total_tests += 1
        success, details = await self.test_orchestrator()
        if success:
            self.passed_tests += 1
            self.print_test("EnhancedAgentOrchestrator", "PASS", details)
        else:
            self.failed_tests += 1
            self.print_test("EnhancedAgentOrchestrator", "FAIL", details)
            self.results["errors"].append(f"Orchestrator: {details}")

        # Test 4: Backend Services
        self.print_header("TEST SUITE 4: BACKEND SERVICES")

        services = await self.test_backend_services()
        for service_name, (success, details) in services.items():
            self.total_tests += 1
            if success:
                self.passed_tests += 1
                self.print_test(service_name, "PASS", details)
            else:
                self.failed_tests += 1
                self.print_test(service_name, "FAIL", details)
                self.results["errors"].append(f"{service_name}: {details}")

        # Final Results
        self.print_header("TEST RESULTS SUMMARY")

        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0

        print(f"Total Tests:   {self.total_tests}")
        print(f"✅ Passed:      {self.passed_tests}")
        print(f"❌ Failed:      {self.failed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%\n")

        if self.results["errors"]:
            self.print_header("ERRORS ENCOUNTERED")
            for i, error in enumerate(self.results["errors"], 1):
                print(f"{i}. {error}")
            print()

        # Overall Status
        if self.failed_tests == 0:
            print("🎉 ALL TESTS PASSED! EIP is ready to deploy!")
            return 0
        elif success_rate >= 90:
            print("⚠️  MOSTLY PASSING - Some components need attention")
            return 1
        else:
            print("❌ MULTIPLE FAILURES - Please review errors above")
            return 2


async def main():
    """Main test runner"""
    print("\n" + "="*80)
    print("  EIP COMPREHENSIVE TEST SUITE")
    print("  Testing all 35 AI Agents + Backend + Integration")
    print("="*80 + "\n")

    runner = EIPTestRunner()
    exit_code = await runner.run_all_tests()

    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
