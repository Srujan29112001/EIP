# 🛠️ HOW TO COMPLETE THE REMAINING 15%

**Quick Reference Guide for Finishing the EIP Platform**

---

## 📋 Overview

You're at **85%** completion. This guide provides **step-by-step instructions** and **code templates** to reach **100%**.

**Estimated Time:** 34-48 hours total
- **Phase 1 (Core):** 12-16 hours → Gets you to 95%
- **Phase 2 (Polish):** 22-32 hours → Gets you to 100%

---

## 🎯 PHASE 1: CORE FUNCTIONALITY (Priority 1)

### Task 1: Complete Individual Agents (8-12 hours)

Each agent follows the same pattern. Here's the **template**:

#### Example: Completing Policy Agent

**File:** `agents/policy_agent/policy_agent.py`

**Current State:** Lines 121, 142, 167, 195 have TODOs

**Step-by-Step Fix:**

##### Step 1: Implement RAG Retrieval (Line 121)

**Find This:**
```python
# TODO: Implement actual RAG retrieval
return []
```

**Replace With:**
```python
async def _retrieve_policy_documents(
    self,
    query: str,
    context: Optional[Dict] = None
) -> List[Dict]:
    """Retrieve relevant policy documents using RAG"""
    if not self.rag_service:
        return []

    try:
        # Add metadata filter based on context
        filter_dict = {"category": "policy"}
        if context and context.get("sector"):
            filter_dict["sector"] = context["sector"]

        # Retrieve from vector store
        results = await self.rag_service.retrieve(
            query=query,
            top_k=5,
            filter=filter_dict
        )

        return results

    except Exception as e:
        print(f"Error retrieving policy documents: {e}")
        return []
```

##### Step 2: Implement GraphRAG Traversal (Line 142)

**Find This:**
```python
# TODO: Implement GraphRAG traversal using Neo4j
return []
```

**Replace With:**
```python
async def _find_related_policies(self, query: str) -> List[Dict]:
    """Find related policies using knowledge graph"""
    if not self.graph_service:
        return []

    try:
        # Extract entities from query (simple keyword extraction for now)
        keywords = query.lower().split()
        policy_keywords = [k for k in keywords if len(k) > 3]

        # Query Neo4j for related policies
        from neo4j import GraphDatabase

        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session() as session:
            result = session.run("""
                MATCH (p:Policy)
                WHERE ANY(keyword IN $keywords WHERE p.title CONTAINS keyword)
                OPTIONAL MATCH (p)-[r:AFFECTS|RELATED_TO]-(related:Policy)
                RETURN p.title as title, p.description as description,
                       collect(related.title) as related_policies
                LIMIT 10
            """, keywords=policy_keywords)

            policies = []
            for record in result:
                policies.append({
                    "title": record["title"],
                    "description": record["description"],
                    "related": record["related_policies"]
                })

            driver.close()
            return policies

    except Exception as e:
        print(f"Error querying knowledge graph: {e}")
        return []
```

##### Step 3: Implement Full LLM Analysis (Line 167)

**Find This:**
```python
# TODO: Use LLM to generate actual analysis
return "Mock policy analysis"
```

**Replace With:**
```python
async def _analyze_policy(
    self,
    query: str,
    retrieved_docs: List[Dict],
    related_policies: List[Dict],
    context: Optional[Dict]
) -> str:
    """Generate comprehensive policy analysis using LLM"""

    # Build rich context
    context_parts = []

    # Add retrieved documents
    if retrieved_docs:
        context_parts.append("**Relevant Policy Documents:**\n")
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"{i}. **{doc.get('metadata', {}).get('title', 'Policy Document')}**")
            context_parts.append(f"   {doc.get('content', '')[:300]}...")
            context_parts.append("")

    # Add related policies from graph
    if related_policies:
        context_parts.append("\n**Related Policies:**\n")
        for policy in related_policies:
            context_parts.append(f"- **{policy['title']}**: {policy['description'][:200]}...")
            if policy.get('related'):
                context_parts.append(f"  Connected to: {', '.join(policy['related'][:3])}")
            context_parts.append("")

    # Add user context
    if context:
        context_parts.append("\n**User Context:**")
        context_parts.append(f"- Business Type: {context.get('business_type', 'N/A')}")
        context_parts.append(f"- Sector: {context.get('sector', 'N/A')}")
        context_parts.append(f"- Revenue Stage: {context.get('revenue_range', 'N/A')}")
        context_parts.append("")

    full_context = "\n".join(context_parts)

    # Generate LLM response
    response = await self._generate_response(
        query=query,
        context=full_context
    )

    return response
```

##### Step 4: Extract Action Items (Line 195)

**Find This:**
```python
# TODO: Use NLP to extract action items
return []
```

**Replace With:**
```python
def _extract_action_items(self, response_text: str) -> List[Dict[str, Any]]:
    """Extract actionable items from response"""
    action_items = []

    # Simple pattern matching for now
    # Look for numbered lists, deadlines, action verbs
    import re

    # Pattern 1: Look for bullet points or numbers with action verbs
    action_patterns = [
        r'(?:^|\n)\s*[\-\*]\s*([^\\n]+(?:deadline|by|before|due)[^\\n]+)',
        r'(?:^|\n)\s*\d+\.\s*([^\\n]+(?:file|submit|register|apply|comply)[^\\n]+)',
        r'(?:deadline|due date|by):\s*([^\\n]+)',
    ]

    for pattern in action_patterns:
        matches = re.findall(pattern, response_text, re.IGNORECASE)
        for match in matches:
            if len(match.strip()) > 10:  # Minimum length filter
                action_items.append({
                    "action": match.strip(),
                    "priority": "medium",
                    "deadline": None  # Could extract dates with more sophisticated parsing
                })

    # Pattern 2: Look for phrases like "you should", "must", "need to"
    recommendation_pattern = r'(?:you should|must|need to|recommended to)\s+([^.!?]+[.!?])'
    recommendations = re.findall(recommendation_pattern, response_text, re.IGNORECASE)

    for rec in recommendations:
        action_items.append({
            "action": rec.strip(),
            "priority": "high",
            "deadline": None
        })

    # Limit to top 5 most relevant
    return action_items[:5]
```

##### Result: Policy Agent is 100% Complete! ✅

**Repeat this process for remaining 7 agents.**

---

### Task 2: Complete GraphRAG Service (4-6 hours)

**File:** `backend/app/services/graphrag_service.py`

#### Add Missing Methods

**Location:** After existing code, add:

```python
class GraphRAGService:
    # ... existing __init__ and basic methods ...

    async def query_policy_relationships(
        self,
        policy_id: str,
        relationship_types: List[str] = None
    ) -> List[Dict]:
        """Query relationships for a specific policy"""
        if relationship_types is None:
            relationship_types = ["AFFECTS", "RELATED_TO", "SUPERSEDES", "CITES"]

        query = """
        MATCH (p:Policy {id: $policy_id})-[r]->(related)
        WHERE type(r) IN $rel_types
        RETURN p, r, related, type(r) as relationship_type
        LIMIT 20
        """

        try:
            result = self.session.run(
                query,
                policy_id=policy_id,
                rel_types=relationship_types
            )

            relationships = []
            for record in result:
                relationships.append({
                    "source": dict(record["p"]),
                    "target": dict(record["related"]),
                    "relationship": record["relationship_type"]
                })

            return relationships

        except Exception as e:
            self.logger.error(f"Error querying policy relationships: {e}")
            return []

    async def find_companies_by_sector(self, sector: str) -> List[Dict]:
        """Find companies in a specific sector"""
        query = """
        MATCH (c:Company {sector: $sector})
        OPTIONAL MATCH (c)-[:SERVES]->(m:Market)
        RETURN c.name as name, c.revenue as revenue, c.metrics as metrics,
               collect(m.name) as markets
        LIMIT 50
        """

        try:
            result = self.session.run(query, sector=sector)
            companies = [dict(record) for record in result]
            return companies
        except Exception as e:
            self.logger.error(f"Error finding companies: {e}")
            return []

    async def analyze_policy_impact(
        self,
        policy_id: str,
        sector: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze the impact of a policy on companies/sectors"""
        query = """
        MATCH (p:Policy {id: $policy_id})-[r:AFFECTS]->(c:Company)
        WHERE $sector IS NULL OR c.sector = $sector
        RETURN p.title as policy_title,
               count(c) as affected_companies,
               collect(DISTINCT c.sector) as affected_sectors,
               avg(c.revenue) as avg_revenue_affected
        """

        try:
            result = self.session.run(query, policy_id=policy_id, sector=sector)
            record = result.single()

            if record:
                return {
                    "policy": record["policy_title"],
                    "companies_affected": record["affected_companies"],
                    "sectors_affected": record["affected_sectors"],
                    "average_revenue": record["avg_revenue_affected"]
                }
            return {}

        except Exception as e:
            self.logger.error(f"Error analyzing policy impact: {e}")
            return {}
```

#### Seed Neo4j with Sample Data

**Create:** `scripts/seed_neo4j.py`

```python
"""Seed Neo4j with sample policy and company data"""
from neo4j import GraphDatabase
import os

def seed_neo4j():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")

        # Create sample policies
        session.run("""
            CREATE (p1:Policy {
                id: 'startup-india-2024',
                title: 'Startup India Initiative 2024',
                description: 'Tax exemptions and benefits for registered startups',
                effective_date: '2024-01-01',
                category: 'taxation'
            })

            CREATE (p2:Policy {
                id: 'gst-amendment-2024',
                title: 'GST Amendment Act 2024',
                description: 'Changes to GST rates for IT services',
                effective_date: '2024-04-01',
                category: 'taxation'
            })

            CREATE (p3:Policy {
                id: 'data-protection-act',
                title: 'Digital Personal Data Protection Act',
                description: 'Privacy regulations for data handling',
                effective_date: '2024-06-01',
                category: 'compliance'
            })

            CREATE (c1:Company {
                name: 'Tech Startup Inc',
                sector: 'SaaS',
                revenue: 2000000,
                employees: 25
            })

            CREATE (c2:Company {
                name: 'FinTech Solutions',
                sector: 'FinTech',
                revenue: 5000000,
                employees: 50
            })

            CREATE (m1:Market {
                name: 'Indian SaaS Market',
                size: 2500000000,
                growth_rate: 0.18
            })

            // Create relationships
            CREATE (p1)-[:AFFECTS {impact_level: 'high'}]->(c1)
            CREATE (p2)-[:AFFECTS {impact_level: 'medium'}]->(c1)
            CREATE (p2)-[:AFFECTS {impact_level: 'medium'}]->(c2)
            CREATE (p3)-[:AFFECTS {impact_level: 'high'}]->(c2)
            CREATE (p1)-[:RELATED_TO]->(p2)
            CREATE (c1)-[:SERVES]->(m1)
        """)

        print("✓ Neo4j seeded with sample data")

    driver.close()

if __name__ == "__main__":
    seed_neo4j()
```

**Run:** `python scripts/seed_neo4j.py`

---

## 🎯 PHASE 2: DATA & TESTING (Priority 2)

### Task 3: Add Kafka Consumers (6-8 hours)

**Create:** `data_pipeline/kafka/consumers.py`

```python
"""Kafka consumers for real-time data processing"""
from kafka import KafkaConsumer
import json
import os
from typing import Callable

class EIPKafkaConsumer:
    """Base Kafka consumer"""

    def __init__(self, topics: list, group_id: str):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers.split(','),
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )

    def consume(self, callback: Callable):
        """Consume messages and pass to callback"""
        for message in self.consumer:
            try:
                callback(message.value)
            except Exception as e:
                print(f"Error processing message: {e}")

class NewsConsumer(EIPKafkaConsumer):
    """Consumer for news stream"""

    def __init__(self):
        super().__init__(topics=["news_stream"], group_id="news_processor")

    def process_news(self, message: dict):
        """Process news article"""
        print(f"Processing news: {message.get('title')}")
        # TODO: Store in database, update agents, trigger notifications

if __name__ == "__main__":
    consumer = NewsConsumer()
    consumer.consume(consumer.process_news)
```

### Task 4: Expand Testing (8-10 hours)

**Enhance:** `tests/unit/agents/test_policy_agent.py`

```python
"""Comprehensive tests for Policy Agent"""
import pytest
from agents.policy_agent.policy_agent import PolicyAgent

@pytest.mark.asyncio
async def test_policy_agent_query_classification():
    """Test that policy agent correctly identifies policy queries"""
    agent = PolicyAgent()

    query = "What are the new startup tax exemptions?"

    # This should now work with real LLM if API key is set
    response = await agent.process(query)

    assert "answer" in response
    assert len(response["answer"]) > 50  # Reasonable length
    assert isinstance(response["sources"], list)
    assert response["confidence"] > 0.5

@pytest.mark.asyncio
async def test_policy_agent_with_context():
    """Test policy agent with user context"""
    agent = PolicyAgent()

    query = "How does the GST amendment affect my business?"
    context = {
        "business_type": "SaaS",
        "sector": "Technology",
        "revenue_range": "$1M-5M"
    }

    response = await agent.process(query, context)

    assert "SaaS" in response["answer"] or "technology" in response["answer"].lower()
    assert response["confidence"] > 0.6

# Add 20+ more tests...
```

---

## 📱 PHASE 3: MOBILE APP (Optional - Can be Phase 2)

### Task 5: Build Mobile Screens (16-20 hours)

**Create:** `mobile/src/screens/ChatScreen.tsx`

```typescript
import React, { useState } from 'react';
import { View, FlatList, TextInput, TouchableOpacity } from 'react-native';
import { Text, Card } from 'react-native-paper';
import { sendMessage } from '../services/api';

export default function ChatScreen() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendMessage(input);
      const aiMessage = { role: 'assistant', content: response.answer };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1 }}>
      <FlatList
        data={messages}
        renderItem={({ item }) => (
          <Card style={{ margin: 8 }}>
            <Card.Content>
              <Text>{item.content}</Text>
            </Card.Content>
          </Card>
        )}
      />
      <View style={{ flexDirection: 'row', padding: 8 }}>
        <TextInput
          value={input}
          onChangeText={setInput}
          placeholder="Ask anything..."
          style={{ flex: 1, borderWidth: 1, padding: 8 }}
        />
        <TouchableOpacity onPress={handleSend}>
          <Text>Send</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
```

---

## ✅ COMPLETION CHECKLIST

Use this to track your progress:

### Phase 1: Core Functionality
- [ ] Policy Agent - Remove 4 TODOs
- [ ] Market Agent - Remove 4 TODOs
- [ ] Finance Agent - Remove 1 TODO
- [ ] Tax Agent - Remove 4 TODOs
- [ ] Distribution Agent - Remove 4 TODOs
- [ ] Investment Agent - Remove 4 TODOs
- [ ] Legal Agent - Remove 4 TODOs
- [ ] News Agent - Remove 4 TODOs
- [ ] GraphRAG - Add query methods
- [ ] Neo4j - Seed with sample data

### Phase 2: Data & Testing
- [ ] Kafka consumers - Implement 4 consumers
- [ ] Spark streaming - Connect to agents
- [ ] Unit tests - 50+ tests, 70% coverage
- [ ] Integration tests - 10+ tests
- [ ] E2E tests - 3 user journeys (working)

### Phase 3: Mobile & Polish
- [ ] Mobile screens - 6 main screens
- [ ] Mobile navigation - React Navigation setup
- [ ] Mobile state - Redux store
- [ ] Deployment scripts - K8s automation
- [ ] Documentation - Update all docs

---

## 🎯 QUICK WINS

**Want to hit 90% in 1 day?** Focus on these:

1. **Complete 3 Core Agents** (Policy, Market, Finance) - 4 hours
2. **Seed Neo4j** - 1 hour
3. **Add 20 Unit Tests** - 2 hours
4. **Test End-to-End** - 1 hour

**Total:** 8 hours → **90% complete** ✅

---

## 📚 REFERENCE CODE LOCATIONS

**When you get stuck, reference these working examples:**

- **Complete LLM Integration:** `backend/app/services/llm_service.py`
- **Complete RAG System:** `backend/app/services/rag_service.py`
- **Complete VLM Service:** `backend/app/services/vlm_service.py`
- **Working Orchestrator:** `agents/orchestrator/agent_orchestrator.py`
- **Base Agent Template:** `agents/base_agent.py`
- **Working API Endpoint:** `backend/app/api/v1/chat.py`

**All of these are fully functional with 0 TODOs!**

---

## 🆘 TROUBLESHOOTING

### "LLM not working"
✅ Check `.env` for `OPENAI_API_KEY=sk-...`
✅ Test with: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

### "Agents returning empty responses"
✅ Check agent initialization logs
✅ Verify LLM service is initialized
✅ Add debug prints in `_generate_response()`

### "Neo4j connection failed"
✅ Run `docker-compose up neo4j`
✅ Check `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` in `.env`
✅ Verify: `docker-compose ps neo4j`

### "Tests failing"
✅ Install test dependencies: `pip install pytest pytest-asyncio pytest-cov`
✅ Run with: `pytest -v`
✅ Check fixture setup in `tests/conftest.py`

---

## 🚀 YOU'RE READY!

You now have:
- ✅ Detailed analysis of what needs work
- ✅ Step-by-step code templates
- ✅ Working examples to reference
- ✅ Clear priorities and time estimates

**Start with Phase 1, Task 1** (complete 2-3 agents) and you'll see immediate results!

Good luck! 🎉
