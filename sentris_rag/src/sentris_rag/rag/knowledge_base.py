"""
Knowledge base implementation using ChromaDB for vector storage and retrieval.
"""

import os
from typing import Any, Dict, List, Optional

import chromadb
import numpy as np
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class KnowledgeBase:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the knowledge base with configuration."""
        self.config = config

        # Initialize ChromaDB
        persist_dir = config["vector_store"]["persist_directory"]
        os.makedirs(persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_dir, settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=config["vector_store"]["collection_name"],
            metadata={"hnsw:space": config["vector_store"]["distance_metric"]},
        )

        # Initialize embedding model
        self.embedder = SentenceTransformer(
            config["embeddings"]["model"], device=config["embeddings"]["device"]
        )
        self.batch_size = config["embeddings"]["batch_size"]

    async def add_documents(
        self,
        texts: List[str],
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to the knowledge base.

        Args:
            texts: List of text chunks to add
            metadata: List of metadata dicts for each chunk
            ids: Optional list of IDs for the chunks

        Returns:
            List of assigned document IDs
        """
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(texts))]

        # Generate embeddings in batches
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_embeddings = self.embedder.encode(
                batch, convert_to_tensor=True, show_progress_bar=False
            )
            embeddings.extend(batch_embeddings.tolist())

        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings, documents=texts, metadatas=metadata, ids=ids
        )

        return ids

    async def search(
        self,
        query: str,
        filter_criteria: Optional[Dict[str, Any]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant documents.

        Args:
            query: Search query text
            filter_criteria: Optional metadata filters
            limit: Maximum number of results

        Returns:
            List of results with text and metadata
        """
        # Generate query embedding
        query_embedding = self.embedder.encode(
            query, convert_to_tensor=True, show_progress_bar=False
        ).tolist()

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=limit, where=filter_criteria
        )

        # Format results
        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append(
                {
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "id": results["ids"][0][i],
                    "distance": results["distances"][0][i],
                }
            )

        return formatted_results

    async def update_document(
        self, doc_id: str, text: str, metadata: Dict[str, Any]
    ) -> None:
        """
        Update an existing document in the knowledge base.

        Args:
            doc_id: ID of document to update
            text: New text content
            metadata: New metadata
        """
        # Generate new embedding
        embedding = self.embedder.encode(
            text, convert_to_tensor=True, show_progress_bar=False
        ).tolist()

        # Update in ChromaDB
        self.collection.update(
            ids=[doc_id], embeddings=[embedding], documents=[text], metadatas=[metadata]
        )

    async def delete_documents(self, doc_ids: List[str]) -> None:
        """
        Delete documents from the knowledge base.

        Args:
            doc_ids: List of document IDs to delete
        """
        self.collection.delete(ids=doc_ids)

    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by ID.

        Args:
            doc_id: Document ID to retrieve

        Returns:
            Document data if found, None otherwise
        """
        results = self.collection.get(
            ids=[doc_id], include=["documents", "metadatas", "embeddings"]
        )

        if not results["documents"]:
            return None

        return {
            "text": results["documents"][0],
            "metadata": results["metadatas"][0],
            "embedding": results["embeddings"][0],
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        return {
            "total_documents": self.collection.count(),
            "embedding_dim": len(self.embedder.encode("test")),
            "distance_metric": self.config["vector_store"]["distance_metric"],
        }
