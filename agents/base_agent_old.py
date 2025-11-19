"""
Base Agent Class
All specialized agents inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os


@dataclass
class AgentConfig:
    """Configuration for agents"""
    llm_model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4000
    use_rag: bool = True
    use_graphrag: bool = False


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the agent

        Args:
            config: Agent configuration
        """
        self.config = config or AgentConfig()
        self.llm = None
        self.retriever = None
        self._initialize()

    def _initialize(self):
        """Initialize agent components (LLM, retriever, etc.)"""
        # TODO: Initialize LLM and retriever
        # For now, placeholder
        pass

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
                "content": source.get("content", ""),
                "url": source.get("url"),
                "relevance_score": source.get("score", 0.0)
            })
        return formatted

    async def _retrieve_context(self, query: str) -> List[Dict]:
        """
        Retrieve relevant context using RAG

        Args:
            query: User query

        Returns:
            List of relevant documents/chunks
        """
        # TODO: Implement RAG retrieval
        # Placeholder for now
        return []

    async def _generate_response(self, query: str, context: str) -> str:
        """
        Generate response using LLM

        Args:
            query: User query
            context: Retrieved context

        Returns:
            Generated response
        """
        # TODO: Implement LLM generation
        # Placeholder for now
        return f"Generated response for: {query}"
