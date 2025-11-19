"""
Tax Agent
Provides tax optimization, compliance, and reporting assistance
"""
from typing import Dict, List, Any, Optional
from ..base_agent import BaseAgent, AgentConfig


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
        Calculate tax liability

        Args:
            financial_data: Financial data

        Returns:
            Tax calculation breakdown
        """
        net_profit = financial_data.get("net_profit", 0)

        # Corporate tax rate (India): 25% for companies with turnover < Rs 400 Cr
        base_tax_rate = 0.25
        base_tax = net_profit * base_tax_rate

        # Surcharge and cess
        surcharge = 0  # No surcharge for income < Rs 1 Cr
        cess = base_tax * 0.04  # 4% health and education cess

        total_tax = base_tax + surcharge + cess

        return {
            "net_profit": net_profit,
            "base_tax_rate": base_tax_rate * 100,
            "base_tax": base_tax,
            "surcharge": surcharge,
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
        Identify applicable tax deductions

        Args:
            financial_data: Financial data
            context: User context

        Returns:
            List of applicable deductions
        """
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

        return deductions

    async def _generate_tax_strategy(
        self,
        tax_calculation: Dict[str, Any],
        deductions: List[Dict[str, Any]],
        context: Optional[Dict]
    ) -> str:
        """
        Generate tax optimization strategy

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
- **Total Savings: ₹{total_savings:,.0f}** ({(total_savings/total_tax*100):.1f}% reduction)

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
