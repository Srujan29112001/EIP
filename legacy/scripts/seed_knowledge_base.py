"""
Knowledge Base Seeding Script
Seeds Neo4j knowledge graph and Vector Store with initial data
"""
import asyncio
import os
import sys
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

from services.graphrag_service import GraphRAGService
from services.rag_service import RAGService, VectorStoreProvider


class KnowledgeBaseSeeder:
    """Seeds knowledge bases with initial data"""

    def __init__(self):
        """Initialize seeder"""
        self.graphrag = GraphRAGService()
        self.rag = RAGService(provider=VectorStoreProvider.CHROMA)
        self.seeded_count = {"neo4j": 0, "vector_store": 0}

    async def seed_all(self):
        """Seed all knowledge bases"""
        print("=" * 80)
        print("KNOWLEDGE BASE SEEDING")
        print("=" * 80)
        print()

        # Seed Neo4j knowledge graph
        await self.seed_neo4j()

        # Seed Vector Store
        await self.seed_vector_store()

        print()
        print("=" * 80)
        print("SEEDING COMPLETE")
        print(f"Neo4j nodes created: {self.seeded_count['neo4j']}")
        print(f"Vector store documents indexed: {self.seeded_count['vector_store']}")
        print("=" * 80)

    async def seed_neo4j(self):
        """Seed Neo4j knowledge graph with policies, companies, markets"""
        print("\n[1/2] Seeding Neo4j Knowledge Graph...")
        print("-" * 80)

        # Sample policies
        policies = [
            {
                "title": "Startup India Initiative - Section 80IAC",
                "description": "Tax exemption for eligible startups for 3 consecutive years out of first 10 years",
                "category": "tax_benefit",
                "effective_date": "2016-04-01",
                "source": "Ministry of Commerce and Industry"
            },
            {
                "title": "MSME Registration - Udyam Portal",
                "description": "Mandatory registration for Micro, Small and Medium Enterprises",
                "category": "registration",
                "effective_date": "2020-07-01",
                "source": "Ministry of MSME"
            },
            {
                "title": "New GST Compliance Rules 2024",
                "description": "Updated GST filing requirements for businesses above Rs 5 Cr turnover",
                "category": "compliance",
                "effective_date": "2024-04-01",
                "source": "CBIC"
            },
            {
                "title": "Digital India Program",
                "description": "Government initiative to transform India into digitally empowered society",
                "category": "digital_transformation",
                "effective_date": "2015-07-01",
                "source": "Ministry of Electronics and IT"
            },
            {
                "title": "Production Linked Incentive (PLI) Scheme",
                "description": "Financial incentive to boost domestic manufacturing",
                "category": "manufacturing",
                "effective_date": "2020-11-11",
                "source": "Ministry of Commerce"
            },
            {
                "title": "Startup Tax Exemption - Section 115BAA",
                "description": "Reduced corporate tax rate of 22% (15% for new manufacturing companies)",
                "category": "taxation",
                "effective_date": "2019-09-20",
                "source": "Income Tax Department"
            }
        ]

        # Sample companies
        companies = [
            {
                "name": "TechVentures India Pvt Ltd",
                "sector": "SaaS",
                "market_share": 12.5,
                "revenue": 5000000,
                "founded_year": 2020,
                "location": "Bangalore"
            },
            {
                "name": "FinanceFlow Solutions",
                "sector": "FinTech",
                "market_share": 8.3,
                "revenue": 3500000,
                "founded_year": 2019,
                "location": "Mumbai"
            },
            {
                "name": "GreenTech Innovations",
                "sector": "CleanTech",
                "market_share": 5.2,
                "revenue": 2000000,
                "founded_year": 2021,
                "location": "Pune"
            },
            {
                "name": "HealthCare.ai",
                "sector": "HealthTech",
                "market_share": 6.7,
                "revenue": 2800000,
                "founded_year": 2020,
                "location": "Delhi"
            },
            {
                "name": "EduLearn Platform",
                "sector": "EdTech",
                "market_share": 10.1,
                "revenue": 4200000,
                "founded_year": 2018,
                "location": "Bangalore"
            }
        ]

        # Sample markets
        markets = [
            {
                "name": "Indian SaaS Market",
                "sector": "SaaS",
                "size": 2500000000,
                "growth_rate": 18.5,
                "maturity": "growth",
                "barriers_to_entry": "medium"
            },
            {
                "name": "FinTech India",
                "sector": "FinTech",
                "size": 3100000000,
                "growth_rate": 22.3,
                "maturity": "growth",
                "barriers_to_entry": "high"
            },
            {
                "name": "CleanTech Ecosystem",
                "sector": "CleanTech",
                "size": 1000000000,
                "growth_rate": 25.0,
                "maturity": "emerging",
                "barriers_to_entry": "high"
            },
            {
                "name": "HealthTech Innovation Hub",
                "sector": "HealthTech",
                "size": 1800000000,
                "growth_rate": 20.5,
                "maturity": "growth",
                "barriers_to_entry": "high"
            },
            {
                "name": "EdTech Revolution",
                "sector": "EdTech",
                "size": 2000000000,
                "growth_rate": 15.7,
                "maturity": "mature",
                "barriers_to_entry": "medium"
            }
        ]

        # Create policy nodes
        print("  Creating Policy nodes...")
        policy_ids = {}
        for policy in policies:
            policy_id = await self.graphrag.add_node(
                label="Policy",
                properties=policy
            )
            policy_ids[policy["title"]] = policy_id
            self.seeded_count["neo4j"] += 1
            print(f"    ✓ {policy['title'][:60]}")

        # Create company nodes
        print("\n  Creating Company nodes...")
        company_ids = {}
        for company in companies:
            company_id = await self.graphrag.add_node(
                label="Company",
                properties=company
            )
            company_ids[company["name"]] = company_id
            self.seeded_count["neo4j"] += 1
            print(f"    ✓ {company['name']}")

        # Create market nodes
        print("\n  Creating Market nodes...")
        market_ids = {}
        for market in markets:
            market_id = await self.graphrag.add_node(
                label="Market",
                properties=market
            )
            market_ids[market["name"]] = market_id
            self.seeded_count["neo4j"] += 1
            print(f"    ✓ {market['name']}")

        # Create relationships
        print("\n  Creating Relationships...")

        # Policy -> Company relationships
        relationships = [
            (policy_ids["Startup India Initiative - Section 80IAC"], company_ids["TechVentures India Pvt Ltd"], "AFFECTS", {"impact_level": "high", "description": "Eligible for 3-year tax exemption"}),
            (policy_ids["Startup India Initiative - Section 80IAC"], company_ids["GreenTech Innovations"], "AFFECTS", {"impact_level": "high", "description": "Eligible for 3-year tax exemption"}),
            (policy_ids["MSME Registration - Udyam Portal"], company_ids["FinanceFlow Solutions"], "REQUIRES", {"compliance_type": "mandatory", "deadline": "Before operations"}),
            (policy_ids["New GST Compliance Rules 2024"], company_ids["TechVentures India Pvt Ltd"], "AFFECTS", {"impact_level": "medium", "description": "Enhanced GST filing requirements"}),
            (policy_ids["Digital India Program"], company_ids["TechVentures India Pvt Ltd"], "PROVIDES_BENEFIT_TO", {"benefit_type": "infrastructure", "description": "Better digital infrastructure"}),
            (policy_ids["Digital India Program"], company_ids["HealthCare.ai"], "PROVIDES_BENEFIT_TO", {"benefit_type": "connectivity", "description": "Improved healthcare connectivity"}),
        ]

        for source_id, target_id, rel_type, props in relationships:
            await self.graphrag.add_relationship(source_id, target_id, rel_type, props)
            print(f"    ✓ Created {rel_type} relationship")

        # Company -> Company (competition) relationships
        competition = [
            (company_ids["TechVentures India Pvt Ltd"], company_ids["EduLearn Platform"], "COMPETES_WITH", {"intensity": "medium", "overlap": "B2B SaaS"}),
            (company_ids["FinanceFlow Solutions"], company_ids["HealthCare.ai"], "PARTNERS_WITH", {"type": "payment_integration"}),
        ]

        for source_id, target_id, rel_type, props in competition:
            await self.graphrag.add_relationship(source_id, target_id, rel_type, props)
            print(f"    ✓ Created {rel_type} relationship")

        # Company -> Market relationships
        print("\n  Creating Company-Market relationships...")
        for company in companies:
            company_id = company_ids[company["name"]]
            sector = company["sector"]

            # Find matching market
            for market in markets:
                if market["sector"] == sector:
                    market_id = market_ids[market["name"]]
                    await self.graphrag.add_relationship(
                        company_id,
                        market_id,
                        "SERVES",
                        {"active_since": str(company["founded_year"])}
                    )
                    print(f"    ✓ {company['name']} → {market['name']}")
                    break

        print(f"\n  ✓ Neo4j seeding complete ({self.seeded_count['neo4j']} nodes)")

    async def seed_vector_store(self):
        """Seed Vector Store with documents"""
        print("\n[2/2] Seeding Vector Store...")
        print("-" * 80)

        # Policy documents
        policy_docs = [
            {
                "content": """Startup India Initiative - Section 80IAC Tax Exemption

                The Startup India Initiative provides eligible startups with a 100% tax exemption under Section 80IAC of the Income Tax Act for 3 consecutive years out of the first 10 years of incorporation.

                Eligibility Criteria:
                1. Incorporated as a Private Limited Company or LLP
                2. Turnover does not exceed Rs 100 crore in any financial year
                3. Working towards innovation, development, or improvement of products/services
                4. Must obtain DPIIT recognition

                How to Apply:
                1. Register on Startup India portal (startupindia.gov.in)
                2. Obtain DPIIT recognition certificate
                3. File Form 10-IC with Income Tax Department
                4. Submit required documents (incorporation certificate, business plan, investor details)

                Benefits:
                - 100% income tax exemption for 3 years
                - No tax on capital gains
                - Easier patent filing (80% rebate on patent fees)
                - Self-certification for labor and environmental laws

                Deadlines:
                - Apply for DPIIT recognition within 10 years of incorporation
                - File Form 10-IC before claiming exemption in ITR
                """,
                "metadata": {
                    "title": "Startup India Initiative - Section 80IAC",
                    "type": "policy",
                    "category": "tax_benefit",
                    "date": "2016-04-01",
                    "url": "https://www.startupindia.gov.in/content/sih/en/tax-exemption.html"
                }
            },
            {
                "content": """MSME Registration on Udyam Portal - Complete Guide

                As per the Atmanirbhar Bharat initiative, all Micro, Small, and Medium Enterprises (MSMEs) must register on the Udyam Registration portal to avail benefits.

                Classification:
                - Micro: Investment up to Rs 1 crore, Turnover up to Rs 5 crore
                - Small: Investment up to Rs 10 crore, Turnover up to Rs 50 crore
                - Medium: Investment up to Rs 50 crore, Turnover up to Rs 250 crore

                Registration Process:
                1. Visit udyamregistration.gov.in
                2. Provide Aadhaar number of entrepreneur
                3. Fill basic details (name, social category, business details)
                4. Provide bank account and investment/turnover details
                5. Submit (no documents required - Aadhaar validated online)
                6. Receive Udyam Registration Certificate instantly

                Benefits:
                - Priority in government procurement
                - Lower interest rates on business loans (1-1.5% less)
                - Patent registration fee rebate
                - ISO certification fee reimbursement
                - Credit guarantee scheme benefits
                - Protection against delayed payments (45-day payment deadline)

                Key Points:
                - Registration is FREE
                - Lifetime validity
                - Can be updated anytime
                - Required for claiming MSME benefits
                """,
                "metadata": {
                    "title": "MSME Udyam Registration Guide",
                    "type": "policy",
                    "category": "registration",
                    "date": "2020-07-01",
                    "url": "https://udyamregistration.gov.in"
                }
            },
            {
                "content": """Section 35(1)(ii) - R&D Expenditure Deduction for Businesses

                Companies conducting in-house R&D can claim weighted deduction of 150% on revenue expenses and 100% on capital expenses.

                Eligibility:
                - Company should have in-house R&D facility
                - R&D should be related to the business of the company
                - Facility must be approved by the Department of Scientific and Industrial Research (DSIR)

                Covered Expenses:
                Revenue Expenses (150% deduction):
                - Salaries of R&D personnel
                - Consumables and materials used in R&D
                - Utilities for R&D facility
                - Other day-to-day R&D expenses

                Capital Expenses (100% deduction):
                - R&D equipment and machinery
                - Land and building for R&D facility

                Application Process:
                1. Apply to DSIR for in-house R&D facility approval
                2. Maintain separate R&D accounts
                3. File annual progress report to DSIR
                4. Claim deduction in ITR with Form 3CL

                Documentation Required:
                - DSIR approval letter
                - Auditor's certificate (Form 3CL)
                - R&D expenditure statement
                - Details of R&D projects

                Example:
                If your company spends Rs 10 lakh on R&D salaries, you can claim deduction of Rs 15 lakh (150% of Rs 10 lakh), reducing taxable income.
                """,
                "metadata": {
                    "title": "Section 35(1)(ii) - R&D Tax Deduction",
                    "type": "policy",
                    "category": "tax_deduction",
                    "date": "2024-01-01",
                    "url": "https://www.incometax.gov.in/section35"
                }
            }
        ]

        # Market reports
        market_reports = [
            {
                "content": """Indian SaaS Market Report 2024

                Market Size: $2.5 Billion (2024)
                Growth Rate: 18.5% CAGR (2024-2029)
                Market Maturity: Growth Stage

                Key Insights:
                - India is becoming the SaaS capital of the world with 1,000+ SaaS companies
                - B2B SaaS dominates (75% of market), B2C is emerging
                - Top subsectors: HR Tech, Sales Tech, Marketing Automation, Fintech
                - 40% of startups are bootstrapped, 60% venture-funded

                Competitive Landscape:
                - Highly fragmented market with no dominant player
                - Top 10 players hold only 30% market share
                - Increasing consolidation through M&A

                Customer Segments:
                1. SMBs (60% of customers): Price-sensitive, need quick ROI
                2. Mid-market (30%): Value features and integration
                3. Enterprise (10%): Require customization and security

                Entry Strategy for New SaaS Startups:
                1. Start with niche vertical SaaS (avoid horizontal)
                2. Focus on product-led growth (PLG)
                3. Leverage content marketing and SEO
                4. Build for global market from day 1
                5. Price 30-40% lower than US competitors

                Success Metrics:
                - Customer Acquisition Cost (CAC): $200-500 for SMB
                - Lifetime Value (LTV): $3,000-8,000
                - Monthly churn: 3-5% for SMB, <2% for enterprise
                - ARR growth: 100%+ in first 3 years

                Funding Landscape:
                - Average Seed round: $500K-1M
                - Average Series A: $5-10M
                - VCs actively funding: Accel, Sequoia, Matrix, Elevation
                """,
                "metadata": {
                    "title": "Indian SaaS Market Report 2024",
                    "type": "market_report",
                    "sector": "SaaS",
                    "date": "2024-01-15",
                    "market_size": 2500000000,
                    "growth_rate": 0.185,
                    "url": "https://www.ibef.org/saas-report-2024"
                }
            },
            {
                "content": """Fintech India - Market Analysis 2024

                Market Size: $3.1 Billion (2024)
                Growth Rate: 22.3% CAGR
                Total Funding (2023): $2.8 Billion across 120 deals

                Sub-segments:
                1. Digital Payments (45% of market)
                2. Lending (30%)
                3. Wealth Management (15%)
                4. Insurtech (10%)

                Key Drivers:
                - UPI adoption (10B+ transactions/month)
                - Account Aggregator framework
                - Open credit enablement network (OCEN)
                - Digital lending regulations

                Regulatory Landscape:
                - RBI digital lending guidelines (Sept 2022)
                - Account aggregator framework operational
                - NPCI innovation sandbox
                - Data localization requirements

                Competition:
                - PhonePe & Paytm dominate digital payments
                - New lending startups facing regulatory scrutiny
                - Wealth management is emerging opportunity

                Opportunities for New Entrants:
                - Embedded finance (Fintech-as-a-Service)
                - B2B payments and reconciliation
                - SME lending (underserved segment)
                - Cross-border remittances
                - Buy-now-pay-later (BNPL) for B2B

                Challenges:
                - Increasing regulatory oversight
                - Customer acquisition costs rising
                - Need for strong compliance team
                - Capital-intensive (lending businesses)
                """,
                "metadata": {
                    "title": "Fintech India Market Analysis 2024",
                    "type": "market_report",
                    "sector": "FinTech",
                    "date": "2024-02-01",
                    "market_size": 3100000000,
                    "growth_rate": 0.223
                }
            }
        ]

        # Financial best practices
        financial_docs = [
            {
                "content": """Financial Metrics for SaaS Startups - Industry Benchmarks

                Key Metrics to Track:

                1. Monthly Recurring Revenue (MRR)
                   - Target growth: 15-20% month-over-month (early stage)
                   - 5-10% month-over-month (growth stage)

                2. Customer Acquisition Cost (CAC)
                   - SMB SaaS: $200-500
                   - Mid-market: $1,000-3,000
                   - Enterprise: $10,000-50,000
                   - Should recover CAC in <12 months

                3. Lifetime Value (LTV)
                   - Target LTV:CAC ratio of 3:1 or higher
                   - LTV = ARPU × Gross Margin % ÷ Churn Rate

                4. Churn Rate
                   - Monthly churn: <5% (acceptable), <3% (good), <2% (excellent)
                   - Annual churn: <20%
                   - Negative churn (expansion revenue > lost revenue) is ideal

                5. Gross Margin
                   - Target: >75% for SaaS
                   - World-class: >85%

                6. Burn Multiple
                   - Net Burn ÷ Net New ARR
                   - <1x: Exceptional efficiency
                   - 1-1.5x: Great
                   - 1.5-2x: Good
                   - >3x: Concerning

                7. Rule of 40
                   - Growth Rate % + Profit Margin % should be >40%
                   - Example: 60% growth + (-20%) margin = 40% ✓

                Cash Flow Management:
                - Maintain 12-18 months runway
                - Collect payments upfront (annual plans)
                - Negotiate 60-90 day payment terms with vendors
                - Monitor cash conversion cycle

                Pricing Strategy:
                - Don't underprice (common mistake)
                - Offer annual plans at 20% discount
                - Introduce usage-based pricing for scale
                - Regular price increases (10% annually)
                """,
                "metadata": {
                    "title": "SaaS Financial Benchmarks",
                    "type": "financial_best_practices",
                    "sector": "SaaS",
                    "date": "2024-01-01"
                }
            }
        ]

        # Seed each collection
        print("  Seeding 'policies' collection...")
        for doc in policy_docs:
            await self.rag.add_documents(
                collection_name="policies",
                documents=[doc]
            )
            self.seeded_count["vector_store"] += 1
            print(f"    ✓ {doc['metadata']['title']}")

        print("\n  Seeding 'market_reports' collection...")
        for doc in market_reports:
            await self.rag.add_documents(
                collection_name="market_reports",
                documents=[doc]
            )
            self.seeded_count["vector_store"] += 1
            print(f"    ✓ {doc['metadata']['title']}")

        print("\n  Seeding 'financial_knowledge' collection...")
        for doc in financial_docs:
            await self.rag.add_documents(
                collection_name="financial_knowledge",
                documents=[doc]
            )
            self.seeded_count["vector_store"] += 1
            print(f"    ✓ {doc['metadata']['title']}")

        print(f"\n  ✓ Vector store seeding complete ({self.seeded_count['vector_store']} documents)")


async def main():
    """Run seeding"""
    seeder = KnowledgeBaseSeeder()

    try:
        await seeder.seed_all()
        print("\n✅ Knowledge base seeding successful!")
        print("\nYou can now:")
        print("  1. Query policies using the Policy Agent")
        print("  2. Get market insights using the Market Agent")
        print("  3. Access financial benchmarks via Finance Agent")
        print("  4. Explore the knowledge graph via GraphRAG service")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        seeder.graphrag.close()


if __name__ == "__main__":
    asyncio.run(main())
