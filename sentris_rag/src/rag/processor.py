"""
Document processor for the Sentris RAG system.
Handles PDF processing, text extraction, and chunking.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf2 import PdfReader

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document processing, including PDF parsing and text chunking."""

    def __init__(self, config: Dict):
        """
        Initialize the document processor.

        Args:
            config: Configuration dictionary containing processing settings
        """
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.get("chunk_size", 1000),
            chunk_overlap=config.get("chunk_overlap", 200),
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        )

    def process_document(self, file_path: Union[str, Path]) -> Dict:
        """
        Process a document and return its processed content.

        Args:
            file_path: Path to the document file

        Returns:
            Dict containing processed document information
        """
        try:
            file_path = Path(file_path)
            if file_path.suffix.lower() != ".pdf":
                raise ValueError(f"Unsupported file type: {file_path.suffix}")

            return self._process_pdf(file_path)
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise

    def _process_pdf(self, pdf_path: Path) -> Dict:
        """
        Process a PDF document.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dict containing processed PDF information
        """
        reader = PdfReader(str(pdf_path))

        # Extract text and metadata
        text = ""
        page_texts = []
        for page in reader.pages:
            page_text = page.extract_text()
            text += page_text
            page_texts.append(page_text)

        # Extract document structure
        structure = self._extract_structure(text, page_texts)

        # Create chunks
        chunks = self.text_splitter.split_text(text)

        # Extract metadata
        metadata = self._extract_metadata(reader)

        return {
            "chunks": chunks,
            "structure": structure,
            "metadata": metadata,
            "statistics": {
                "num_pages": len(reader.pages),
                "num_chunks": len(chunks),
                "total_length": len(text),
            },
        }

    def _extract_structure(self, text: str, page_texts: List[str]) -> Dict:
        """
        Extract document structure (chapters, sections, etc.).

        Args:
            text: Full document text
            page_texts: List of text content for each page

        Returns:
            Dict containing document structure information
        """
        structure = {
            "chapters": self._identify_chapters(text),
            "sections": self._identify_sections(text),
            "page_breaks": [len(pt) for pt in page_texts],
        }

        return structure

    def _identify_chapters(self, text: str) -> List[Dict]:
        """
        Identify chapters in the document.

        Args:
            text: Document text

        Returns:
            List of chapter information
        """
        # Simple chapter detection based on common patterns
        chapter_patterns = [
            r"Chapter \d+",
            r"CHAPTER \d+",
            r"\d+\.\s+[A-Z]",
        ]

        chapters = []
        # Implementation of chapter detection logic
        # This is a placeholder - you should implement proper chapter detection

        return chapters

    def _identify_sections(self, text: str) -> List[Dict]:
        """
        Identify sections in the document.

        Args:
            text: Document text

        Returns:
            List of section information
        """
        # Simple section detection
        sections = []
        # Implementation of section detection logic
        # This is a placeholder - you should implement proper section detection

        return sections

    def _extract_metadata(self, reader: PdfReader) -> Dict:
        """
        Extract metadata from the PDF document.

        Args:
            reader: PdfReader instance

        Returns:
            Dict containing document metadata
        """
        metadata = {}

        try:
            if reader.metadata:
                metadata = {
                    "title": reader.metadata.get("/Title", ""),
                    "author": reader.metadata.get("/Author", ""),
                    "subject": reader.metadata.get("/Subject", ""),
                    "keywords": reader.metadata.get("/Keywords", ""),
                    "creator": reader.metadata.get("/Creator", ""),
                    "producer": reader.metadata.get("/Producer", ""),
                    "creation_date": reader.metadata.get("/CreationDate", ""),
                    "modification_date": reader.metadata.get("/ModDate", ""),
                }
        except Exception as e:
            logger.warning(f"Error extracting metadata: {str(e)}")

        return metadata
