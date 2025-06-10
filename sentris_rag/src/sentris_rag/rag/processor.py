"""
Document processor for handling various file formats and chunking text.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import docx
import PyPDF2
import tiktoken
from bs4 import BeautifulSoup


class DocumentProcessor:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the document processor with configuration."""
        self.config = config
        self.chunk_size = config["document_processor"]["chunk_size"]
        self.chunk_overlap = config["document_processor"]["chunk_overlap"]
        self.max_chunks = config["document_processor"]["max_chunks_per_doc"]
        self.supported_formats = config["document_processor"]["supported_formats"]

        # Initialize tokenizer for chunk size estimation
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    async def process_file(
        self, file_path: str
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Process a file and return chunks with metadata.

        Args:
            file_path: Path to the file to process

        Returns:
            Tuple of (chunks, metadata)
        """
        file_ext = Path(file_path).suffix.lower()[1:]
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")

        # Extract text based on file type
        if file_ext == "pdf":
            text = self._extract_pdf(file_path)
        elif file_ext == "txt":
            text = self._extract_txt(file_path)
        elif file_ext == "docx":
            text = self._extract_docx(file_path)
        elif file_ext == "html":
            text = self._extract_html(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        # Generate chunks and metadata
        chunks = self._chunk_text(text)
        metadata = self._generate_metadata(chunks, file_path)

        return chunks, metadata

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return self._clean_text(text)

    def _extract_txt(self, file_path: str) -> str:
        """Extract text from plain text file."""
        with open(file_path, "r", encoding="utf-8") as file:
            return self._clean_text(file.read())

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return self._clean_text(text)

    def _extract_html(self, file_path: str) -> str:
        """Extract text from HTML file."""
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            return self._clean_text(text)

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove special characters
        text = re.sub(r"[^\w\s.,!?-]", "", text)
        # Fix spacing after punctuation
        text = re.sub(r"([.,!?])(\w)", r"\1 \2", text)
        return text.strip()

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        Uses token-based chunking for more accurate size control.
        """
        chunks = []
        tokens = self.tokenizer.encode(text)

        # Convert token counts to approximate character counts
        token_size = self.chunk_size * 4  # Approximate chars per token
        token_overlap = self.chunk_overlap * 4

        start = 0
        while start < len(tokens):
            # Get chunk tokens
            end = start + token_size
            chunk_tokens = tokens[start:end]

            # Decode chunk
            chunk = self.tokenizer.decode(chunk_tokens)

            # Adjust chunk boundaries to respect sentence boundaries
            if start > 0:
                # Find first sentence boundary
                match = re.search(r"[.!?]\s+\w", chunk)
                if match:
                    chunk = chunk[match.end() - 1 :]

            if end < len(tokens):
                # Find last sentence boundary
                match = re.search(r"[.!?]\s+\w[^.!?]*$", chunk)
                if match:
                    chunk = chunk[: match.end() - 1]

            chunks.append(chunk.strip())

            # Move start position accounting for overlap
            start = end - token_overlap

            # Check max chunks limit
            if len(chunks) >= self.max_chunks:
                break

        return chunks

    def _generate_metadata(
        self, chunks: List[str], file_path: str
    ) -> List[Dict[str, Any]]:
        """Generate metadata for chunks."""
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1][1:]

        metadata = []
        for i, chunk in enumerate(chunks):
            metadata.append(
                {
                    "source_file": file_name,
                    "file_type": file_ext,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk),
                    "token_count": len(self.tokenizer.encode(chunk)),
                }
            )

        return metadata
