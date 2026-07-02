"""
Unit tests for RAG Service
"""
import pytest
from backend.app.services.rag_service import (
    RAGService,
    VectorStoreType,
    ChromaVectorStore,
    PineconeVectorStore
)


class TestRAGService:
    """Test suite for RAG Service"""

    def test_vector_store_type_enum(self):
        """Test vector store type enumeration"""
        assert VectorStoreType.CHROMA == "chroma"
        assert VectorStoreType.PINECONE == "pinecone"
        assert VectorStoreType.WEAVIATE == "weaviate"

    def test_service_initialization_chroma(self):
        """Test service initialization with Chroma"""
        service = RAGService(
            vector_store_type=VectorStoreType.CHROMA,
            embedding_model="text-embedding-3-large"
        )
        assert service.vector_store_type == VectorStoreType.CHROMA

    @pytest.mark.asyncio
    async def test_chunk_documents(self, rag_service):
        """Test document chunking"""
        documents = [
            {
                "content": "This is a test document. " * 100,  # Long document
                "metadata": {"source": "test.pdf", "page": 1}
            }
        ]

        chunks = await rag_service.chunk_documents(
            documents,
            chunk_size=200,
            chunk_overlap=50
        )

        assert len(chunks) > 1  # Should be chunked
        assert all("content" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    @pytest.mark.requires_api_keys
    async def test_generate_embeddings(self, rag_service):
        """Test embedding generation"""
        texts = ["Hello world", "This is a test"]

        embeddings = await rag_service.generate_embeddings(texts)

        assert len(embeddings) == 2
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)

    @pytest.mark.asyncio
    @pytest.mark.requires_api_keys
    async def test_add_documents(self, rag_service):
        """Test adding documents to vector store"""
        documents = [
            {
                "content": "Test document 1",
                "metadata": {"source": "test1.pdf"}
            },
            {
                "content": "Test document 2",
                "metadata": {"source": "test2.pdf"}
            }
        ]

        doc_ids = await rag_service.add_documents(documents)

        assert len(doc_ids) == 2
        assert all(isinstance(doc_id, str) for doc_id in doc_ids)

    @pytest.mark.asyncio
    @pytest.mark.requires_api_keys
    async def test_search_similar_documents(self, rag_service):
        """Test similarity search"""
        # First add documents
        documents = [
            {"content": "Machine learning is a subset of AI", "metadata": {"topic": "ML"}},
            {"content": "Python is a programming language", "metadata": {"topic": "Programming"}},
        ]
        await rag_service.add_documents(documents)

        # Then search
        results = await rag_service.search(
            query="What is machine learning?",
            top_k=2
        )

        assert len(results) <= 2
        assert all("content" in doc for doc in results)
        assert all("score" in doc for doc in results)

    @pytest.mark.asyncio
    async def test_format_context_for_llm(self, rag_service):
        """Test context formatting for LLM"""
        documents = [
            {"content": "Doc 1", "metadata": {"source": "s1"}, "score": 0.95},
            {"content": "Doc 2", "metadata": {"source": "s2"}, "score": 0.85},
        ]

        context = rag_service.format_context_for_llm(documents)

        assert isinstance(context, str)
        assert "Doc 1" in context
        assert "Doc 2" in context
        assert "source" in context.lower()
