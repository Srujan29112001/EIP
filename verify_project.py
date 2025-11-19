"""
Project Verification Script for EIP Platform
Verifies all components are properly set up WITHOUT requiring API keys
"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))

def verify_agent_imports():
    """Verify all 35 agents can be imported"""
    print("\n" + "="*80)
    print("VERIFICATION 1: Agent Imports (35 agents)")
    print("="*80)

    agents_to_test = [
        # Core agents (8)
        ("policy_agent.policy_agent", "PolicyAgent"),
        ("market_agent.market_agent", "MarketAgent"),
        ("finance_agent.finance_agent", "FinanceAgent"),
        ("tax_agent.tax_agent", "TaxAgent"),
        ("distribution_agent.distribution_agent", "DistributionAgent"),
        ("investment_agent.investment_agent", "InvestmentAgent"),
        ("legal_agent.legal_agent", "LegalAgent"),
        ("news_agent.news_agent", "NewsAgent"),

        # Enhanced agents - Phase 2 (12)
        ("enhanced.business_model_agent", "BusinessModelAgent"),
        ("enhanced.stock_analysis_agent", "StockAnalysisAgent"),
        ("enhanced.competitor_intelligence_agent", "CompetitorIntelligenceAgent"),
        ("enhanced.subsidies_agent", "SubsidiesAnalyzerAgent"),
        ("enhanced.business_model_recommender_agent", "BusinessModelRecommenderAgent"),
        ("enhanced.loophole_predictor_agent", "LoopholePredictorAgent"),
        ("enhanced.hedge_fund_agent", "HedgeFundAnalyzerAgent"),
        ("enhanced.mutual_fund_agent", "MutualFundAnalyzerAgent"),
        ("enhanced.industry_expert_agent", "IndustryDomainExpertAgent"),
        ("enhanced.enhanced_news_agent", "EnhancedNewsAgent"),
        ("enhanced.macroeconomics_agent", "MacroeconomicsAgent"),
        ("enhanced.international_markets_agent", "InternationalMarketsAgent"),

        # Enhanced agents - Phase 3 (15)
        ("enhanced.real_estate_agent", "RealEstateAnalysisAgent"),
        ("enhanced.marketing_strategy_agent", "MarketingStrategyAgent"),
        ("enhanced.business_strategy_agent", "BusinessStrategyAgent"),
        ("enhanced.connecting_dots_agent", "ConnectingDotsAgent"),
        ("enhanced.hft_analysis_agent", "HFTAnalysisAgent"),
        ("enhanced.hr_analytics_agent", "HRAnalyticsAgent"),
        ("enhanced.human_behaviour_agent", "HumanBehaviourAgent"),
        ("enhanced.human_needs_agent", "HumanNeedsAgent"),
        ("enhanced.esg_environmental_agent", "ESGEnvironmentalAgent"),
        ("enhanced.philosophy_ethics_agent", "PhilosophyEthicsAgent"),
        ("enhanced.money_happiness_agent", "MoneyHappinessAgent"),
        ("enhanced.ngo_nonprofit_agent", "NGONonProfitAgent"),
        ("enhanced.philanthropy_impact_agent", "PhilanthropyImpactAgent"),
        ("enhanced.schemes_monitoring_agent", "SchemesMonitoringAgent"),
        ("enhanced.regulator_analysis_agent", "RegulatorAnalysisAgent"),
    ]

    imported_count = 0
    failed = []

    for module_path, class_name in agents_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            print(f"✓ {class_name}")
            imported_count += 1
        except Exception as e:
            print(f"✗ {class_name}: {str(e)[:80]}")
            failed.append((class_name, str(e)))

    print(f"\n📊 Result: {imported_count}/{len(agents_to_test)} agents imported successfully")

    if imported_count == len(agents_to_test):
        print("✅ ALL AGENTS CAN BE IMPORTED!")
        return True
    else:
        print(f"\n⚠ {len(failed)} agents failed to import:")
        for name, error in failed:
            print(f"  - {name}: {error[:100]}")
        return False


def verify_backend_services():
    """Verify backend services can be imported"""
    print("\n" + "="*80)
    print("VERIFICATION 2: Backend Services")
    print("="*80)

    services = [
        ("services.llm_service", "LLMService"),
        ("services.rag_service", "RAGService"),
        ("services.graphrag_service", "GraphRAGService"),
        ("services.ocr_service", "OCRService"),
        ("services.vlm_service", "VLMService"),
    ]

    imported_count = 0
    for module_path, class_name in services:
        try:
            module = __import__(module_path, fromlist=[class_name])
            service_class = getattr(module, class_name)
            print(f"✓ {class_name}")
            imported_count += 1
        except Exception as e:
            print(f"⚠ {class_name}: {str(e)[:60]}")

    print(f"\n📊 Result: {imported_count}/{len(services)} services imported")
    return imported_count == len(services)


def verify_file_structure():
    """Verify all required files and directories exist"""
    print("\n" + "="*80)
    print("VERIFICATION 3: File Structure")
    print("="*80)

    required_paths = [
        ("agents/base_agent.py", "Base Agent"),
        ("agents/orchestrator/enhanced_agent_orchestrator.py", "Enhanced Orchestrator"),
        ("backend/app/main.py", "FastAPI Backend"),
        ("backend/app/api/v1/chat.py", "Chat API"),
        ("frontend/app.py", "Streamlit Frontend"),
        ("docker-compose.yml", "Docker Compose"),
        ("requirements.txt", "Requirements"),
        ("README.md", "README"),
    ]

    found_count = 0
    for path, name in required_paths:
        full_path = os.path.join(os.path.dirname(__file__), path)
        if os.path.exists(full_path):
            print(f"✓ {name}")
            found_count += 1
        else:
            print(f"✗ {name} (missing: {path})")

    print(f"\n📊 Result: {found_count}/{len(required_paths)} required files found")
    return found_count == len(required_paths)


def count_lines_of_code():
    """Count total lines of code in the project"""
    print("\n" + "="*80)
    print("VERIFICATION 4: Code Statistics")
    print("="*80)

    import subprocess

    try:
        # Count Python files
        result = subprocess.run(
            ["find", ".", "-name", "*.py", "-type", "f"],
            capture_output=True,
            text=True
        )
        py_files = result.stdout.strip().split('\n')
        py_file_count = len([f for f in py_files if f])

        # Count lines (excluding __pycache__, .git, etc.)
        result = subprocess.run(
            ["find", ".", "-name", "*.py", "-type", "f", "-not", "-path", "*/__pycache__/*", "-not", "-path", "*/.git/*"],
            capture_output=True,
            text=True
        )
        files = result.stdout.strip().split('\n')

        total_lines = 0
        for file in files:
            if file:
                try:
                    with open(file, 'r') as f:
                        total_lines += len(f.readlines())
                except:
                    pass

        print(f"✓ Total Python files: {py_file_count}")
        print(f"✓ Total lines of code: {total_lines:,}")

        return True

    except Exception as e:
        print(f"⚠ Could not count lines: {e}")
        return False


def verify_orchestrator_structure():
    """Verify the orchestrator has all 35 agents registered"""
    print("\n" + "="*80)
    print("VERIFICATION 5: Orchestrator Configuration")
    print("="*80)

    try:
        with open('agents/orchestrator/enhanced_agent_orchestrator.py', 'r') as f:
            content = f.read()

        # Count agent registrations in the agents dictionary
        import re
        agent_pattern = r'"([^"]+)":\s*self\.'
        agents_found = re.findall(agent_pattern, content)

        print(f"✓ Agents registered in orchestrator: {len(agents_found)}")

        if len(agents_found) >= 35:
            print("✅ ALL 35 AGENTS ARE REGISTERED!")
            return True
        else:
            print(f"⚠ Expected 35, found {len(agents_found)}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all verifications"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "EIP PLATFORM VERIFICATION SUITE" + " "*32 + "║")
    print("║" + " "*20 + "Verifying All Components" + " "*34 + "║")
    print("╚" + "="*78 + "╝")

    results = []

    results.append(("Agent Imports (35 agents)", verify_agent_imports()))
    results.append(("Backend Services", verify_backend_services()))
    results.append(("File Structure", verify_file_structure()))
    results.append(("Code Statistics", count_lines_of_code()))
    results.append(("Orchestrator Configuration", verify_orchestrator_structure()))

    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)

    for test_name, result in results:
        status = "✅ PASSED" if result else "⚠ NEEDS ATTENTION"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, result in results if result)
    total_tests = len(results)
    success_rate = (total_passed / total_tests) * 100

    print(f"\n{'='*80}")
    print(f"OVERALL: {total_passed}/{total_tests} verifications passed ({success_rate:.1f}%)")
    print(f"{'='*80}")

    if success_rate == 100:
        print("\n✅ PROJECT VERIFICATION SUCCESSFUL!")
        print("🎉 All 35 agents and components are properly configured")
        print("\n📝 Next Steps:")
        print("   1. Configure API keys in .env file (OPENAI_API_KEY, ANTHROPIC_API_KEY)")
        print("   2. Run 'docker-compose up -d' to start infrastructure")
        print("   3. Run 'uvicorn backend.app.main:app --reload' to start backend")
        print("   4. Run 'streamlit run frontend/streamlit/app.py' to start frontend")
        return True
    else:
        print("\n⚠️ SOME VERIFICATIONS NEED ATTENTION")
        print("Please review the issues above")
        return False


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
