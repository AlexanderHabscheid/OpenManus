"""
Web search implementation supporting multiple search engines.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup


class WebSearch:
    def __init__(self, config: Dict[str, Any]):
        """Initialize web search with configuration."""
        self.config = config
        self.default_engine = config["web_search"]["default_engine"]
        self.max_results = config["web_search"]["max_results"]
        self.cache_duration = config["web_search"]["cache_duration"]

        # Initialize cache
        self.cache = {}

    async def search(
        self,
        query: str,
        engine: Optional[str] = None,
        num_results: Optional[int] = None,
        filter_criteria: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform web search using specified engine.

        Args:
            query: Search query
            engine: Search engine to use (default from config)
            num_results: Number of results to return
            filter_criteria: Optional filtering criteria

        Returns:
            Search results with metadata
        """
        engine = engine or self.default_engine
        num_results = min(num_results or self.max_results, self.max_results)

        # Check cache
        cache_key = f"{engine}:{query}:{num_results}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        # Perform search based on engine
        if engine == "google":
            results = await self._google_search(query, num_results)
        elif engine == "duckduckgo":
            results = await self._duckduckgo_search(query, num_results)
        else:
            raise ValueError(f"Unsupported search engine: {engine}")

        # Apply filters if specified
        if filter_criteria:
            results = self._apply_filters(results, filter_criteria)

        # Cache results
        self._add_to_cache(cache_key, results)

        return results

    async def _google_search(self, query: str, num_results: int) -> Dict[str, Any]:
        """Perform Google Custom Search."""
        api_key = self.config["web_search"]["google_api_key"]
        cx = self.config["web_search"]["google_cx"]

        if not api_key or not cx:
            raise ValueError("Google API key and CX required")

        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": api_key, "cx": cx, "q": query, "num": num_results}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

                if "error" in data:
                    raise Exception(f"Google API error: {data['error']['message']}")

                results = []
                for item in data.get("items", []):
                    results.append(
                        {
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "source": "google",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

                return {
                    "results": results,
                    "total_results": data.get("searchInformation", {}).get(
                        "totalResults", 0
                    ),
                    "search_time": data.get("searchInformation", {}).get(
                        "searchTime", 0
                    ),
                }

    async def _duckduckgo_search(self, query: str, num_results: int) -> Dict[str, Any]:
        """Perform DuckDuckGo search."""
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                results = []
                for result in soup.select(".result")[:num_results]:
                    title_elem = result.select_one(".result__title")
                    snippet_elem = result.select_one(".result__snippet")
                    url_elem = result.select_one(".result__url")

                    if title_elem and url_elem:
                        results.append(
                            {
                                "title": title_elem.get_text(strip=True),
                                "url": url_elem.get("href", ""),
                                "snippet": (
                                    snippet_elem.get_text(strip=True)
                                    if snippet_elem
                                    else ""
                                ),
                                "source": "duckduckgo",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )

                return {
                    "results": results,
                    "total_results": len(results),
                    "search_time": None,  # DuckDuckGo doesn't provide this
                }

    def _apply_filters(
        self, results: Dict[str, Any], filter_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply filters to search results."""
        filtered = []

        for result in results["results"]:
            matches = True

            # Apply each filter criterion
            for key, value in filter_criteria.items():
                if key == "date_range":
                    # Filter by date if available
                    if "date" in result:
                        result_date = datetime.fromisoformat(result["date"])
                        if not (value["start"] <= result_date <= value["end"]):
                            matches = False
                            break
                elif key == "domain":
                    # Filter by domain
                    if not re.search(value, result["url"]):
                        matches = False
                        break
                elif key == "keywords":
                    # Filter by keywords in title or snippet
                    text = f"{result['title']} {result['snippet']}".lower()
                    if not all(kw.lower() in text for kw in value):
                        matches = False
                        break

            if matches:
                filtered.append(result)

        results["results"] = filtered
        results["total_results"] = len(filtered)
        return results

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get results from cache if not expired."""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.utcnow() - entry["timestamp"] < timedelta(
                seconds=self.cache_duration
            ):
                return entry["data"]
            else:
                del self.cache[key]
        return None

    def _add_to_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Add results to cache."""
        self.cache[key] = {"data": data, "timestamp": datetime.utcnow()}

        # Clean expired entries
        self._clean_cache()

    def _clean_cache(self) -> None:
        """Remove expired cache entries."""
        now = datetime.utcnow()
        expired = [
            k
            for k, v in self.cache.items()
            if now - v["timestamp"] >= timedelta(seconds=self.cache_duration)
        ]
        for key in expired:
            del self.cache[key]
