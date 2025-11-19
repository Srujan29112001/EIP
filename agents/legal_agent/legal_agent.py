"""
Legal Agent
Handles contract analysis, legal advisory, and compliance
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent


class LegalAgent(BaseAgent):
    """
    Legal Agent - Contract analysis, legal advisory, compliance

    Purpose: Help entrepreneurs navigate legal complexities

    Capabilities:
    - Contract review and analysis
    - Legal risk identification
    - Compliance checking
    - Corporate structure advisory
    - Intellectual property guidance
    - Employment law guidance
    """

    def __init__(self, config=None):
        super().__init__(config)
        self.agent_name = "Legal Agent"

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Legal Agent"""
        return """You are a Legal Advisory AI Agent specialized in business and entrepreneurship law.

Your expertise includes:

1. Contract Analysis
   - Vendor agreements
   - Partnership agreements
   - Employment contracts
   - Service level agreements (SLAs)
   - Non-disclosure agreements (NDAs)
   - Licensing agreements

2. Risk Identification
   - Liability clauses
   - Indemnification provisions
   - Termination conditions
   - Intellectual property rights
   - Non-compete and non-solicitation clauses
   - Dispute resolution mechanisms

3. Compliance
   - Corporate governance requirements
   - Regulatory compliance (industry-specific)
   - Data protection and privacy (GDPR, CCPA, etc.)
   - Labor laws and employment regulations
   - Tax compliance
   - Licensing and permits

4. Corporate Structure
   - Entity selection (LLC, C-Corp, S-Corp, Partnership)
   - Founder agreements
   - Cap table management
   - Equity compensation
   - Board structure

5. Intellectual Property
   - Trademark protection
   - Copyright considerations
   - Patent strategies
   - Trade secret protection
   - IP assignment agreements

6. Contract Drafting Support
   - Key terms and conditions
   - Standard clauses
   - Industry-specific provisions
   - Amendments and modifications

When analyzing contracts:
1. **Executive Summary** (Overall assessment and key concerns)
2. **Red Flags** (Critical issues requiring immediate attention)
3. **Key Terms Analysis** (Important clauses explained)
4. **Risk Assessment** (Potential legal risks)
5. **Recommendations** (Suggested amendments or actions)

IMPORTANT DISCLAIMER:
Always emphasize that this is AI-generated legal information, NOT legal advice.
Users should consult with a licensed attorney for formal legal counsel.
"""

    async def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process legal-related queries

        Args:
            query: User query about legal matters
            context: User context (documents, business info, etc.)

        Returns:
            Legal analysis and recommendations
        """
        # Extract user context
        user_context = context or {}
        user_tier = user_context.get("tier", "aspiring")

        # Check if contract/legal document is provided
        document_text = user_context.get("document_text")
        document_type = user_context.get("document_type", "unknown")

        # Retrieve relevant legal knowledge
        retrieved_docs = await self._retrieve_context(query)

        # Build context for LLM
        context_str = self._build_context(
            query,
            user_context,
            retrieved_docs,
            document_text,
            document_type
        )

        # Generate legal analysis using LLM
        response = await self._generate_response(query, context_str)

        # Add legal disclaimer
        response_with_disclaimer = self._add_legal_disclaimer(response)

        # Format sources
        sources = self._format_sources(retrieved_docs)

        return {
            "agent": self.agent_name,
            "answer": response_with_disclaimer,
            "sources": sources,
            "metadata": {
                "user_tier": user_tier,
                "document_type": document_type,
                "has_document": document_text is not None,
                "query_type": "legal_analysis"
            }
        }

    def _build_context(
        self,
        query: str,
        user_context: Dict[str, Any],
        retrieved_docs: List[Dict],
        document_text: Optional[str] = None,
        document_type: str = "unknown"
    ) -> str:
        """Build context string for LLM"""
        context_parts = []

        # Add document if provided
        if document_text:
            context_parts.append(f"Document Type: {document_type}")
            context_parts.append("Document Content (extracted via OCR):")
            context_parts.append("```")
            context_parts.append(document_text[:5000])  # Limit to first 5000 chars
            if len(document_text) > 5000:
                context_parts.append("\n... (document truncated for analysis)")
            context_parts.append("```")
            context_parts.append("")

        # Add user business context
        if user_context:
            context_parts.append(f"Business Context:")
            context_parts.append(f"- Business Type: {user_context.get('business_type', 'N/A')}")
            context_parts.append(f"- Industry: {user_context.get('industry', 'N/A')}")
            context_parts.append(f"- Stage: {user_context.get('tier', 'N/A')}")
            context_parts.append("")

        # Add retrieved legal precedents/knowledge
        if retrieved_docs:
            context_parts.append("Relevant Legal Knowledge:")
            for i, doc in enumerate(retrieved_docs[:3], 1):
                context_parts.append(f"\n{i}. {doc.get('title', 'Legal Document')}")
                context_parts.append(doc.get('content', '')[:400])
            context_parts.append("")

        # Add query
        context_parts.append(f"Legal Query: {query}")

        return "\n".join(context_parts)

    def _add_legal_disclaimer(self, response: str) -> str:
        """Add legal disclaimer to response"""
        disclaimer = """

---
⚠️ **LEGAL DISCLAIMER**:
This is AI-generated legal information, NOT formal legal advice. The analysis provided is for informational purposes only and should not be relied upon as a substitute for professional legal counsel. Always consult with a licensed attorney in your jurisdiction before making legal decisions or taking action based on this information.
"""
        return response + disclaimer

    def _identify_contract_clauses(self, contract_text: str) -> Dict[str, List[str]]:
        """
        Identify key contract clauses using simple pattern matching
        (In production, this would use NER models)
        """
        clauses = {
            "payment_terms": [],
            "termination": [],
            "liability": [],
            "confidentiality": [],
            "intellectual_property": [],
            "dispute_resolution": []
        }

        # Simple keyword-based identification (placeholder)
        # In production, use NER (spaCy, transformers) for entity extraction

        contract_lower = contract_text.lower()

        if "payment" in contract_lower or "invoice" in contract_lower:
            clauses["payment_terms"].append("Payment terms identified")

        if "termination" in contract_lower or "cancel" in contract_lower:
            clauses["termination"].append("Termination clauses identified")

        if "liable" in contract_lower or "liability" in contract_lower:
            clauses["liability"].append("Liability provisions identified")

        if "confidential" in contract_lower or "nda" in contract_lower:
            clauses["confidentiality"].append("Confidentiality clauses identified")

        if "intellectual property" in contract_lower or "ip" in contract_lower or "copyright" in contract_lower:
            clauses["intellectual_property"].append("IP clauses identified")

        if "arbitration" in contract_lower or "dispute" in contract_lower:
            clauses["dispute_resolution"].append("Dispute resolution clauses identified")

        return clauses

    def _assess_contract_risk(self, contract_text: str) -> str:
        """Assess overall contract risk level"""
        risk_keywords = {
            "high": ["unlimited liability", "perpetual", "no termination", "irrevocable"],
            "medium": ["indemnify", "hold harmless", "warranty"],
            "low": ["standard terms", "mutual agreement"]
        }

        contract_lower = contract_text.lower()
        risk_score = 0

        for keyword in risk_keywords["high"]:
            if keyword in contract_lower:
                risk_score += 3

        for keyword in risk_keywords["medium"]:
            if keyword in contract_lower:
                risk_score += 1

        if risk_score >= 5:
            return "HIGH"
        elif risk_score >= 2:
            return "MEDIUM"
        else:
            return "LOW"
