"""
Sentris RAG System - Educational content generation and management.
"""

from .educational.learning_path import LearningPathGenerator
from .educational.quality import ContentQualityChecker
from .educational.quiz import AdaptiveQuizGenerator
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

        # Initialize educational components
        self.learning_path = LearningPathGenerator(self)
        self.quiz_generator = AdaptiveQuizGenerator(self)
        self.quality_checker = ContentQualityChecker(self.config)

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
            "educational": {
                "default_difficulty_levels": [
                    "beginner",
                    "intermediate",
                    "advanced",
                    "expert",
                ],
                "quiz_types": ["multiple_choice", "true_false", "short_answer"],
                "learning_styles": ["visual", "auditory", "reading", "kinesthetic"],
            },
            "quality": {
                "min_quality_score": 0.7,
                "check_plagiarism": True,
                "check_readability": True,
                "check_accuracy": True,
                "readability_target": "grade8",
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

    async def generate_materials(self, doc_id: str) -> dict:
        """
        Generate educational materials from document.

        Args:
            doc_id: Document ID in knowledge base

        Returns:
            Generated materials
        """
        # Get document content
        doc = await self.knowledge_base.get_document(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")

        # Generate materials
        materials = {
            "summary": await self._generate_summary(doc),
            "flashcards": await self._generate_flashcards(doc),
            "quiz": await self._generate_quiz(doc),
        }

        # Check quality
        quality_report = await self.quality_checker.validate_content(
            materials, "study_materials"
        )
        materials["quality_report"] = quality_report

        return materials

    async def _generate_summary(self, doc: dict) -> str:
        """Generate document summary using LLM."""
        prompt = f"""
        Generate a concise summary of the following text. Focus on key concepts and main ideas.

        Text: {doc['text']}

        Summary:
        """

        return await self.llm.generate(prompt=prompt, temperature=0.7, max_tokens=200)

    async def _generate_flashcards(self, doc: dict) -> list:
        """Generate flashcards from document using LLM."""
        prompt = f"""
        Create a set of flashcards from the following text. Each flashcard should have a front (question/term)
        and back (answer/definition). Focus on key concepts and important facts.

        Text: {doc['text']}

        Format each flashcard as:
        Front: <question/term>
        Back: <answer/definition>

        Flashcards:
        """

        response = await self.llm.generate(
            prompt=prompt, temperature=0.7, max_tokens=500
        )

        # Parse response into flashcards
        flashcards = []
        current_card = {}

        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("Front:"):
                if current_card:
                    flashcards.append(current_card)
                current_card = {"front": line[6:].strip()}
            elif line.startswith("Back:"):
                current_card["back"] = line[5:].strip()

        if current_card:
            flashcards.append(current_card)

        return flashcards

    async def _generate_quiz(self, doc: dict) -> dict:
        """Generate quiz from document."""
        return await self.quiz_generator.generate_adaptive_quiz(
            topic=doc["metadata"].get("topic", "general"),
            user_level=0.5,  # Default to intermediate
            num_questions=5,
        )
