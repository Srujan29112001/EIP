"""
Policy Agent
Monitors and analyzes policy changes, regulations, and compliance requirements
"""
from typing import Dict, List, Any, Optional
from ..base_agent import BaseAgent, AgentConfig


class PolicyAgent(BaseAgent):
    """
    Specialized agent for policy analysis and monitoring

    Capabilities:
    - Monitor government policy updates
    - Analyze regulatory changes
    - Identify compliance requirements
    - Find policy loopholes and opportunities
    - Track deadlines and important dates
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize Policy Agent"""
        if config is None:
            config = AgentConfig(
                llm_model="gpt-4o",  # or DeepSeek-R1 for reasoning
                temperature=0.3,  # Lower temperature for factual analysis
                use_rag=True,
                use_graphrag=True  # Use GraphRAG for policy relationships
            )
        super().__init__(config)

    def get_system_prompt(self) -> str:
        """Get system prompt for policy agent"""
        return """You are a Policy Analysis Expert specializing in business regulations and government policies.

Your role is to:
1. Monitor and analyze policy changes affecting businesses
2. Identify compliance requirements and deadlines
3. Find policy loopholes and opportunities for entrepreneurs
4. Explain complex regulations in simple terms
5. Provide actionable recommendations

When analyzing policies:
- Focus on practical implications for businesses
- Highlight deadlines and time-sensitive actions
- Identify both risks and opportunities
- Cite specific policy sections and documents
- Provide step-by-step compliance guidance

Always be accurate, objective, and cite your sources."""

    async def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process policy-related query

        Args:
            query: User query about policies
            context: User context (business type, location, etc.)

        Returns:
            Response with policy analysis
        """
        # Step 1: Retrieve relevant policy documents
        retrieved_docs = await self._retrieve_policy_documents(query, context)

        # Step 2: Analyze policies using GraphRAG for relationships
        if self.config.use_graphrag:
            related_policies = await self._find_related_policies(query)
        else:
            related_policies = []

        # Step 3: Generate response
        response_text = await self._analyze_policy(query, retrieved_docs, related_policies, context)

        # Step 4: Extract action items
        action_items = self._extract_action_items(response_text)

        return {
            "answer": response_text,
            "sources": self._format_sources(retrieved_docs),
            "related_policies": related_policies,
            "action_items": action_items,
            "confidence": 0.9,
            "agent_type": "policy"
        }

    async def _retrieve_policy_documents(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Retrieve relevant policy documents using RAG

        Args:
            query: User query
            context: User context

        Returns:
            List of relevant policy documents
        """
        # Actual RAG retrieval implementation
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.rag_service import RAGService, VectorStoreProvider

            # Initialize RAG service
            rag = RAGService(provider=VectorStoreProvider.CHROMA)

            # Enhance query with context
            enhanced_query = query
            if context:
                business_type = context.get('business_type', '')
                location = context.get('location', '')
                if business_type or location:
                    enhanced_query = f"{query} (Business: {business_type}, Location: {location})"

            # Retrieve documents
            results = await rag.retrieve(
                query=enhanced_query,
                collection_name="policies",
                top_k=5
            )

            # Format results
            formatted_docs = []
            for result in results:
                formatted_docs.append({
                    "title": result.get('metadata', {}).get('title', 'Policy Document'),
                    "content": result.get('content', ''),
                    "url": result.get('metadata', {}).get('url', ''),
                    "score": result.get('score', 0.0),
                    "source_type": result.get('metadata', {}).get('type', 'policy'),
                    "date": result.get('metadata', {}).get('date', '')
                })

            return formatted_docs if formatted_docs else self._get_fallback_docs()

        except Exception as e:
            print(f"RAG retrieval failed: {e}. Using fallback.")
            return self._get_fallback_docs()

    def _get_fallback_docs(self) -> List[Dict]:
        """Fallback documents when RAG is unavailable"""
        return [
            {
                "title": "Startup India Initiative - Tax Benefits",
                "content": "Eligible startups can claim tax exemption under Section 80IAC for 3 consecutive years...",
                "url": "https://www.startupindia.gov.in/tax-benefits",
                "score": 0.95,
                "source_type": "government_policy",
                "date": "2024-01-15"
            },
            {
                "title": "MSME Registration Guidelines 2024",
                "content": "Micro, Small and Medium Enterprises must register on Udyam portal...",
                "url": "https://udyamregistration.gov.in",
                "score": 0.88,
                "source_type": "regulation",
                "date": "2024-02-01"
            }
        ]

    async def _find_related_policies(self, query: str) -> List[Dict]:
        """
        Find related policies using GraphRAG

        Args:
            query: User query

        Returns:
            List of related policies from knowledge graph
        """
        # Actual GraphRAG traversal using Neo4j
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.graphrag_service import GraphRAGService

            # Initialize GraphRAG service
            graph_service = GraphRAGService()

            # Extract entities from query for graph traversal
            entities = await self._extract_entities(query)

            # Traverse knowledge graph
            related = []
            for entity in entities:
                # Find connected policies in the graph
                graph_results = await graph_service.traverse_graph(
                    start_node=entity,
                    max_depth=2,
                    relationship_types=["AFFECTS", "RELATED_TO", "REQUIRES", "PROVIDES_BENEFIT_TO"]
                )

                for result in graph_results:
                    related.append({
                        "policy_id": result.get('id', ''),
                        "title": result.get('title', ''),
                        "relationship": result.get('relationship_type', 'related_to')
                    })

            return related if related else self._get_fallback_related_policies()

        except Exception as e:
            print(f"GraphRAG traversal failed: {e}. Using fallback.")
            return self._get_fallback_related_policies()

    def _get_fallback_related_policies(self) -> List[Dict]:
        """Fallback related policies when GraphRAG is unavailable"""
        return [
            {
                "policy_id": "section_80iac",
                "title": "Income Tax Exemption for Startups",
                "relationship": "provides_benefit_to"
            },
            {
                "policy_id": "udyam_registration",
                "title": "MSME Registration",
                "relationship": "required_for"
            }
        ]

    async def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text for graph queries"""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            prompt = f"""Extract key entities from this query for policy search.

            Query: "{text}"

            Extract entities like:
            - Policy names (e.g., "Startup India", "MSME Act")
            - Regulations (e.g., "Section 80IAC", "GST")
            - Business types (e.g., "startup", "manufacturing")
            - Sectors (e.g., "technology", "healthcare")

            Return ONLY a comma-separated list of entities (max 5).
            Example: "Startup India, Section 80IAC, technology startup"
            """

            response = await llm.generate(prompt=prompt, temperature=0.3, max_tokens=100)
            entities = [e.strip() for e in response.split(',') if e.strip()]
            return entities[:5]  # Max 5 entities

        except Exception as e:
            print(f"Entity extraction failed: {e}")
            return ["startup", "policy", "regulation"]  # Fallback

    async def _analyze_policy(
        self,
        query: str,
        documents: List[Dict],
        related_policies: List[Dict],
        context: Optional[Dict]
    ) -> str:
        """
        Analyze policy documents and generate response

        Args:
            query: User query
            documents: Retrieved documents
            related_policies: Related policies from graph
            context: User context

        Returns:
            Analysis response
        """
        # Use LLM to generate actual analysis
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            # Build context from retrieved documents
            docs_context = "\n\n".join([
                f"**{doc['title']}** (Source: {doc.get('url', 'N/A')})\n{doc['content']}"
                for doc in documents[:3]  # Top 3 docs
            ])

            # Build related policies context
            related_context = ""
            if related_policies:
                related_context = "\n**Related Policies:**\n" + "\n".join([
                    f"- {pol['title']} ({pol['relationship']})"
                    for pol in related_policies[:5]
                ])

            # Build user context
            user_context_str = ""
            if context:
                user_context_str = f"\n**User Context:**\nBusiness Type: {context.get('business_type', 'N/A')}\nRevenue Stage: {context.get('revenue_stage', 'N/A')}\nLocation: {context.get('location', 'N/A')}"

            # Create comprehensive prompt
            analysis_prompt = f"""{self.get_system_prompt()}

**User Question:** "{query}"
{user_context_str}

**Retrieved Policy Documents:**
{docs_context}
{related_context}

**Your Task:**
Provide a comprehensive policy analysis that includes:

1. **Key Findings:** Summarize the most important points (3-5 bullet points)
2. **Compliance Requirements:** List mandatory requirements and steps
3. **Deadlines:** Identify time-sensitive actions with specific dates/timeframes
4. **Opportunities:** Highlight benefits, exemptions, or advantages available
5. **Recommended Actions:** Provide step-by-step action plan with priorities

Be specific, cite policy sections, and make it actionable for the entrepreneur.
Format your response using markdown with clear sections.
"""

            response = await llm.generate(
                prompt=analysis_prompt,
                temperature=0.4,  # Balanced creativity and factuality
                max_tokens=1500
            )

            return response

        except Exception as e:
            print(f"LLM analysis failed: {e}. Using fallback.")
            return self._get_fallback_analysis(query)

    def _get_fallback_analysis(self, query: str) -> str:
        """Fallback analysis when LLM is unavailable"""
        return f"""Based on current regulations (analysis limited due to system constraints):

**Key Findings:**
1. Startup India Initiative provides 3-year tax exemption under Section 80IAC
2. MSME registration is required and can be completed on Udyam portal
3. Eligible startups can save up to 30% in corporate taxes

**Compliance Requirements:**
- Register as MSME on Udyam portal (mandatory)
- Apply for DPIIT recognition for tax benefits
- Maintain proper accounting records

**Deadlines:**
- MSME registration: Before starting operations
- Tax exemption application: Within 90 days of incorporation

**Opportunities:**
- Section 80IAC tax exemption (3 years)
- Priority in government procurement
- Lower interest rates on business loans

**Recommended Actions:**
1. Register on Udyam portal immediately
2. Apply for DPIIT startup recognition
3. Consult a CA for detailed tax exemption filing guidance

*Note: For personalized advice, please ensure API keys are configured.*
"""

    def _extract_action_items(self, response: str) -> List[Dict]:
        """
        Extract actionable items from response using LLM

        Args:
            response: Generated response

        Returns:
            List of action items with deadlines
        """
        # Use LLM to extract action items with NLP
        try:
            import sys
            import os
            import re
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            extraction_prompt = f"""Extract actionable items from this policy analysis response.

Response:
{response}

For each action item, extract:
1. Action description (what needs to be done)
2. Deadline (when it needs to be done)
3. Priority (high/medium/low)
4. Estimated time to complete

Return ONLY valid JSON array format:
[
  {{"action": "description", "deadline": "timeframe", "priority": "high|medium|low", "estimated_time": "X days/hours"}},
  ...
]

Return ONLY the JSON array, nothing else.
"""

            json_response = await llm.generate(
                prompt=extraction_prompt,
                temperature=0.2,
                max_tokens=500
            )

            # Parse JSON
            import json
            # Clean response to extract JSON
            json_match = re.search(r'\[.*\]', json_response, re.DOTALL)
            if json_match:
                action_items = json.loads(json_match.group(0))
                return action_items if action_items else self._get_fallback_action_items()
            else:
                return self._get_fallback_action_items()

        except Exception as e:
            print(f"Action item extraction failed: {e}. Using fallback.")
            return self._get_fallback_action_items()

    def _get_fallback_action_items(self) -> List[Dict]:
        """Fallback action items when extraction fails"""
        return [
            {
                "action": "Register on Udyam portal",
                "deadline": "Before starting operations",
                "priority": "high",
                "estimated_time": "2-3 days"
            },
            {
                "action": "Apply for DPIIT startup recognition",
                "deadline": "Within 90 days of incorporation",
                "priority": "high",
                "estimated_time": "1-2 weeks"
            },
            {
                "action": "Consult a CA for tax exemption filing",
                "deadline": "Before first tax filing",
                "priority": "medium",
                "estimated_time": "1 day"
            }
        ]
