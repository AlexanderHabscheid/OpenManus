"""
Sentris RAG System - Document retrieval and web search capabilities.
"""

from .llm.provider import LLMProvider, get_llm_provider
from .rag.knowledge_base import KnowledgeBase
from .rag.processor import DocumentProcessor
from .web.search import WebSearch

__version__ = "0.1.0"


class RagSystem:
    """Main RAG system interface."""

    def __init__(self, config_path: str = None):
        """
        Initialize the RAG system.

        Args:
            config_path: Optional path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize LLM provider
        self.llm = get_llm_provider(self.config)

        # Initialize components
        self.knowledge_base = KnowledgeBase(self.config)
        self.processor = DocumentProcessor(self.config)
        self.web_search = WebSearch(self.config)

    def _load_config(self, config_path: str = None) -> dict:
        """Load configuration from file or use defaults."""
        import os
        from pathlib import Path

        import toml

        # Default configuration
        default_config = {
            "llm": {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            "embeddings": {
                "model": "sentence-transformers/all-mpnet-base-v2",
                "device": "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu",
                "batch_size": 32,
            },
            "vector_store": {
                "engine": "chromadb",
                "persist_directory": "./data/vectors",
                "collection_name": "sentris_knowledge",
                "distance_metric": "cosine",
            },
            "document_processor": {
                "chunk_size": 512,
                "chunk_overlap": 50,
                "max_chunks_per_doc": 1000,
                "supported_formats": ["pdf", "txt", "docx", "html"],
            },
            "web_search": {
                "default_engine": "duckduckgo",
                "max_results": 10,
                "cache_duration": 3600,
            },
        }

        if config_path:
            # Load and merge with defaults
            config_path = Path(config_path)
            if config_path.exists():
                with open(config_path) as f:
                    user_config = toml.load(f)

                # Deep merge configurations
                def deep_merge(d1, d2):
                    merged = d1.copy()
                    for k, v in d2.items():
                        if (
                            k in merged
                            and isinstance(merged[k], dict)
                            and isinstance(v, dict)
                        ):
                            merged[k] = deep_merge(merged[k], v)
                        else:
                            merged[k] = v
                    return merged

                return deep_merge(default_config, user_config)

        return default_config

    async def process_document(self, file_path: str) -> str:
        """
        Process a document and add to knowledge base.

        Args:
            file_path: Path to document file

        Returns:
            Document ID in knowledge base
        """
        # Process document
        chunks, metadata = await self.processor.process_file(file_path)

        # Add to knowledge base
        doc_ids = await self.knowledge_base.add_documents(chunks, metadata)

        return doc_ids[0] if doc_ids else None

    async def search(
        self, query: str, filter_criteria: dict = None, limit: int = 5
    ) -> list:
        """
        Search the knowledge base.

        Args:
            query: Search query
            filter_criteria: Optional filtering criteria
            limit: Maximum number of results

        Returns:
            List of search results
        """
        return await self.knowledge_base.search(query, filter_criteria, limit)

    async def web_search_and_process(self, query: str, max_results: int = 5) -> list:
        """
        Perform web search and process results into knowledge base.

        Args:
            query: Search query
            max_results: Maximum number of results to process

        Returns:
            List of processed document IDs
        """
        # Perform web search
        search_results = await self.web_search.search(query, max_results)

        # Process and store results
        doc_ids = []
        for result in search_results:
            chunks, metadata = await self.processor.process_text(
                result["content"],
                metadata={
                    "source": result["url"],
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "search_query": query,
                },
            )

            # Add to knowledge base
            result_ids = await self.knowledge_base.add_documents(chunks, metadata)
            if result_ids:
                doc_ids.extend(result_ids)

        return doc_ids
