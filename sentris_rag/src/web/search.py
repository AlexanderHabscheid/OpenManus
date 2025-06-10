"""
Web search implementation for the Sentris RAG system.
Provides multi-engine search capabilities and content extraction.
"""

import json
import logging
import time
import urllib.parse
from typing import Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebSearch:
    """Handles web search operations across multiple search engines."""

    def __init__(self, config: Dict):
        """
        Initialize the web search system.

        Args:
            config: Configuration dictionary containing search settings
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

        # Configure search engines
        self.search_engines = {
            "google": self._search_google,
            "duckduckgo": self._search_duckduckgo,
            "custom": self._search_custom,
        }

        self.default_engine = config.get("default_engine", "duckduckgo")
        self.max_results = config.get("max_results", 10)
        self.rate_limit = config.get("rate_limit", 1.0)  # seconds between requests
        self.last_request = 0

    def search(
        self,
        query: str,
        engine: Optional[str] = None,
        num_results: Optional[int] = None,
    ) -> Dict:
        """
        Perform a web search.

        Args:
            query: Search query
            engine: Search engine to use (default: configured default_engine)
            num_results: Number of results to return (default: configured max_results)

        Returns:
            Dict containing search results
        """
        try:
            engine = engine or self.default_engine
            num_results = min(num_results or self.max_results, self.max_results)

            if engine not in self.search_engines:
                raise ValueError(f"Unsupported search engine: {engine}")

            # Rate limiting
            self._respect_rate_limit()

            # Perform search
            results = self.search_engines[engine](query, num_results)

            # Extract content from results
            enriched_results = self._enrich_results(results)

            return {
                "query": query,
                "engine": engine,
                "results": enriched_results,
                "total_found": len(enriched_results),
            }

        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            raise

    def _search_google(self, query: str, num_results: int) -> List[Dict]:
        """
        Perform a Google search.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of search results
        """
        if "google_api_key" not in self.config:
            raise ValueError("Google API key not configured")

        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.config["google_api_key"],
                "cx": self.config["google_cx"],
                "q": query,
                "num": num_results,
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("items", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "google",
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Error in Google search: {str(e)}")
            return []

    def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict]:
        """
        Perform a DuckDuckGo search.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of search results
        """
        try:
            url = "https://api.duckduckgo.com/"
            params = {"q": query, "format": "json", "no_html": 1, "no_redirect": 1}

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            results = []
            for result in data.get("Results", [])[:num_results]:
                results.append(
                    {
                        "title": result.get("Title", ""),
                        "url": result.get("FirstURL", ""),
                        "snippet": result.get("Text", ""),
                        "source": "duckduckgo",
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Error in DuckDuckGo search: {str(e)}")
            return []

    def _search_custom(self, query: str, num_results: int) -> List[Dict]:
        """
        Perform a search using a custom search engine.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of search results
        """
        if "custom_search_url" not in self.config:
            raise ValueError("Custom search URL not configured")

        try:
            url = self.config["custom_search_url"]
            params = {
                "q": query,
                "num": num_results,
                "api_key": self.config.get("custom_search_api_key", ""),
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Process according to custom search engine response format
            results = []
            for item in data.get("results", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "custom",
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Error in custom search: {str(e)}")
            return []

    def _enrich_results(self, results: List[Dict]) -> List[Dict]:
        """
        Enrich search results with additional content.

        Args:
            results: List of search results

        Returns:
            List of enriched search results
        """
        enriched = []
        for result in results:
            try:
                # Extract main content from URL
                content = self._extract_content(result["url"])

                enriched.append(
                    {**result, "content": content, "extracted_at": time.time()}
                )

            except Exception as e:
                logger.warning(f"Error enriching result {result['url']}: {str(e)}")
                enriched.append(result)

            self._respect_rate_limit()

        return enriched

    def _extract_content(self, url: str) -> str:
        """
        Extract main content from a webpage.

        Args:
            url: URL to extract content from

        Returns:
            Extracted content as string
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            # Extract text content
            text = soup.get_text(separator="\n", strip=True)

            # Basic text cleaning
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(lines)

            return text

        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return ""

    def _respect_rate_limit(self) -> None:
        """Ensure rate limiting between requests."""
        now = time.time()
        if now - self.last_request < self.rate_limit:
            time.sleep(self.rate_limit - (now - self.last_request))
        self.last_request = time.time()
