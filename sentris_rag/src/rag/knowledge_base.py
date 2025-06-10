"""
Knowledge base implementation for the Sentris RAG system.
Handles vector storage and retrieval of document chunks.
"""

import logging
from typing import Dict, List, Optional, Union

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Manages the vector store and retrieval of document information."""

    def __init__(self, config: Dict):
        """
        Initialize the knowledge base.

        Args:
            config: Configuration dictionary containing knowledge base settings
        """
        self.config = config

        # Initialize ChromaDB client
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=config.get("persist_directory", "./data/chroma"),
                anonymized_telemetry=False,
            )
        )

        # Set up embedding function
        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=config.get(
                    "embedding_model", "sentence-transformers/all-mpnet-base-v2"
                )
            )
        )

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=config.get("collection_name", "sentris_docs"),
            embedding_function=self.embedding_function,
        )

    def add_document(self, doc_id: str, processed_doc: Dict) -> None:
        """
        Add a processed document to the knowledge base.

        Args:
            doc_id: Unique identifier for the document
            processed_doc: Processed document information
        """
        try:
            chunks = processed_doc["chunks"]
            metadata = processed_doc["metadata"]
            structure = processed_doc["structure"]

            # Prepare chunks for storage
            chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            chunk_metadata = []

            for i, chunk in enumerate(chunks):
                chunk_meta = {
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "source": metadata.get("title", ""),
                    "author": metadata.get("author", ""),
                }

                # Add structural information if available
                if structure and "chapters" in structure:
                    chunk_meta["chapter"] = self._find_chunk_chapter(
                        chunk, structure["chapters"]
                    )

                chunk_metadata.append(chunk_meta)

            # Add to collection
            self.collection.add(
                ids=chunk_ids, documents=chunks, metadatas=chunk_metadata
            )

            logger.info(
                f"Successfully added document {doc_id} with {len(chunks)} chunks"
            )

        except Exception as e:
            logger.error(f"Error adding document {doc_id} to knowledge base: {str(e)}")
            raise

    def query(
        self, query: str, n_results: int = 5, filters: Optional[Dict] = None
    ) -> Dict:
        """
        Query the knowledge base.

        Args:
            query: Query string
            n_results: Number of results to return
            filters: Optional filters to apply to the query

        Returns:
            Dict containing query results
        """
        try:
            results = self.collection.query(
                query_texts=[query], n_results=n_results, where=filters
            )

            # Process and format results
            processed_results = []
            for i, (doc, metadata, distance) in enumerate(
                zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ):
                processed_results.append(
                    {
                        "content": doc,
                        "metadata": metadata,
                        "relevance_score": 1
                        - distance,  # Convert distance to similarity score
                        "rank": i + 1,
                    }
                )

            return {
                "query": query,
                "results": processed_results,
                "total_found": len(processed_results),
            }

        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            raise

    def get_document_chunks(self, doc_id: str) -> List[Dict]:
        """
        Retrieve all chunks for a specific document.

        Args:
            doc_id: Document identifier

        Returns:
            List of document chunks with metadata
        """
        try:
            results = self.collection.get(where={"doc_id": doc_id})

            chunks = []
            for doc, metadata in zip(results["documents"], results["metadatas"]):
                chunks.append({"content": doc, "metadata": metadata})

            return chunks

        except Exception as e:
            logger.error(f"Error retrieving chunks for document {doc_id}: {str(e)}")
            raise

    def _find_chunk_chapter(self, chunk: str, chapters: List[Dict]) -> Optional[str]:
        """
        Find which chapter a chunk belongs to.

        Args:
            chunk: Text chunk
            chapters: List of chapter information

        Returns:
            Chapter identifier or None if not found
        """
        # Implementation of chapter assignment logic
        # This is a placeholder - you should implement proper chapter assignment
        return None

    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document and its chunks from the knowledge base.

        Args:
            doc_id: Document identifier
        """
        try:
            self.collection.delete(where={"doc_id": doc_id})
            logger.info(f"Successfully deleted document {doc_id}")

        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            raise

    def get_statistics(self) -> Dict:
        """
        Get statistics about the knowledge base.

        Returns:
            Dict containing knowledge base statistics
        """
        try:
            return {
                "total_chunks": self.collection.count(),
                "documents": len(
                    set(m["doc_id"] for m in self.collection.get()["metadatas"])
                ),
                "collection_name": self.collection.name,
            }
        except Exception as e:
            logger.error(f"Error getting knowledge base statistics: {str(e)}")
            raise
