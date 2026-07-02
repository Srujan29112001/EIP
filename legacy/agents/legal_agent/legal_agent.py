"""
Legal Agent
Handles contract analysis, legal advisory, and compliance
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
import os


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
        document_path = user_context.get("document_path")
        document_type = user_context.get("document_type", "unknown")

        # OCR processing if document path is provided (image/PDF)
        if document_path and not document_text:
            document_text = await self._extract_text_from_document(document_path)
            if document_text:
                user_context["document_text"] = document_text

        # If we have a contract document, perform comprehensive analysis
        contract_analysis = None
        if document_text:
            contract_analysis = await self._analyze_contract_comprehensive(document_text)

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

        # Add contract-specific analysis if available
        if contract_analysis:
            response = self._integrate_contract_analysis(response, contract_analysis)

        # Add legal disclaimer
        response_with_disclaimer = self._add_legal_disclaimer(response)

        # Format sources
        sources = self._format_sources(retrieved_docs)

        return {
            "agent": self.agent_name,
            "answer": response_with_disclaimer,
            "sources": sources,
            "contract_analysis": contract_analysis,
            "metadata": {
                "user_tier": user_tier,
                "document_type": document_type,
                "has_document": document_text is not None,
                "ocr_used": document_path is not None and not user_context.get("document_text"),
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

    async def _identify_contract_clauses(self, contract_text: str) -> Dict[str, List[str]]:
        """
        Identify key contract clauses using LLM-powered NER

        Uses LLM to extract and categorize contract clauses with high accuracy
        """
        try:
            import sys
            import os
            import json
            import re
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            # Use LLM for advanced clause extraction
            extraction_prompt = f"""Analyze this contract and extract key clauses. Identify and categorize specific clause text.

Contract Text:
{contract_text[:4000]}  # Limit for token efficiency

Extract clauses in the following categories:
1. payment_terms - Payment amounts, schedules, methods, late fees
2. termination - How and when the contract can be terminated
3. liability - Liability limitations, caps, indemnification
4. confidentiality - NDA provisions, confidential information handling
5. intellectual_property - IP ownership, licensing, assignments
6. dispute_resolution - Arbitration, mediation, governing law

Return ONLY valid JSON format:
{{
  "payment_terms": ["clause text 1", "clause text 2"],
  "termination": ["clause text 1"],
  "liability": ["clause text 1"],
  "confidentiality": ["clause text 1"],
  "intellectual_property": ["clause text 1"],
  "dispute_resolution": ["clause text 1"]
}}

Extract actual clause text (1-2 sentences max per clause). Return ONLY the JSON."""

            response = await llm.generate(
                prompt=extraction_prompt,
                temperature=0.2,  # Low temp for precision
                max_tokens=1000
            )

            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                clauses = json.loads(json_match.group(0))
                return clauses
            else:
                return self._get_fallback_clauses(contract_text)

        except Exception as e:
            print(f"LLM clause extraction failed: {e}. Using fallback.")
            return self._get_fallback_clauses(contract_text)

    def _get_fallback_clauses(self, contract_text: str) -> Dict[str, List[str]]:
        """Fallback clause extraction using keyword matching"""
        clauses = {
            "payment_terms": [],
            "termination": [],
            "liability": [],
            "confidentiality": [],
            "intellectual_property": [],
            "dispute_resolution": []
        }

        contract_lower = contract_text.lower()

        if "payment" in contract_lower or "invoice" in contract_lower:
            clauses["payment_terms"].append("Payment terms identified (keyword-based)")

        if "termination" in contract_lower or "cancel" in contract_lower:
            clauses["termination"].append("Termination clauses identified (keyword-based)")

        if "liable" in contract_lower or "liability" in contract_lower:
            clauses["liability"].append("Liability provisions identified (keyword-based)")

        if "confidential" in contract_lower or "nda" in contract_lower:
            clauses["confidentiality"].append("Confidentiality clauses identified (keyword-based)")

        if "intellectual property" in contract_lower or "ip" in contract_lower or "copyright" in contract_lower:
            clauses["intellectual_property"].append("IP clauses identified (keyword-based)")

        if "arbitration" in contract_lower or "dispute" in contract_lower:
            clauses["dispute_resolution"].append("Dispute resolution clauses identified (keyword-based)")

        return clauses

    async def _assess_contract_risk(self, contract_text: str) -> Dict[str, Any]:
        """
        Assess overall contract risk level using LLM analysis

        Returns comprehensive risk assessment with specific risk factors
        """
        try:
            import sys
            import os
            import json
            import re
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            # Use LLM for comprehensive risk assessment
            risk_prompt = f"""Analyze this contract for legal risks and provide a comprehensive risk assessment.

Contract Text:
{contract_text[:4000]}

Assess the following risk dimensions:
1. **Liability Risk**: Unlimited liability, uncapped damages, broad indemnification
2. **Financial Risk**: Unfavorable payment terms, penalties, financial commitments
3. **Termination Risk**: Difficulty terminating, lock-in periods, penalties for exit
4. **IP Risk**: IP assignment, loss of rights, broad licensing
5. **Compliance Risk**: Regulatory requirements, audit rights, compliance burdens
6. **Dispute Risk**: Unfavorable jurisdiction, arbitration clauses, legal costs

Return ONLY valid JSON format:
{{
  "overall_risk": "LOW|MEDIUM|HIGH|CRITICAL",
  "risk_score": <0-100>,
  "risk_factors": [
    {{
      "category": "liability|financial|termination|ip|compliance|dispute",
      "severity": "low|medium|high|critical",
      "description": "Brief description of the risk",
      "clause_reference": "Specific clause or section"
    }}
  ],
  "red_flags": ["Critical issue 1", "Critical issue 2"],
  "recommendations": ["Action 1", "Action 2"]
}}

Return ONLY the JSON."""

            response = await llm.generate(
                prompt=risk_prompt,
                temperature=0.2,  # Low temp for precision
                max_tokens=1200
            )

            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                risk_assessment = json.loads(json_match.group(0))
                return risk_assessment
            else:
                return self._get_fallback_risk_assessment(contract_text)

        except Exception as e:
            print(f"LLM risk assessment failed: {e}. Using fallback.")
            return self._get_fallback_risk_assessment(contract_text)

    def _get_fallback_risk_assessment(self, contract_text: str) -> Dict[str, Any]:
        """Fallback risk assessment using keyword matching"""
        risk_keywords = {
            "high": ["unlimited liability", "perpetual", "no termination", "irrevocable"],
            "medium": ["indemnify", "hold harmless", "warranty"],
            "low": ["standard terms", "mutual agreement"]
        }

        contract_lower = contract_text.lower()
        risk_score = 0
        red_flags = []

        for keyword in risk_keywords["high"]:
            if keyword in contract_lower:
                risk_score += 30
                red_flags.append(f"Contains '{keyword}' - high risk clause")

        for keyword in risk_keywords["medium"]:
            if keyword in contract_lower:
                risk_score += 10

        if risk_score >= 60:
            overall_risk = "HIGH"
        elif risk_score >= 30:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"

        return {
            "overall_risk": overall_risk,
            "risk_score": min(risk_score, 100),
            "risk_factors": [
                {
                    "category": "general",
                    "severity": overall_risk.lower(),
                    "description": "Risk assessed using keyword analysis (limited)",
                    "clause_reference": "Multiple clauses"
                }
            ],
            "red_flags": red_flags if red_flags else ["No critical issues detected with keyword analysis"],
            "recommendations": ["Consult with attorney for comprehensive review", "Review all clauses carefully"]
        }

    async def _extract_text_from_document(self, document_path: str) -> Optional[str]:
        """
        Extract text from document using OCR (for images/PDFs)

        Supports:
        - PDF files (using PyPDF2 + OCR fallback)
        - Image files (PNG, JPG, TIFF using Tesseract OCR)
        """
        try:
            file_extension = os.path.splitext(document_path)[1].lower()

            # For PDF files
            if file_extension == '.pdf':
                return await self._extract_from_pdf(document_path)

            # For image files
            elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                return await self._extract_from_image(document_path)

            else:
                print(f"Unsupported file format: {file_extension}")
                return None

        except Exception as e:
            print(f"OCR extraction failed: {e}")
            return None

    async def _extract_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract text from PDF using PyPDF2 and OCR fallback"""
        try:
            # Try PyPDF2 first for text-based PDFs
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"

                    if text.strip():  # If text was extracted
                        return text
            except ImportError:
                print("PyPDF2 not available, using OCR")
            except Exception as e:
                print(f"PyPDF2 extraction failed: {e}, falling back to OCR")

            # Fallback to OCR for scanned PDFs
            try:
                import pdf2image
                import pytesseract
                from PIL import Image

                # Convert PDF to images
                images = pdf2image.convert_from_path(pdf_path)

                text = ""
                for i, image in enumerate(images):
                    # Perform OCR on each page
                    page_text = pytesseract.image_to_string(image)
                    text += f"\n--- Page {i+1} ---\n{page_text}"

                return text
            except ImportError:
                print("pdf2image or pytesseract not available")
                return None

        except Exception as e:
            print(f"PDF extraction failed: {e}")
            return None

    async def _extract_from_image(self, image_path: str) -> Optional[str]:
        """Extract text from image using Tesseract OCR"""
        try:
            import pytesseract
            from PIL import Image

            # Open image
            image = Image.open(image_path)

            # Perform OCR
            text = pytesseract.image_to_string(image)

            return text if text.strip() else None

        except ImportError:
            print("pytesseract or PIL not available for OCR")
            return None
        except Exception as e:
            print(f"Image OCR failed: {e}")
            return None

    async def _analyze_contract_comprehensive(self, contract_text: str) -> Dict[str, Any]:
        """
        Perform comprehensive contract analysis using all LLM-powered tools

        Returns complete analysis including clauses, risks, entities, recommendations
        """
        try:
            # Extract entities (parties, dates, amounts) using NER
            entities = await self._extract_contract_entities(contract_text)

            # Identify and categorize clauses
            clauses = await self._identify_contract_clauses(contract_text)

            # Assess risks
            risk_assessment = await self._assess_contract_risk(contract_text)

            # Generate executive summary
            summary = await self._generate_contract_summary(contract_text, entities, clauses, risk_assessment)

            return {
                "summary": summary,
                "entities": entities,
                "clauses": clauses,
                "risk_assessment": risk_assessment,
                "analysis_timestamp": str(os.times())
            }

        except Exception as e:
            print(f"Comprehensive contract analysis failed: {e}")
            return {
                "summary": "Contract analysis partially completed due to system limitations.",
                "entities": {},
                "clauses": {},
                "risk_assessment": {"overall_risk": "UNKNOWN"},
                "error": str(e)
            }

    async def _extract_contract_entities(self, contract_text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from contract using LLM-powered NER

        Extracts: parties, dates, monetary amounts, locations, obligations
        """
        try:
            import sys
            import os
            import json
            import re
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            ner_prompt = f"""Extract named entities from this contract. Identify all relevant parties, dates, amounts, and obligations.

Contract Text:
{contract_text[:3500]}

Extract entities in these categories:
1. **Parties**: All parties to the contract (companies, individuals)
2. **Effective Dates**: Start date, end date, renewal dates
3. **Monetary Amounts**: Payment amounts, fees, penalties
4. **Obligations**: Key obligations for each party
5. **Deliverables**: What must be delivered
6. **Deadlines**: Important deadlines and timeframes

Return ONLY valid JSON format:
{{
  "parties": ["Party 1", "Party 2"],
  "dates": {{
    "effective_date": "YYYY-MM-DD or description",
    "expiration_date": "YYYY-MM-DD or description",
    "other_dates": ["date1", "date2"]
  }},
  "monetary_amounts": [
    {{"description": "Payment type", "amount": "USD 10,000", "frequency": "monthly"}}
  ],
  "obligations": {{
    "party1": ["obligation1", "obligation2"],
    "party2": ["obligation1", "obligation2"]
  }},
  "deliverables": ["deliverable1", "deliverable2"],
  "deadlines": ["deadline1", "deadline2"]
}}

Return ONLY the JSON."""

            response = await llm.generate(
                prompt=ner_prompt,
                temperature=0.1,  # Very low temp for factual extraction
                max_tokens=1000
            )

            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                entities = json.loads(json_match.group(0))
                return entities
            else:
                return self._get_fallback_entities()

        except Exception as e:
            print(f"Entity extraction failed: {e}")
            return self._get_fallback_entities()

    def _get_fallback_entities(self) -> Dict[str, List[str]]:
        """Fallback entities when NER fails"""
        return {
            "parties": ["Entities not extracted"],
            "dates": {"effective_date": "Not extracted", "expiration_date": "Not extracted"},
            "monetary_amounts": [],
            "obligations": {},
            "deliverables": [],
            "deadlines": []
        }

    async def _generate_contract_summary(
        self,
        contract_text: str,
        entities: Dict,
        clauses: Dict,
        risk_assessment: Dict
    ) -> str:
        """Generate executive summary of contract using LLM"""
        try:
            import sys
            import os
            import json
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))
            from services.llm_service import LLMService, LLMProvider

            llm = LLMService(provider=LLMProvider.OPENAI, model="gpt-4o")

            summary_prompt = f"""Generate a concise executive summary of this contract.

Contract Text:
{contract_text[:3000]}

Extracted Information:
- Parties: {entities.get('parties', [])}
- Risk Level: {risk_assessment.get('overall_risk', 'Unknown')}
- Key Clauses: {list(clauses.keys())}

Provide a 3-5 sentence executive summary covering:
1. What is this contract about?
2. Who are the parties?
3. What are the key terms?
4. What is the overall risk level?
5. What are the most important things to know?

Write in clear, business-friendly language."""

            summary = await llm.generate(
                prompt=summary_prompt,
                temperature=0.4,
                max_tokens=300
            )

            return summary.strip()

        except Exception as e:
            print(f"Summary generation failed: {e}")
            return "Contract summary generation failed. Please review the detailed analysis below."

    def _integrate_contract_analysis(self, response: str, contract_analysis: Dict) -> str:
        """Integrate contract-specific analysis into the general response"""
        analysis_section = "\n\n## Contract Analysis\n\n"
        analysis_section += f"**Executive Summary:** {contract_analysis.get('summary', 'N/A')}\n\n"

        risk = contract_analysis.get('risk_assessment', {})
        if risk:
            analysis_section += f"**Risk Level:** {risk.get('overall_risk', 'Unknown')} "
            analysis_section += f"(Score: {risk.get('risk_score', 0)}/100)\n\n"

            if risk.get('red_flags'):
                analysis_section += "**Red Flags:**\n"
                for flag in risk['red_flags'][:5]:  # Top 5
                    analysis_section += f"- {flag}\n"
                analysis_section += "\n"

        entities = contract_analysis.get('entities', {})
        if entities.get('parties'):
            analysis_section += f"**Parties:** {', '.join(entities['parties'])}\n\n"

        return response + analysis_section
