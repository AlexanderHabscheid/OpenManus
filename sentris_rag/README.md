# Sentris RAG

A focused RAG (Retrieval-Augmented Generation) system adapted from OpenManus, providing powerful document processing and web search capabilities.

## Features

- **Advanced RAG System**
  - ChromaDB-based vector storage
  - Multi-format document processing (PDF, TXT, DOCX, HTML)
  - Token-based text chunking with overlap
  - Efficient document retrieval

- **Web Search Integration**
  - DuckDuckGo and Google support
  - Automatic content extraction
  - Result caching
  - Search result processing into knowledge base

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
git clone https://github.com/AlexanderHabscheid/OpenManus.git
cd OpenManus
git checkout sentris_rag_component
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

# Search the knowledge base
results = await rag.search("your query")

# Perform web search and add to knowledge base
doc_ids = await rag.web_search_and_process("your query")
```

## Configuration

The system is highly configurable through a TOML configuration file. Key configuration sections include:

- `llm`: LLM provider settings (DeepSeek/OpenAI)
- `embeddings`: Embedding model configuration
- `vector_store`: Vector database settings
- `document_processor`: Document processing parameters
- `web_search`: Web search configuration

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
