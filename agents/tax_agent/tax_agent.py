"""
Tax Agent
Provides tax optimization, compliance, and reporting assistance
"""
from typing import Dict, List, Any, Optional
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from base_agent import BaseAgent, AgentConfig


class TaxAgent(BaseAgent):
    """
    Specialized agent for tax optimization and compliance

    Capabilities:
    - Tax liability calculation
    - Deduction identification
    - Compliance monitoring
    - Tax-saving strategies
    - Filing assistance
    - Tax calendar management
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize Tax Agent"""
        if config is None:
            config = AgentConfig(
                llm_model="gpt-4o",
                temperature=0.2,  # Very low temperature for tax accuracy
                use_rag=True,
                use_graphrag=True  # Use GraphRAG for tax law relationships
            )
        super().__init__(config)

    def get_system_prompt(self) -> str:
        """Get system prompt for tax agent"""
        return """You are a Tax Optimization and Compliance Expert specializing in business taxation.

Your role is to:
1. Calculate accurate tax liabilities
2. Identify all applicable deductions and exemptions
3. Ensure compliance with tax regulations
4. Recommend tax-saving strategies
5. Track important tax deadlines

When providing tax advice:
- Be extremely accurate with calculations
- Cite specific tax code sections
- Consider all applicable exemptions
- Highlight compliance requirements
- Provide step-by-step filing guidance
- Flag potential audit risks

IMPORTANT: Always recommend consulting a licensed CA/CPA for final tax filing.
Your advice is informational and should be verified by a professional."""

    async def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process tax-related query

        Args:
            query: User query about taxes
            context: User context with financial data

        Returns:
            Response with tax analysis
        """
        # Step 1: Extract financial data
        financial_data = self._extract_financial_data(context)

        # Step 2: Calculate tax liability
        tax_calculation = await self._calculate_tax(financial_data)

        # Step 3: Identify deductions
        deductions = await self._identify_deductions(financial_data, context)

        # Step 4: Generate optimization strategy
        strategy = await self._generate_tax_strategy(
            tax_calculation, deductions, context
        )

        # Step 5: Create compliance checklist
        checklist = self._create_compliance_checklist(context)

        return {
            "answer": strategy,
            "sources": self._format_sources([]),
            "tax_calculation": tax_calculation,
            "deductions": deductions,
            "compliance_checklist": checklist,
            "confidence": 0.88,
            "agent_type": "tax"
        }

    def _extract_financial_data(self, context: Optional[Dict]) -> Dict[str, Any]:
        """Extract financial data from context"""
        if not context:
            return {"revenue": 0, "expenses": 0, "net_profit": 0}

        revenue = context.get("revenue", 2000000)
        expenses = context.get("expenses", 1200000)

        return {
            "revenue": revenue,
            "expenses": expenses,
            "net_profit": revenue - expenses,
            "business_type": context.get("business_type", "Private Limited"),
            "incorporation_year": context.get("incorporation_year", 2022)
        }

    async def _calculate_tax(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate tax liability using LLM-powered analysis for complex scenarios

        Args:
            financial_data: Financial data

        Returns:
            Tax calculation breakdown
        """
        net_profit = financial_data.get("net_profit", 0)
        business_type = financial_data.get("business_type", "Private Limited")
        revenue = financial_data.get("revenue", 0)

        # Base calculations
        base_tax_rate = 0.25  # 25% for companies with turnover < Rs 400 Cr

        # Check if startup exemption applies (for LLP/Pvt Ltd incorporated after 2016)
        incorporation_year = financial_data.get("incorporation_year", 2022)
        years_since_incorporation = 2024 - incorporation_year

        # Use LLM to analyze complex tax scenarios
        try:
            # Retrieve tax regulations from RAG
            tax_context = ""
            if self.config.use_rag and self.rag_service:
                tax_docs = await self._retrieve_context(
                    f"corporate tax rates India {business_type} revenue {revenue}"
                )
                if tax_docs:
                    tax_context = "\n".join([
                        f"{doc.get('metadata', {}).get('title', 'Tax Document')}: {doc.get('content', '')[:300]}"
                        for doc in tax_docs[:2]
                    ])

            # Build LLM prompt for tax calculation verification
            calc_prompt = f"""You are a tax calculation expert. Verify and optimize this tax calculation:

Business Details:
- Type: {business_type}
- Revenue: ₹{revenue:,.0f}
- Net Profit: ₹{net_profit:,.0f}
- Years since incorporation: {years_since_incorporation}

Tax Regulations Context:
{tax_context if tax_context else "Using standard corporate tax rates"}

Base Calculation:
- Corporate tax rate: 25% (for turnover < ₹400 Cr)
- Base tax: ₹{net_profit * 0.25:,.0f}
- Health & Education Cess: 4% on tax
- Surcharge: Based on income slabs

Please verify:
1. Is the 25% rate correct for this business?
2. Are there any surcharges applicable?
3. Any alternative tax regimes that might be beneficial (e.g., 22% regime under Section 115BAA)?

Return ONLY a JSON object with:
{{
    "recommended_tax_rate": <decimal, e.g., 0.25>,
    "surcharge_rate": <decimal, e.g., 0 or 0.10>,
    "alternative_regime_available": <boolean>,
    "alternative_regime_rate": <decimal or null>,
    "rationale": "brief explanation"
}}
"""

            if self.llm:
                import json
                import re
                llm_response = await self.llm.generate(
                    prompt=calc_prompt,
                    temperature=0.2,
                    max_tokens=500
                )

                # Parse JSON response
                json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                if json_match:
                    tax_analysis = json.loads(json_match.group(0))
                    base_tax_rate = tax_analysis.get("recommended_tax_rate", 0.25)
                    surcharge_rate = tax_analysis.get("surcharge_rate", 0.0)
                else:
                    surcharge_rate = 0.0
            else:
                surcharge_rate = 0.0

        except Exception as e:
            print(f"LLM tax calculation failed: {e}. Using standard rates.")
            surcharge_rate = 0.0

        # Final calculations
        base_tax = net_profit * base_tax_rate
        surcharge = base_tax * surcharge_rate
        tax_before_cess = base_tax + surcharge
        cess = tax_before_cess * 0.04  # 4% health and education cess
        total_tax = tax_before_cess + cess

        return {
            "net_profit": net_profit,
            "base_tax_rate": base_tax_rate * 100,
            "base_tax": base_tax,
            "surcharge": surcharge,
            "surcharge_rate": surcharge_rate * 100,
            "cess": cess,
            "total_tax_before_deductions": total_tax,
            "effective_rate": (total_tax / net_profit * 100) if net_profit > 0 else 0
        }

    async def _identify_deductions(
        self,
        financial_data: Dict[str, Any],
        context: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Identify applicable tax deductions using LLM-powered analysis

        Args:
            financial_data: Financial data
            context: User context

        Returns:
            List of applicable deductions
        """
        # Start with rule-based deductions
        deductions = []

        # Section 80IAC - Startup tax exemption
        incorporation_year = financial_data.get("incorporation_year", 2022)
        years_since_incorporation = 2024 - incorporation_year
        if years_since_incorporation <= 10:
            deductions.append({
                "section": "80IAC",
                "name": "Startup Tax Exemption",
                "description": "100% tax exemption for 3 consecutive years out of first 10 years",
                "max_deduction": financial_data.get("net_profit", 0),
                "eligibility": "Must have DPIIT recognition",
                "savings": financial_data.get("net_profit", 0) * 0.25,
                "priority": "High"
            })

        # Section 35(1)(ii) - R&D expenses
        rd_expenses = context.get("rd_expenses", 300000) if context else 300000
        deductions.append({
            "section": "35(1)(ii)",
            "name": "R&D Expenditure Deduction",
            "description": "150% weighted deduction for in-house R&D",
            "max_deduction": rd_expenses * 1.5,
            "eligibility": "Must maintain R&D records",
            "savings": rd_expenses * 0.5 * 0.25,
            "priority": "Medium"
        })

        # Depreciation on IT equipment
        it_assets = context.get("it_assets", 500000) if context else 500000
        depreciation = it_assets * 0.40  # 40% depreciation on computers
        deductions.append({
            "section": "32",
            "name": "Depreciation on IT Equipment",
            "description": "40% depreciation on computers and software",
            "max_deduction": depreciation,
            "eligibility": "Automatic",
            "savings": depreciation * 0.25,
            "priority": "High"
        })

        # Use LLM to identify additional deductions based on business profile
        try:
            if self.llm:
                # Retrieve tax deduction information from RAG
                deduction_context = ""
                if self.config.use_rag and self.rag_service:
                    deduction_docs = await self._retrieve_context(
                        f"tax deductions India business {financial_data.get('business_type', 'startup')}"
                    )
                    if deduction_docs:
                        deduction_context = "\n\n".join([
                            f"**{doc.get('metadata', {}).get('title', 'Tax Guide')}**\n{doc.get('content', '')[:400]}"
                            for doc in deduction_docs[:3]
                        ])

                # Build LLM prompt for deduction identification
                deduction_prompt = f"""You are a tax deduction expert. Identify additional applicable tax deductions:

Business Profile:
- Type: {financial_data.get('business_type', 'Private Limited')}
- Revenue: ₹{financial_data.get('revenue', 0):,.0f}
- Net Profit: ₹{financial_data.get('net_profit', 0):,.0f}
- Industry: {context.get('industry', 'Technology') if context else 'Technology'}
- Employees: {context.get('employees', 10) if context else 10}
- R&D Expenses: ₹{rd_expenses:,.0f}
- IT Assets: ₹{it_assets:,.0f}

Tax Deduction Knowledge:
{deduction_context if deduction_context else "Using standard tax code knowledge"}

Already Identified Deductions:
{', '.join([d['section'] for d in deductions])}

Please identify 2-3 additional tax deductions this business might be eligible for.
Consider: Section 80G (donations), Section 35AD (specified businesses), Section 10AA (SEZ units), etc.

Return ONLY a JSON array:
[
  {{
    "section": "section code",
    "name": "deduction name",
    "description": "brief description",
    "estimated_benefit": <amount in INR>,
    "eligibility_criteria": "key requirements",
    "priority": "High|Medium|Low",
    "action_required": "what business needs to do"
  }}
]
"""

                llm_response = await self.llm.generate(
                    prompt=deduction_prompt,
                    temperature=0.3,
                    max_tokens=1000
                )

                # Parse JSON response
                import json
                import re
                json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
                if json_match:
                    additional_deductions = json.loads(json_match.group(0))

                    # Add LLM-identified deductions
                    for deduction in additional_deductions[:3]:  # Max 3 additional
                        deductions.append({
                            "section": deduction.get("section", "N/A"),
                            "name": deduction.get("name", "Additional Deduction"),
                            "description": deduction.get("description", ""),
                            "max_deduction": deduction.get("estimated_benefit", 0),
                            "eligibility": deduction.get("eligibility_criteria", ""),
                            "savings": deduction.get("estimated_benefit", 0) * 0.25,  # Approximate
                            "priority": deduction.get("priority", "Medium"),
                            "action_required": deduction.get("action_required", "")
                        })

        except Exception as e:
            print(f"LLM deduction identification failed: {e}. Using rule-based deductions only.")

        return deductions

    async def _generate_tax_strategy(
        self,
        tax_calculation: Dict[str, Any],
        deductions: List[Dict[str, Any]],
        context: Optional[Dict]
    ) -> str:
        """
        Generate tax optimization strategy using LLM-powered analysis

        Args:
            tax_calculation: Tax calculation
            deductions: Identified deductions
            context: User context

        Returns:
            Strategy text
        """
        total_tax = tax_calculation.get("total_tax_before_deductions", 0)
        total_savings = sum(d.get("savings", 0) for d in deductions)
        optimized_tax = total_tax - total_savings

        # Use LLM to generate personalized tax strategy
        try:
            if self.llm:
                # Build comprehensive context
                strategy_prompt = f"""{self.get_system_prompt()}

Generate a comprehensive tax optimization strategy for this business:

**Financial Overview:**
- Net Profit: ₹{tax_calculation.get('net_profit', 0):,.0f}
- Base Tax Rate: {tax_calculation.get('base_tax_rate', 0):.1f}%
- Tax Before Deductions: ₹{total_tax:,.0f}
- Business Type: {context.get('business_type', 'Private Limited') if context else 'Private Limited'}
- Industry: {context.get('industry', 'Technology') if context else 'Technology'}

**Identified Deductions ({len(deductions)} total):**
{chr(10).join(f"- {d['section']} - {d['name']}: ₹{d.get('savings', 0):,.0f} savings (Priority: {d.get('priority', 'N/A')})" for d in deductions)}

**Calculated Savings:**
- Total Deductions: ₹{total_savings:,.0f}
- Optimized Tax: ₹{optimized_tax:,.0f}
- Savings Percentage: {(total_savings/total_tax*100) if total_tax > 0 else 0:.1f}%

Please generate a comprehensive tax strategy including:

1. **Executive Summary** (2-3 sentences on key insights)
2. **Deduction Prioritization** (which deductions to pursue first and why)
3. **Action Plan** with specific timelines:
   - Immediate actions (this month)
   - Short-term actions (1-3 months)
   - Long-term planning (quarterly/annually)
4. **Risk Mitigation** (compliance risks and how to avoid them)
5. **Additional Opportunities** (advanced tax strategies not yet captured)
6. **Important Deadlines** with specific dates
7. **Professional Advisory** (when to consult a CA)

Format using markdown with clear sections and bullet points.
Include specific rupee amounts and percentages where relevant.
Be practical and actionable for a busy entrepreneur.
"""

                llm_response = await self.llm.generate(
                    prompt=strategy_prompt,
                    temperature=0.4,
                    max_tokens=2000
                )

                # Add disclaimer
                llm_response += f"""

---

**📊 Tax Calculation Summary:**
- Net Profit: ₹{tax_calculation.get('net_profit', 0):,.0f}
- Tax Before Deductions: ₹{total_tax:,.0f}
- Total Deductions: ₹{total_savings:,.0f}
- **Final Tax Liability: ₹{optimized_tax:,.0f}**
- **Tax Savings: ₹{total_savings:,.0f}** ({(total_savings/total_tax*100) if total_tax > 0 else 0:.1f}% reduction)

**⚠️ Important Disclaimer:**
This is AI-generated tax guidance for informational purposes only. Tax laws are complex and change frequently.
Please consult a licensed Chartered Accountant (CA) for:
- Final tax filing and compliance
- Verification of deductions and calculations
- Audit representation
- Legal compliance confirmation
- Business-specific tax planning
"""

                return llm_response

        except Exception as e:
            print(f"LLM strategy generation failed: {e}. Using template response.")

        # Fallback template response
        return f"""**Tax Optimization Strategy**

**Current Tax Liability:**
- Net Profit: ₹{tax_calculation.get('net_profit', 0):,.0f}
- Tax Rate: {tax_calculation.get('base_tax_rate', 0):.1f}%
- Tax Before Deductions: ₹{total_tax:,.0f}

**Available Deductions:**
{chr(10).join(f"✓ {d['section']} - {d['name']}: ₹{d['savings']:,.0f} savings" for d in deductions)}

**Optimized Tax Liability:**
- Total Deductions: ₹{total_savings:,.0f}
- **Final Tax: ₹{optimized_tax:,.0f}**
- **Total Savings: ₹{total_savings:,.0f}** ({(total_savings/total_tax*100) if total_tax > 0 else 0:.1f}% reduction)

**Recommended Actions:**

1. **Immediate (This Month):**
   - Apply for Section 80IAC if eligible (100% exemption possible)
   - Document R&D expenses with proper categorization
   - Prepare depreciation schedule for IT assets

2. **Within 30 Days:**
   - Gather supporting documents for all deductions
   - Consult CA for tax filing strategy
   - Review salary structure for tax optimization

3. **Quarterly:**
   - File advance tax (if applicable)
   - Track deductible expenses monthly
   - Update R&D documentation

**Important Deadlines:**
- Advance Tax Q1: June 15
- Advance Tax Q2: September 15
- Advance Tax Q3: December 15
- Advance Tax Q4: March 15
- ITR Filing: July 31 (for companies: September 30)

**⚠️ Disclaimer:**
This is AI-generated tax guidance. Please consult a licensed Chartered Accountant for:
- Final tax filing
- Complex deductions
- Audit representation
- Legal compliance verification
"""

    def _create_compliance_checklist(self, context: Optional[Dict]) -> List[Dict[str, Any]]:
        """
        Create tax compliance checklist

        Args:
            context: User context

        Returns:
            Compliance checklist
        """
        return [
            {
                "item": "File ITR (Income Tax Return)",
                "deadline": "September 30, 2024",
                "status": "pending",
                "priority": "Critical"
            },
            {
                "item": "Pay Advance Tax - Q1",
                "deadline": "June 15, 2024",
                "status": "pending",
                "priority": "High"
            },
            {
                "item": "Maintain books of accounts",
                "deadline": "Continuous",
                "status": "ongoing",
                "priority": "High"
            },
            {
                "item": "TDS return filing (if applicable)",
                "deadline": "Quarterly",
                "status": "pending",
                "priority": "Medium"
            },
            {
                "item": "GST returns (if registered)",
                "deadline": "Monthly",
                "status": "ongoing",
                "priority": "High"
            }
        ]
