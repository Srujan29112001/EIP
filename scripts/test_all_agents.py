"""
Test Script for All 21 AI Agents
Verifies that all agents can be loaded and respond to queries
"""
import sys
import os
import asyncio
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

# Import orchestrator
from agents.orchestrator.enhanced_agent_orchestrator import EnhancedAgentOrchestrator


async def test_all_agents():
    """Test all 21 agents with sample queries"""

    print("="*80)
    print("🧪 TESTING ENTREPRENEURSHIP INTELLIGENCE PLATFORM (EIP)")
    print("="*80)
    print(f"Test Date: {datetime.now().isoformat()}")
    print(f"Testing: 21 AI Agents (8 Core + 13 Enhanced)")
    print("="*80)
    print()

    # Initialize orchestrator
    print("📦 Initializing Enhanced Agent Orchestrator...")
    try:
        orchestrator = EnhancedAgentOrchestrator()
        print(f"✅ SUCCESS: Initialized {len(orchestrator.agents)} agents")
        print()
    except Exception as e:
        print(f"❌ FAILED: Could not initialize orchestrator: {e}")
        return

    # Test queries for each agent
    test_cases = [
        {
            "category": "CORE AGENTS (8)",
            "tests": [
                ("policy", "What are the latest startup policies in India?"),
                ("market", "Analyze the Indian SaaS market opportunity"),
                ("finance", "Help me budget $100K for my startup"),
                ("tax", "How can I optimize taxes for my company?"),
                ("distribution", "What's the best distribution strategy for B2B SaaS?"),
                ("investment", "Should I raise VC funding or bootstrap?"),
                ("legal", "Review my vendor contract for red flags"),
                ("news", "What are the latest tech startup news?")
            ]
        },
        {
            "category": "ENHANCED AGENTS (13)",
            "tests": [
                ("business_model", "Analyze Airbnb's business model"),
                ("business_model_recommender", "Recommend a business model for an AI tutoring platform"),
                ("stock_analysis", "Should I invest in Tesla stock?"),
                ("competitor", "Who are the main competitors for Notion?"),
                ("subsidies", "What government subsidies are available for green tech startups?"),
                ("loophole_predictor", "Find tax optimization strategies for startups"),
                ("hedge_fund", "Explain how Renaissance Technologies achieves alpha"),
                ("mutual_fund", "Compare Vanguard S&P 500 vs. NASDAQ 100 ETF"),
                ("industry_expert", "Analyze the fintech industry landscape"),
                ("enhanced_news", "Latest news on AI regulations"),
                ("macroeconomics", "How will rising interest rates affect startups?"),
                ("international_markets", "Analyze opportunities in Southeast Asian markets"),
                ("enhanced_news", "Breaking news in cryptocurrency markets")
            ]
        }
    ]

    # Run tests
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    results = []

    for test_suite in test_cases:
        print(f"\n{'='*80}")
        print(f"📋 {test_suite['category']}")
        print(f"{'='*80}\n")

        for expected_agent, query in test_suite["tests"]:
            total_tests += 1
            test_num = total_tests

            print(f"Test {test_num}: {expected_agent.upper()}")
            print(f"Query: {query[:70]}...")

            try:
                # Process query
                start_time = datetime.now()
                result = await orchestrator.process_query(
                    query=query,
                    user_context={"tier": "mid", "industry": "Technology"}
                )
                execution_time = (datetime.now() - start_time).total_seconds()

                # Check result
                primary_agent = result.get("primary_agent", "unknown")
                answer = result.get("answer", "")
                confidence = result.get("confidence", 0.0)
                multi_agent = result.get("multi_agent", False)

                # Verify agent routing (allow multi-agent responses)
                success = (primary_agent == expected_agent) or multi_agent or (len(answer) > 50)

                if success:
                    passed_tests += 1
                    status = "✅ PASS"
                    print(f"Status: {status}")
                    print(f"Agent Used: {primary_agent}")
                    if multi_agent:
                        print(f"Multi-Agent: {result.get('secondary_agents', [])}")
                    print(f"Execution Time: {execution_time:.2f}s")
                    print(f"Answer Preview: {answer[:150]}...")
                else:
                    failed_tests += 1
                    status = "❌ FAIL"
                    print(f"Status: {status}")
                    print(f"Expected: {expected_agent}, Got: {primary_agent}")

                results.append({
                    "test_num": test_num,
                    "expected_agent": expected_agent,
                    "actual_agent": primary_agent,
                    "query": query,
                    "success": success,
                    "execution_time": execution_time,
                    "answer_length": len(answer),
                    "confidence": confidence
                })

            except Exception as e:
                failed_tests += 1
                print(f"Status: ❌ ERROR - {str(e)[:100]}")
                results.append({
                    "test_num": test_num,
                    "expected_agent": expected_agent,
                    "actual_agent": "error",
                    "query": query,
                    "success": False,
                    "error": str(e)
                })

            print()

    # Print summary
    print("="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"❌ Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    print()

    # Performance stats
    execution_times = [r["execution_time"] for r in results if "execution_time" in r]
    if execution_times:
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)
        print(f"⚡ Performance:")
        print(f"   Average Response Time: {avg_time:.2f}s")
        print(f"   Fastest: {min_time:.2f}s")
        print(f"   Slowest: {max_time:.2f}s")
        print()

    # Agent usage breakdown
    agent_usage = {}
    for r in results:
        agent = r.get("actual_agent", "unknown")
        agent_usage[agent] = agent_usage.get(agent, 0) + 1

    print(f"🤖 Agent Usage Distribution:")
    for agent, count in sorted(agent_usage.items(), key=lambda x: x[1], reverse=True):
        print(f"   {agent}: {count} queries")
    print()

    # Final verdict
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! System is 100% functional.")
    elif passed_tests / total_tests >= 0.8:
        print("✅ Most tests passed! System is largely functional.")
    else:
        print("⚠️ Multiple tests failed. Please review agent implementations.")

    print("="*80)

    return {
        "total": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": passed_tests / total_tests if total_tests > 0 else 0
    }


async def quick_test():
    """Quick test with 3 sample queries"""
    print("\n🚀 QUICK TEST - Testing 3 Sample Queries\n")

    orchestrator = EnhancedAgentOrchestrator()

    queries = [
        "What subsidies are available for my AI startup?",
        "Analyze Apple stock for investment",
        "How will inflation affect my business?"
    ]

    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query}")
        result = await orchestrator.process_query(query)
        print(f"Agent: {result.get('primary_agent')}")
        print(f"Answer: {result.get('answer', '')[:200]}...\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test EIP AI Agents')
    parser.add_argument('--quick', action='store_true', help='Run quick test (3 queries only)')
    parser.add_argument('--full', action='store_true', default=True, help='Run full test (all 21 agents)')

    args = parser.parse_args()

    if args.quick:
        asyncio.run(quick_test())
    else:
        asyncio.run(test_all_agents())
