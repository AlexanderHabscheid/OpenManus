# Sentris RAG

A powerful educational RAG (Retrieval-Augmented Generation) system designed for integration with the Sentris platform. This package provides advanced document processing, knowledge management, and educational content generation capabilities.

## Features

- **Advanced RAG System**
  - ChromaDB-based vector storage
  - Multi-format document processing (PDF, TXT, DOCX, HTML)
  - Web search integration (Google, DuckDuckGo)
  - Token-based text chunking with overlap

- **Educational Features**
  - Learning path generation
  - Adaptive quiz system
  - Content quality checking
  - Progress tracking
  - Multiple learning style support

- **LLM Integration**
  - DeepSeek API support (default)
  - OpenAI API support (optional)
  - Configurable models and parameters

## Installation

```bash
pip install sentris_rag
```

For development installation:

```bash
git clone https://github.com/sentris/sentris_rag.git
cd sentris_rag
pip install -e ".[dev]"
```

## Quick Start

1. Create a configuration file:

```bash
cp config/config.example.toml config.toml
```

2. Update the configuration with your API keys and preferences.

3. Basic usage:

```python
from sentris_rag import RagSystem

# Initialize the system
rag = RagSystem("path/to/config.toml")

# Process a document
doc_id = await rag.process_document("path/to/document.pdf")

# Generate educational materials
materials = await rag.generate_materials(doc_id)

# Access different components
summary = materials["summary"]
flashcards = materials["flashcards"]
quiz = materials["quiz"]
```

## Configuration

The system is highly configurable through a TOML configuration file. Key configuration sections include:

- `llm`: LLM provider settings (DeepSeek/OpenAI)
- `embeddings`: Embedding model configuration
- `vector_store`: Vector database settings
- `document_processor`: Document processing parameters
- `web_search`: Web search configuration
- `educational`: Educational feature settings
- `quality`: Content quality parameters

See `config.example.toml` for a complete configuration reference.

## Development

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Run tests:
```bash
pytest tests/
```

3. Format code:
```bash
black src/ tests/
isort src/ tests/
```

4. Type checking:
```bash
mypy src/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
