# Getting Started with OpenManus

This guide will help you get started with OpenManus, including installation, configuration, and basic usage.

## Prerequisites

Before installing OpenManus, ensure you have:
- Python 3.12 or higher
- Git
- A package manager (pip or uv)
- API keys for LLM services (e.g., OpenAI)

## Installation

### Method 1: Using conda

```bash
# Create and activate conda environment
conda create -n open_manus python=3.12
conda activate open_manus

# Clone the repository
git clone https://github.com/FoundationAgents/OpenManus.git
cd OpenManus

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/FoundationAgents/OpenManus.git
cd OpenManus

# Create and activate virtual environment
uv venv --python 3.12
source .venv/bin/activate  # On Unix/macOS
# Or on Windows:
# .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### Optional: Browser Automation Setup

If you plan to use browser automation features:

```bash
playwright install
```

## Configuration

1. Create your configuration file:

```bash
cp config/config.example.toml config/config.toml
```

2. Edit `config/config.toml` with your settings:

```toml
# Global LLM configuration
[llm]
model = "gpt-4"
base_url = "https://api.openai.com/v1"
api_key = "your-api-key"
max_tokens = 4096
temperature = 0.0

# Optional: Configure specific features
[search]
default_engine = "google"
max_results = 10

[browser]
headless = true
timeout = 30
```

## Basic Usage

### 1. Starting OpenManus

```bash
# Basic usage
python main.py

# Or for MCP tool version
python run_mcp.py

# Or for multi-agent version
python run_flow.py
```

### 2. Using Web Search

```python
# Example interaction
User: "Search for recent developments in AI"
Agent: *performs web search and provides summarized results*
```

### 3. Using Browser Automation

```python
# Example interaction
User: "Extract information from website.com"
Agent: *navigates to website and extracts relevant content*
```

### 4. Using RAG Capabilities

```python
# Example interaction
User: "Analyze this document and answer questions"
Agent: *processes document and provides context-aware responses*
```

## Common Operations

### 1. Basic Query

```bash
python main.py
> Tell me about artificial intelligence
```

### 2. Data Analysis

```bash
python main.py
> Analyze this dataset and create visualizations
```

### 3. Web Research

```bash
python main.py
> Research the latest developments in quantum computing
```

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure your API keys are correctly set in `config.toml`
   - Check API key permissions and quotas

2. **Browser Automation Issues**
   - Run `playwright install` if browser automation fails
   - Check browser dependencies are installed

3. **Search Issues**
   - Verify search API configurations
   - Check rate limiting settings

### Getting Help

- Check the [Troubleshooting Guide](./troubleshooting.md)
- Join the community on Discord
- Create an issue on GitHub

## Next Steps

After getting started, you might want to:

1. Explore [Advanced Features](./guides/advanced-features.md)
2. Learn about [Custom Agents](./guides/custom-agents.md)
3. Contribute to the project
4. Join the community

## Best Practices

1. **Configuration**
   - Keep API keys secure
   - Use environment variables for sensitive data
   - Regular configuration backups

2. **Usage**
   - Start with simple queries
   - Gradually explore advanced features
   - Monitor resource usage

3. **Development**
   - Follow coding standards
   - Write tests for custom components
   - Document your changes
