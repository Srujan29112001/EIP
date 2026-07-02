"""
RAG Service - Retrieval Augmented Generation
Supports Chroma (local) and Pinecone (cloud) vector stores
"""
from typing import List, Dict, Any, Optional
from enum import Enum
import os
from abc import ABC, abstractmethod
import hashlib


class VectorStoreType(str, Enum):
    """Supported vector store types"""
    CHROMA = "chroma"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"


class BaseVectorStore(ABC):
    """Abstract base class for vector stores"""

    @abstractmethod
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict]] = None
    ) -> List[str]:
        """Add documents to vector store"""
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        pass

    @abstractmethod
    async def delete(self, ids: List[str]) -> bool:
        """Delete documents by IDs"""
        pass


class ChromaVectorStore(BaseVectorStore):
    """Chroma vector store implementation (local/self-hosted)"""

    def __init__(self, collection_name: str = "eip_knowledge", persist_directory: str = "./chroma_db"):
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError("Please install chromadb: pip install chromadb")

        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Initialize Chroma client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "EIP knowledge base"}
            )

    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict]] = None
    ) -> List[str]:
        """Add documents to Chroma"""
        # Generate IDs if not provided
        ids = []
        texts = []
        metadatas = metadata or []

        for i, doc in enumerate(documents):
            # Generate unique ID based on content hash
            content = doc.get("content", "")
            doc_id = hashlib.md5(content.encode()).hexdigest()
            ids.append(doc_id)
            texts.append(content)

            # Add metadata
            if i < len(metadatas):
                metadatas[i]["title"] = doc.get("title", "")
                metadatas[i]["source"] = doc.get("source", "")
            else:
                metadatas.append({
                    "title": doc.get("title", ""),
                    "source": doc.get("source", "")
                })

        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

        return ids

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search Chroma for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter
        )

        # Format results
        formatted_results = []
        if results and 'documents' in results:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "score": 1 - results['distances'][0][i] if results['distances'] else 0.0
                })

        return formatted_results

    async def delete(self, ids: List[str]) -> bool:
        """Delete documents from Chroma"""
        try:
            self.collection.delete(ids=ids)
            return True
        except Exception:
            return False


class PineconeVectorStore(BaseVectorStore):
    """Pinecone vector store implementation (cloud)"""

    def __init__(
        self,
        api_key: str,
        environment: str,
        index_name: str = "eip-knowledge",
        dimension: int = 1536
    ):
        try:
            import pinecone
        except ImportError:
            raise ImportError("Please install pinecone: pip install pinecone-client")

        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension

        # Initialize Pinecone
        pinecone.init(api_key=api_key, environment=environment)

        # Create index if it doesn't exist
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine"
            )

        self.index = pinecone.Index(index_name)

    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict]] = None
    ) -> List[str]:
        """Add documents to Pinecone"""
        vectors = []
        ids = []

        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Generate unique ID
            content = doc.get("content", "")
            doc_id = hashlib.md5(content.encode()).hexdigest()
            ids.append(doc_id)

            # Prepare metadata
            meta = metadata[i] if metadata and i < len(metadata) else {}
            meta.update({
                "title": doc.get("title", ""),
                "content": content[:1000],  # Pinecone metadata has size limits
                "source": doc.get("source", "")
            })

            vectors.append((doc_id, embedding, meta))

        # Upsert to Pinecone
        self.index.upsert(vectors=vectors)

        return ids

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search Pinecone for similar documents"""
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filter,
            include_metadata=True
        )

        # Format results
        formatted_results = []
        for match in results.get('matches', []):
            formatted_results.append({
                "id": match.get('id'),
                "content": match.get('metadata', {}).get('content', ''),
                "metadata": match.get('metadata', {}),
                "score": match.get('score', 0.0)
            })

        return formatted_results

    async def delete(self, ids: List[str]) -> bool:
        """Delete documents from Pinecone"""
        try:
            self.index.delete(ids=ids)
            return True
        except Exception:
            return False


class EmbeddingService:
    """Service for generating embeddings"""

    def __init__(self, model: str = "text-embedding-3-large", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    async def embed_text(self, text: str) -> List[float]:
        """Embed single text"""
        return await self.embed_batch([text])[0]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed batch of texts"""
        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "input": texts
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()

            embeddings = []
            for item in sorted(result['data'], key=lambda x: x['index']):
                embeddings.append(item['embedding'])

            return embeddings


class DocumentChunker:
    """Chunk documents into smaller pieces for embedding"""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Chunk text into smaller pieces"""
        chunks = []
        words = text.split()

        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)

            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata["chunk_index"] = len(chunks)
            chunk_metadata["total_words"] = len(words)

            chunks.append({
                "content": chunk_text,
                "metadata": chunk_metadata
            })

        return chunks


class RAGService:
    """
    Main RAG service that combines vector store, embeddings, and retrieval
    """

    def __init__(
        self,
        vector_store_type: VectorStoreType = VectorStoreType.CHROMA,
        embedding_model: str = "text-embedding-3-large",
        **kwargs
    ):
        """
        Initialize RAG service

        Args:
            vector_store_type: Type of vector store to use
            embedding_model: Model to use for embeddings
            **kwargs: Additional arguments for vector store initialization
        """
        self.vector_store_type = vector_store_type
        self.embedding_service = EmbeddingService(model=embedding_model)
        self.chunker = DocumentChunker(chunk_size=512, chunk_overlap=50)
        self.vector_store = self._create_vector_store(**kwargs)

    def _create_vector_store(self, **kwargs) -> BaseVectorStore:
        """Create vector store based on type"""
        if self.vector_store_type == VectorStoreType.CHROMA:
            return ChromaVectorStore(**kwargs)
        elif self.vector_store_type == VectorStoreType.PINECONE:
            api_key = kwargs.get("api_key") or os.getenv("PINECONE_API_KEY")
            environment = kwargs.get("environment") or os.getenv("PINECONE_ENVIRONMENT")
            return PineconeVectorStore(
                api_key=api_key,
                environment=environment,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported vector store type: {self.vector_store_type}")

    async def ingest_documents(
        self,
        documents: List[Dict[str, Any]],
        chunk: bool = True
    ) -> int:
        """
        Ingest documents into the RAG system

        Args:
            documents: List of documents with 'content', 'title', 'source' fields
            chunk: Whether to chunk documents

        Returns:
            Number of chunks ingested
        """
        all_chunks = []

        for doc in documents:
            if chunk:
                chunks = self.chunker.chunk_text(
                    text=doc.get("content", ""),
                    metadata={
                        "title": doc.get("title", ""),
                        "source": doc.get("source", "")
                    }
                )
                all_chunks.extend(chunks)
            else:
                all_chunks.append(doc)

        # Generate embeddings
        texts = [chunk["content"] for chunk in all_chunks]
        embeddings = await self.embedding_service.embed_batch(texts)

        # Add to vector store
        metadatas = [chunk.get("metadata", {}) for chunk in all_chunks]
        ids = await self.vector_store.add_documents(
            documents=all_chunks,
            embeddings=embeddings,
            metadata=metadatas
        )

        return len(ids)

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query

        Args:
            query: Search query
            top_k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of relevant documents with scores
        """
        # Embed query
        query_embedding = await self.embedding_service.embed_text(query)

        # Search vector store
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter=filter
        )

        return results

    async def retrieve_and_format(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> str:
        """
        Retrieve and format documents as context string

        Args:
            query: Search query
            top_k: Number of results to return
            filter: Optional metadata filter

        Returns:
            Formatted context string for LLM
        """
        results = await self.retrieve(query, top_k, filter)

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Document {i}]")
            context_parts.append(f"Source: {result.get('metadata', {}).get('source', 'Unknown')}")
            context_parts.append(f"Content: {result.get('content', '')}")
            context_parts.append("")

        return "\n".join(context_parts)


# Factory function for easy creation
def create_rag_service(
    vector_store_type: str = "chroma",
    **kwargs
) -> RAGService:
    """
    Factory function to create RAG service

    Args:
        vector_store_type: Type of vector store ('chroma', 'pinecone')
        **kwargs: Additional arguments for configuration

    Returns:
        RAGService instance
    """
    store_type = VectorStoreType(vector_store_type)
    return RAGService(vector_store_type=store_type, **kwargs)
