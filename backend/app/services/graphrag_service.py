"""
GraphRAG Service - Graph-based Retrieval Augmented Generation
Uses Neo4j for knowledge graph storage and traversal
"""
from typing import List, Dict, Any, Optional, Tuple
import os
from dataclasses import dataclass


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph"""
    id: str
    label: str
    properties: Dict[str, Any]


@dataclass
class GraphRelationship:
    """Represents a relationship in the knowledge graph"""
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any]


class GraphRAGService:
    """
    GraphRAG Service for knowledge graph operations
    Uses Neo4j as the graph database
    """

    def __init__(
        self,
        uri: str = None,
        username: str = None,
        password: str = None
    ):
        """
        Initialize GraphRAG service

        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
        """
        try:
            from neo4j import GraphDatabase
        except ImportError:
            raise ImportError("Please install neo4j: pip install neo4j")

        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password)
        )

    def close(self):
        """Close the database connection"""
        self.driver.close()

    async def add_node(
        self,
        label: str,
        properties: Dict[str, Any],
        node_id: Optional[str] = None
    ) -> str:
        """
        Add a node to the knowledge graph

        Args:
            label: Node label (e.g., 'Policy', 'Company', 'Market')
            properties: Node properties
            node_id: Optional custom node ID

        Returns:
            Node ID
        """
        with self.driver.session() as session:
            result = session.run(
                f"""
                CREATE (n:{label} $props)
                RETURN elementId(n) as id
                """,
                props=properties
            )
            record = result.single()
            return record["id"] if record else None

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a relationship between two nodes

        Args:
            source_id: Source node ID
            target_id: Target node ID
            relationship_type: Relationship type (e.g., 'AFFECTS', 'COMPETES_WITH')
            properties: Optional relationship properties

        Returns:
            Success status
        """
        props = properties or {}
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (source), (target)
                WHERE elementId(source) = $source_id AND elementId(target) = $target_id
                CREATE (source)-[r:{relationship_type} $props]->(target)
                RETURN r
                """,
                source_id=source_id,
                target_id=target_id,
                props=props
            )
            return result.single() is not None

    async def query_neighbors(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both",
        max_depth: int = 1
    ) -> List[GraphNode]:
        """
        Query neighboring nodes

        Args:
            node_id: Starting node ID
            relationship_type: Optional relationship type filter
            direction: Direction ('outgoing', 'incoming', 'both')
            max_depth: Maximum traversal depth

        Returns:
            List of neighboring nodes
        """
        direction_pattern = {
            "outgoing": "->",
            "incoming": "<-",
            "both": "-"
        }
        pattern = direction_pattern.get(direction, "-")

        rel_filter = f":{relationship_type}" if relationship_type else ""

        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (start){pattern}[r{rel_filter}*1..{max_depth}]{pattern}(neighbor)
                WHERE elementId(start) = $node_id
                RETURN DISTINCT elementId(neighbor) as id, labels(neighbor) as labels, properties(neighbor) as props
                """,
                node_id=node_id
            )

            neighbors = []
            for record in result:
                neighbors.append(GraphNode(
                    id=record["id"],
                    label=record["labels"][0] if record["labels"] else "Unknown",
                    properties=dict(record["props"])
                ))

            return neighbors

    async def query_graph(
        self,
        query: str,
        params: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a custom Cypher query

        Args:
            query: Cypher query string
            params: Query parameters

        Returns:
            Query results
        """
        params = params or {}
        with self.driver.session() as session:
            result = session.run(query, **params)
            return [dict(record) for record in result]

    async def find_policy_impacts(
        self,
        policy_title: str,
        business_sector: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find how a policy affects companies/markets

        Args:
            policy_title: Policy title or keywords
            business_sector: Optional sector filter

        Returns:
            List of affected entities with relationships
        """
        sector_filter = "AND c.sector = $sector" if business_sector else ""

        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (p:Policy)-[r:AFFECTS]->(c:Company)
                WHERE p.title CONTAINS $policy_title {sector_filter}
                RETURN p.title as policy,
                       c.name as company,
                       c.sector as sector,
                       r.impact_level as impact,
                       r.description as impact_description
                ORDER BY r.impact_level DESC
                LIMIT 20
                """,
                policy_title=policy_title,
                sector=business_sector
            )

            impacts = []
            for record in result:
                impacts.append({
                    "policy": record["policy"],
                    "company": record["company"],
                    "sector": record["sector"],
                    "impact_level": record["impact"],
                    "description": record["impact_description"]
                })

            return impacts

    async def find_competitors(
        self,
        company_name: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find competitors for a given company

        Args:
            company_name: Company name
            max_results: Maximum number of results

        Returns:
            List of competitors with relationship details
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c1:Company)-[r:COMPETES_WITH]-(c2:Company)
                WHERE c1.name CONTAINS $company_name
                RETURN c2.name as competitor,
                       c2.sector as sector,
                       c2.market_share as market_share,
                       r.intensity as competition_intensity
                ORDER BY r.intensity DESC
                LIMIT $limit
                """,
                company_name=company_name,
                limit=max_results
            )

            competitors = []
            for record in result:
                competitors.append({
                    "name": record["competitor"],
                    "sector": record["sector"],
                    "market_share": record["market_share"],
                    "competition_intensity": record["competition_intensity"]
                })

            return competitors

    async def find_market_opportunities(
        self,
        sector: str,
        min_growth_rate: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        Find market opportunities in a sector

        Args:
            sector: Business sector
            min_growth_rate: Minimum growth rate percentage

        Returns:
            List of market opportunities
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Market)
                WHERE m.sector = $sector AND m.growth_rate >= $min_growth
                OPTIONAL MATCH (c:Company)-[:SERVES]->(m)
                WITH m, count(c) as company_count
                RETURN m.name as market,
                       m.size as market_size,
                       m.growth_rate as growth_rate,
                       company_count,
                       m.barriers_to_entry as barriers
                ORDER BY m.growth_rate DESC
                """,
                sector=sector,
                min_growth=min_growth_rate
            )

            opportunities = []
            for record in result:
                opportunities.append({
                    "market": record["market"],
                    "size": record["market_size"],
                    "growth_rate": record["growth_rate"],
                    "competitors_count": record["company_count"],
                    "barriers": record["barriers"]
                })

            return opportunities

    async def find_legal_precedents(
        self,
        case_type: str,
        jurisdiction: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find legal precedents/cases

        Args:
            case_type: Type of legal case
            jurisdiction: Optional jurisdiction filter

        Returns:
            List of relevant legal cases
        """
        jurisdiction_filter = "AND l.jurisdiction = $jurisdiction" if jurisdiction else ""

        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (l:LegalCase)
                WHERE l.case_type = $case_type {jurisdiction_filter}
                OPTIONAL MATCH (l)-[:CITES]->(precedent:LegalCase)
                RETURN l.case_id as case_id,
                       l.summary as summary,
                       l.outcome as outcome,
                       l.year as year,
                       collect(precedent.case_id) as cited_precedents
                ORDER BY l.year DESC
                LIMIT 10
                """,
                case_type=case_type,
                jurisdiction=jurisdiction
            )

            cases = []
            for record in result:
                cases.append({
                    "case_id": record["case_id"],
                    "summary": record["summary"],
                    "outcome": record["outcome"],
                    "year": record["year"],
                    "cited_precedents": record["cited_precedents"]
                })

            return cases

    async def populate_sample_data(self):
        """Populate graph with sample data for demonstration"""
        with self.driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")

            # Create sample policies
            session.run("""
                CREATE (p1:Policy {
                    title: 'Startup India Initiative',
                    description: 'Government initiative to promote startups',
                    date: date('2024-01-01'),
                    category: 'business_promotion'
                })
                CREATE (p2:Policy {
                    title: 'New Tax Regulations for SaaS',
                    description: 'Updated tax framework for SaaS companies',
                    date: date('2024-02-15'),
                    category: 'taxation'
                })
            """)

            # Create sample companies
            session.run("""
                CREATE (c1:Company {
                    name: 'TechCorp India',
                    sector: 'SaaS',
                    market_share: 15.5,
                    revenue: 5000000
                })
                CREATE (c2:Company {
                    name: 'InnoSoft Solutions',
                    sector: 'SaaS',
                    market_share: 12.3,
                    revenue: 3500000
                })
                CREATE (c3:Company {
                    name: 'GreenEnergy Startups',
                    sector: 'CleanTech',
                    market_share: 8.2,
                    revenue: 2000000
                })
            """)

            # Create sample markets
            session.run("""
                CREATE (m1:Market {
                    name: 'Indian SaaS Market',
                    sector: 'SaaS',
                    size: 2500000000,
                    growth_rate: 18.5,
                    barriers_to_entry: 'medium'
                })
                CREATE (m2:Market {
                    name: 'CleanTech India',
                    sector: 'CleanTech',
                    size: 1000000000,
                    growth_rate: 25.0,
                    barriers_to_entry: 'high'
                })
            """)

            # Create relationships
            session.run("""
                MATCH (p:Policy {title: 'Startup India Initiative'})
                MATCH (c:Company)
                WHERE c.sector IN ['SaaS', 'CleanTech']
                CREATE (p)-[:AFFECTS {impact_level: 'high', description: 'Provides tax exemptions and funding support'}]->(c)
            """)

            session.run("""
                MATCH (c1:Company {name: 'TechCorp India'})
                MATCH (c2:Company {name: 'InnoSoft Solutions'})
                CREATE (c1)-[:COMPETES_WITH {intensity: 'high'}]->(c2)
            """)

            session.run("""
                MATCH (c:Company)
                MATCH (m:Market)
                WHERE c.sector = m.sector
                CREATE (c)-[:SERVES]->(m)
            """)

            return True

    async def get_graph_stats(self) -> Dict[str, int]:
        """Get statistics about the knowledge graph"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
            """)

            stats = {}
            for record in result:
                stats[record["label"]] = record["count"]

            return stats


# Factory function
def create_graphrag_service(
    uri: str = None,
    username: str = None,
    password: str = None
) -> GraphRAGService:
    """
    Factory function to create GraphRAG service

    Args:
        uri: Neo4j connection URI
        username: Neo4j username
        password: Neo4j password

    Returns:
        GraphRAGService instance
    """
    return GraphRAGService(uri=uri, username=username, password=password)
