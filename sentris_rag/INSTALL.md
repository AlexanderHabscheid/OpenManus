# Installing Sentris RAG Package

## Quick Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sentris_rag.git
cd sentris_rag

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Install optional dependencies
pip install -e ".[dev]"  # For development tools
```

## Package Structure

```
sentris_rag/
├── src/
│   ├── rag/
│   │   ├── processor.py        # Document processing
│   │   ├── knowledge_base.py   # Vector store
│   │   ├── generator.py        # Content generation
│   │   └── educational.py      # Educational features
│   ├── web/
│   │   ├── search.py          # Web search
│   │   └── browser.py         # Browser automation
│   └── utils/
│       └── helpers.py         # Utility functions
├── config/
│   └── config.example.toml    # Configuration template
├── docs/
│   ├── rag_system.md         # RAG documentation
│   ├── web_search.md         # Search documentation
│   └── integration.md        # Integration guide
└── examples/
    ├── basic_usage.py        # Basic examples
    └── educational.py        # Educational features
```

## Configuration

1. Copy the example configuration:
```bash
cp config/config.example.toml config/config.toml
```

2. Edit `config.toml` with your settings:
```toml
[llm]
model = "gpt-4"
api_key = "your-api-key"

[vector_store]
engine = "chromadb"
persist_directory = "./data/vectors"

[web_search]
engine = "duckduckgo"  # or "google"
api_key = "your-api-key"  # if using Google
```

## Integration with Sentris

1. Add the package to your Sentris project:
```bash
cd your-sentris-project
pip install -e path/to/sentris_rag
```

2. Import and use in your code:
```python
from sentris_rag import RagSystem, WebSearch
from sentris_rag.educational import LearningPathGenerator

# Initialize components
rag = RagSystem()
web = WebSearch()
path_gen = LearningPathGenerator(rag)

# Use in your application
results = await rag.process_document("your_document.pdf")
```

## Troubleshooting

Common issues and solutions:

1. **Vector Store Issues**
   - Ensure ChromaDB is properly installed
   - Check persistence directory permissions
   - Verify embedding model installation

2. **API Connection Issues**
   - Verify API keys in config.toml
   - Check network connectivity
   - Confirm rate limits

3. **Integration Issues**
   - Check Python version compatibility
   - Verify all dependencies are installed
   - Ensure paths are correctly configured

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Contact the maintainers
