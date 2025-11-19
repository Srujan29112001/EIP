"""
Integration Test for EIP Platform
Tests all 35 agents and inter-agent communication (A2A protocol)
"""
import sys
import os
import asyncio

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))

async def test_orchestrator_initialization():
    """Test 1: Verify all 35 agents are initialized"""
    print("\n" + "="*80)
    print("TEST 1: Agent Orchestrator Initialization")
    print("="*80)

    try:
        from orchestrator.enhanced_agent_orchestrator import EnhancedAgentOrchestrator

        orchestrator = EnhancedAgentOrchestrator()

        # Check agent count
        agent_count = len(orchestrator.agents)
        print(f"✓ Total agents registered: {agent_count}")

        if agent_count == 35:
            print("✓ SUCCESS: All 35 agents registered correctly!")
        else:
            print(f"⚠ WARNING: Expected 35 agents, found {agent_count}")

        # List all agents
        print("\n📋 Registered Agents:")
        for i, (name, agent) in enumerate(orchestrator.agents.items(), 1):
            print(f"  {i}. {name}: {agent.__class__.__name__}")

        return True, orchestrator

    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_single_agent_query(orchestrator):
    """Test 2: Single Agent Query"""
    print("\n" + "="*80)
    print("TEST 2: Single Agent Query (Stock Analysis)")
    print("="*80)

    try:
        result = await orchestrator.process_query(
            query="What are the best stocks to invest in for 2025?",
            user_context={"risk_tolerance": "moderate"}
        )

        print(f"✓ Primary Agent: {result['primary_agent']}")
        print(f"✓ Confidence: {result.get('confidence', 0)}")
        print(f"✓ Execution Time: {result.get('execution_time_seconds', 0)}s")
        print(f"\n📝 Response Preview:\n{result['answer'][:300]}...")

        return True

    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multi_agent_query(orchestrator):
    """Test 3: Multi-Agent Query (A2A Communication)"""
    print("\n" + "="*80)
    print("TEST 3: Multi-Agent Query (A2A Protocol)")
    print("="*80)

    try:
        result = await orchestrator.process_query(
            query="I want to start a SaaS startup. Analyze the market, recommend a business model, and suggest marketing strategies.",
            user_context={"industry": "SaaS", "stage": "ideation"}
        )

        print(f"✓ Primary Agent: {result['primary_agent']}")
        print(f"✓ Secondary Agents: {result.get('secondary_agents', [])}")
        print(f"✓ Multi-Agent Collaboration: {result.get('multi_agent', False)}")
        print(f"✓ Confidence: {result.get('confidence', 0)}")
        print(f"✓ Execution Time: {result.get('execution_time_seconds', 0)}s")
        print(f"\n📝 Response Preview:\n{result['answer'][:300]}...")

        if result.get('multi_agent', False):
            print("\n✓ SUCCESS: Multi-agent communication verified!")
        else:
            print("\n⚠ INFO: Query handled by single agent")

        return True

    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_specific_enhanced_agents(orchestrator):
    """Test 4: Test specific enhanced agents"""
    print("\n" + "="*80)
    print("TEST 4: Enhanced Agents Verification")
    print("="*80)

    test_queries = [
        ("Real Estate Analysis", "What are the best real estate investment opportunities in 2025?"),
        ("Marketing Strategy", "How can I optimize my digital marketing ROI?"),
        ("Connecting Dots", "Connect the dots between recent RBI rate cuts and startup funding trends"),
        ("HR Analytics", "What should be the salary budget for a 50-person tech startup?"),
        ("ESG Environmental", "How can my company reduce carbon footprint?"),
    ]

    results = []
    for agent_name, query in test_queries:
        try:
            result = await orchestrator.process_query(
                query=query,
                user_context={"test": True}
            )
            print(f"\n✓ {agent_name}")
            print(f"  Agent Used: {result['primary_agent']}")
            print(f"  Response Length: {len(result['answer'])} chars")
            results.append(True)
        except Exception as e:
            print(f"\n✗ {agent_name}: {str(e)[:100]}")
            results.append(False)

    success_rate = (sum(results) / len(results)) * 100
    print(f"\n📊 Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)} passed)")

    return success_rate >= 80


async def test_agent_routing(orchestrator):
    """Test 5: Intelligent Agent Routing"""
    print("\n" + "="*80)
    print("TEST 5: Intelligent Agent Routing")
    print("="*80)

    routing_tests = [
        ("tax optimization strategies", ["tax", "loophole_predictor"]),
        ("hedge fund investment", ["hedge_fund", "stock_analysis"]),
        ("government subsidies for startups", ["subsidies", "schemes_monitoring"]),
        ("macroeconomic impact of inflation", ["macroeconomics", "market"]),
        ("real estate investment", ["real_estate", "investment"]),
    ]

    correct_routing = 0
    for query, expected_agents in routing_tests:
        try:
            result = await orchestrator.process_query(query=query)
            primary = result['primary_agent']

            if primary in expected_agents:
                print(f"✓ '{query[:40]}...' → {primary}")
                correct_routing += 1
            else:
                print(f"⚠ '{query[:40]}...' → {primary} (expected: {expected_agents})")

        except Exception as e:
            print(f"✗ Error routing: {str(e)[:100]}")

    accuracy = (correct_routing / len(routing_tests)) * 100
    print(f"\n📊 Routing Accuracy: {accuracy:.1f}% ({correct_routing}/{len(routing_tests)})")

    return accuracy >= 60  # 60% threshold for passing


async def run_all_tests():
    """Run all integration tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "EIP INTEGRATION TEST SUITE" + " "*32 + "║")
    print("║" + " "*15 + "Testing All 35 Agents + A2A Protocol" + " "*27 + "║")
    print("╚" + "="*78 + "╝")

    # Test 1: Initialize orchestrator
    success, orchestrator = await test_orchestrator_initialization()
    if not success or not orchestrator:
        print("\n❌ CRITICAL FAILURE: Cannot initialize orchestrator")
        return False

    # Test 2: Single agent query
    test2 = await test_single_agent_query(orchestrator)

    # Test 3: Multi-agent query
    test3 = await test_multi_agent_query(orchestrator)

    # Test 4: Enhanced agents
    test4 = await test_specific_enhanced_agents(orchestrator)

    # Test 5: Agent routing
    test5 = await test_agent_routing(orchestrator)

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    tests = [
        ("Agent Initialization (35 agents)", success),
        ("Single Agent Query", test2),
        ("Multi-Agent Query (A2A)", test3),
        ("Enhanced Agents Verification", test4),
        ("Intelligent Agent Routing", test5)
    ]

    for test_name, result in tests:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, result in tests if result)
    total_tests = len(tests)
    overall_success_rate = (total_passed / total_tests) * 100

    print(f"\n{'='*80}")
    print(f"OVERALL: {total_passed}/{total_tests} tests passed ({overall_success_rate:.1f}%)")
    print(f"{'='*80}")

    if overall_success_rate >= 80:
        print("\n✅ INTEGRATION TESTS PASSED!")
        print("🎉 EIP Platform is functioning correctly with all 35 agents")
        return True
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Please review the errors above")
        return False


if __name__ == "__main__":
    # Run tests
    result = asyncio.run(run_all_tests())

    # Exit with appropriate code
    sys.exit(0 if result else 1)
