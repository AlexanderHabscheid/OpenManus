from setuptools import find_packages, setup

setup(
    name="sentris_rag",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pypdf2>=3.0.1",
        "langchain>=0.1.0",
        "chromadb>=0.4.15",
        "transformers>=4.36.2",
        "torch>=2.1.2",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "python-multipart>=0.0.6",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "playwright>=1.41.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ]
    },
    python_requires=">=3.9",
    author="Your Name",
    author_email="your.email@example.com",
    description="RAG system and web search capabilities for Sentris",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sentris_rag",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
