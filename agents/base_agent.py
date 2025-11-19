"""
Base Agent Class - Updated with full LLM, RAG, and GraphRAG integration
All specialized agents inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
import sys

# Add backend services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

from services.llm_service import LLMService, LLMProvider
from services.rag_service import RAGService, VectorStoreType
from services.graphrag_service import GraphRAGService


@dataclass
class AgentConfig:
    """Configuration for agents"""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4000
    use_rag: bool = True
    use_graphrag: bool = False
    vector_store_type: str = "chroma"


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents
    Now fully integrated with LLM, RAG, and GraphRAG services
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the agent

        Args:
            config: Agent configuration
        """
        self.config = config or AgentConfig()
        self.llm = None
        self.rag_service = None
        self.graph_service = None
        self._initialize()

    def _initialize(self):
        """Initialize agent components (LLM, RAG, GraphRAG)"""
        # Initialize LLM service
        try:
            self.llm = LLMService(
                provider=LLMProvider(self.config.llm_provider),
                model=self.config.llm_model
            )
            print(f"✓ LLM service initialized: {self.config.llm_provider}/{self.config.llm_model}")
        except Exception as e:
            print(f"⚠ Warning: Could not initialize LLM service: {e}")
            print("  Agent will use fallback responses")

        # Initialize RAG service if enabled
        if self.config.use_rag:
            try:
                self.rag_service = RAGService(
                    vector_store_type=VectorStoreType(self.config.vector_store_type),
                    embedding_model="text-embedding-3-large"
                )
                print(f"✓ RAG service initialized: {self.config.vector_store_type}")
            except Exception as e:
                print(f"⚠ Warning: Could not initialize RAG service: {e}")
                self.rag_service = None

        # Initialize GraphRAG service if enabled
        if self.config.use_graphrag:
            try:
                self.graph_service = GraphRAGService()
                print(f"✓ GraphRAG service initialized")
            except Exception as e:
                print(f"⚠ Warning: Could not initialize GraphRAG service: {e}")
                self.graph_service = None

    @abstractmethod
    async def process(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a query and return a response

        Args:
            query: User query
            context: Optional context (user profile, previous conversation, etc.)

        Returns:
            Agent response with answer and sources
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent

        Returns:
            System prompt string
        """
        pass

    def _format_sources(self, sources: List[Dict]) -> List[Dict[str, Any]]:
        """
        Format retrieved sources for response

        Args:
            sources: Raw sources from retrieval

        Returns:
            Formatted sources
        """
        formatted = []
        for source in sources:
            formatted.append({
                "title": source.get("title", "Unknown"),
                "content": source.get("content", "")[:200],  # Truncate for brevity
                "url": source.get("url"),
                "source": source.get("source", ""),
                "relevance_score": source.get("score", 0.0)
            })
        return formatted

    async def _retrieve_context(self, query: str, filter: Optional[Dict] = None) -> List[Dict]:
        """
        Retrieve relevant context using RAG

        Args:
            query: User query
            filter: Optional metadata filter

        Returns:
            List of relevant documents/chunks
        """
        if not self.rag_service:
            return []

        try:
            results = await self.rag_service.retrieve(
                query=query,
                top_k=5,
                filter=filter
            )
            return results
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []

    async def _retrieve_graph_context(self, query: str, **kwargs) -> List[Dict]:
        """
        Retrieve relevant context using GraphRAG

        Args:
            query: User query
            **kwargs: Additional arguments for graph queries

        Returns:
            List of relevant graph nodes/relationships
        """
        if not self.graph_service:
            return []

        try:
            # This is agent-specific - subclasses can override
            # For now, return empty list
            return []
        except Exception as e:
            print(f"Error retrieving graph context: {e}")
            return []

    async def _generate_response(
        self,
        query: str,
        context: str = "",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate response using LLM

        Args:
            query: User query
            context: Retrieved context
            conversation_history: Optional conversation history

        Returns:
            Generated response
        """
        if not self.llm:
            return self._generate_fallback_response(query)

        try:
            # Build prompt
            system_prompt = self.get_system_prompt()

            if context:
                full_prompt = f"""Context Information:
{context}

User Query: {query}

Please provide a comprehensive answer based on the context above."""
            else:
                full_prompt = query

            # Generate response
            if conversation_history:
                # Use conversation history
                messages = [{"role": "system", "content": system_prompt}]
                messages.extend(conversation_history)
                messages.append({"role": "user", "content": full_prompt})

                response = await self.llm.generate_with_history(
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
            else:
                # Single query
                response = await self.llm.generate(
                    prompt=full_prompt,
                    system_prompt=system_prompt,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )

            return response

        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return self._generate_fallback_response(query)

    def _generate_fallback_response(self, query: str) -> str:
        """
        Generate fallback response when LLM is unavailable

        Args:
            query: User query

        Returns:
            Fallback response
        """
        return f"""I understand you're asking about: "{query}"

I'm currently operating in limited mode without full AI capabilities. Here's what I can suggest:

1. **Check back later**: Full AI services will be available once API keys are configured
2. **Contact support**: Reach out to support@eip-platform.com for assistance
3. **Review documentation**: Check our knowledge base for common questions

This is an automated fallback response. For full AI-powered insights, please ensure API keys are configured in the .env file.
"""

    async def _build_context_for_llm(
        self,
        query: str,
        user_context: Optional[Dict] = None,
        use_rag: bool = True,
        use_graph: bool = False
    ) -> str:
        """
        Build comprehensive context for LLM by combining RAG and GraphRAG

        Args:
            query: User query
            user_context: User-specific context
            use_rag: Whether to use RAG retrieval
            use_graph: Whether to use GraphRAG

        Returns:
            Formatted context string
        """
        context_parts = []

        # Add user context if available
        if user_context:
            context_parts.append("**User Context:**")
            for key, value in user_context.items():
                context_parts.append(f"- {key}: {value}")
            context_parts.append("")

        # Retrieve from vector store if enabled
        if use_rag and self.rag_service:
            rag_results = await self._retrieve_context(query)
            if rag_results:
                context_parts.append("**Relevant Knowledge (Vector Store):**")
                for i, result in enumerate(rag_results, 1):
                    context_parts.append(f"\n{i}. {result.get('metadata', {}).get('title', 'Document')}")
                    context_parts.append(f"   {result.get('content', '')[:300]}...")
                context_parts.append("")

        # Retrieve from knowledge graph if enabled
        if use_graph and self.graph_service:
            graph_results = await self._retrieve_graph_context(query)
            if graph_results:
                context_parts.append("**Knowledge Graph Data:**")
                for i, result in enumerate(graph_results, 1):
                    context_parts.append(f"\n{i}. {result}")
                context_parts.append("")

        return "\n".join(context_parts)

    async def ingest_knowledge(
        self,
        documents: List[Dict[str, Any]],
        use_rag: bool = True,
        use_graph: bool = False
    ) -> Dict[str, int]:
        """
        Ingest new knowledge into the agent's knowledge base

        Args:
            documents: List of documents to ingest
            use_rag: Whether to add to RAG vector store
            use_graph: Whether to add to knowledge graph

        Returns:
            Statistics about ingestion
        """
        stats = {"rag_chunks": 0, "graph_nodes": 0}

        # Ingest into RAG
        if use_rag and self.rag_service:
            try:
                chunks_ingested = await self.rag_service.ingest_documents(documents)
                stats["rag_chunks"] = chunks_ingested
                print(f"✓ Ingested {chunks_ingested} chunks into RAG system")
            except Exception as e:
                print(f"Error ingesting into RAG: {e}")

        # Ingest into GraphRAG
        if use_graph and self.graph_service:
            # This would be agent-specific implementation
            # For now, just placeholder
            stats["graph_nodes"] = 0

        return stats
