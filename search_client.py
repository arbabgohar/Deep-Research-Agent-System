
import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import re

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

try:
    import requests
except ImportError:
    requests = None

class SearchClient:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("search_client")
        
        self.provider = config.get("search_provider", "tavily").lower()
        self.max_results = config.get("max_results", 10)
        
        self._initialize_clients()
        
    def _initialize_clients(self):
        
        if self.provider == "tavily":
            if TavilyClient is None:
                raise ImportError("Tavily library not installed. Run: pip install tavily-python")
            
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                raise ValueError("TAVILY_API_KEY environment variable not set")
            
            self.client = TavilyClient(api_key=api_key)
            
        elif self.provider == "duckduckgo":
            if DDGS is None:
                raise ImportError("DuckDuckGo Search library not installed. Run: pip install duckduckgo-search")
            
            self.client = DDGS()
            
        else:
            raise ValueError(f"Unsupported search provider: {self.provider}")
    
    async def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        
        max_results = max_results or self.max_results
        
        try:
            if self.provider == "tavily":
                return await self._search_tavily(query, max_results)
            elif self.provider == "duckduckgo":
                return await self._search_duckduckgo(query, max_results)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            return self._get_fallback_results(query)
    
    async def _search_tavily(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        
        response = await asyncio.to_thread(
            self.client.search,
            query=query,
            search_depth="basic",
            max_results=max_results
        )
        
        results = []
        for result in response.get("results", []):
            processed_result = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("content", ""),
                "domain": self._extract_domain(result.get("url", "")),
                "published_date": result.get("published_date"),
                "score": result.get("score", 0.0)
            }
            results.append(processed_result)
        
        return results
    
    async def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        
        results = []
        
        try:
            search_results = await asyncio.to_thread(
                lambda: list(self.client.text(query, max_results=max_results))
            )
            
            for result in search_results:
                processed_result = {
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("body", ""),
                    "domain": self._extract_domain(result.get("link", "")),
                    "published_date": None,
                    "score": 0.5
                }
                results.append(processed_result)
                
        except Exception as e:
            self.logger.warning(f"DuckDuckGo search failed: {str(e)}")
        
        return results
    
    def _extract_domain(self, url: str) -> str:
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if domain.startswith("www."):
                domain = domain[4:]
            
            return domain
        except:
            return "unknown"
    
    def _get_fallback_results(self, query: str) -> List[Dict[str, Any]]:
        
        return [
            {
                "title": f"Search results for: {query}",
                "url": "https://example.com/fallback",
                "snippet": f"Search results for '{query}' are currently unavailable. Please try again later.",
                "domain": "example.com",
                "published_date": None,
                "score": 0.0
            }
        ]
    
    async def search_with_filters(
        self, 
        query: str, 
        filters: Dict[str, Any],
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        
        results = await self.search(query, max_results)
        
        filtered_results = []
        
        for result in results:
            if self._apply_filters(result, filters):
                filtered_results.append(result)
        
        return filtered_results
    
    def _apply_filters(self, result: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        
        if "domain" in filters:
            allowed_domains = filters["domain"]
            if isinstance(allowed_domains, str):
                allowed_domains = [allowed_domains]
            
            if result.get("domain") not in allowed_domains:
                return False
        
        if "date_range" in filters:
            pass
        
        if "content_keywords" in filters:
            keywords = filters["content_keywords"]
            if isinstance(keywords, str):
                keywords = [keywords]
            
            content = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
            if not any(keyword.lower() in content for keyword in keywords):
                return False
        
        return True
    
    async def get_source_content(self, url: str) -> Optional[str]:
        
        if requests is None:
            self.logger.warning("Requests library not available for content fetching")
            return None
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = await asyncio.to_thread(
                requests.get,
                url,
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            
            content = response.text
            
            content = re.sub(r'<[^>]+>', '', content)
            
            content = re.sub(r'\s+', ' ', content).strip()
            
            return content[:5000]
            
        except Exception as e:
            self.logger.error(f"Failed to fetch content from {url}: {str(e)}")
            return None
    
    async def search_multiple_queries(self, queries: List[str], max_results_per_query: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        
        max_results_per_query = max_results_per_query or self.max_results
        
        tasks = [
            self.search(query, max_results_per_query) 
            for query in queries
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        search_results = {}
        for i, result in enumerate(results):
            query = queries[i]
            
            if isinstance(result, Exception):
                self.logger.error(f"Search failed for query '{query}': {str(result)}")
                search_results[query] = self._get_fallback_results(query)
            else:
                search_results[query] = result
        
        return search_results
    
    def get_source_quality_score(self, result: Dict[str, Any]) -> float:
        
        score = 0.0
        
        domain = result.get("domain", "").lower()
        if any(high_quality in domain for high_quality in [".edu", ".gov", ".org"]):
            score += 0.3
        elif any(medium_quality in domain for medium_quality in ["wikipedia.org", "reuters.com", "bbc.com"]):
            score += 0.2
        
        snippet_length = len(result.get("snippet", ""))
        if snippet_length > 200:
            score += 0.2
        elif snippet_length > 100:
            score += 0.1
        
        title = result.get("title", "").lower()
        if title and len(title) > 10:
            score += 0.1
        
        url = result.get("url", "")
        if url and "http" in url:
            score += 0.1
        
        if result.get("published_date"):
            score += 0.1
        
        provider_score = result.get("score", 0.0)
        score += provider_score * 0.2
        
        return min(1.0, score)
    
    def get_available_providers(self) -> List[str]:
        
        providers = []
        
        if TavilyClient is not None:
            providers.append("tavily")
        
        if DDGS is not None:
            providers.append("duckduckgo")
        
        return providers
    
    def get_provider_info(self) -> Dict[str, Any]:
        
        return {
            "provider": self.provider,
            "max_results": self.max_results,
            "available_providers": self.get_available_providers()
        }

async def test_search_client():
    
    config = {
        "search_provider": "tavily",
        "max_results": 5
    }
    
    try:
        client = SearchClient(config)
        
        results = await client.search("electric car benefits")
        print(f"Search results: {len(results)} found")
        
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Domain: {result['domain']}")
            print(f"   Quality Score: {client.get_source_quality_score(result):.2f}")
            print()
        
        filters = {
            "domain": ["wikipedia.org", "edu"],
            "content_keywords": ["electric", "car"]
        }
        
        filtered_results = await client.search_with_filters("electric vehicles", filters)
        print(f"Filtered results: {len(filtered_results)} found")
        
        queries = ["electric cars", "renewable energy", "climate change"]
        multi_results = await client.search_multiple_queries(queries, max_results_per_query=3)
        
        for query, results in multi_results.items():
            print(f"'{query}': {len(results)} results")
        
        provider_info = client.get_provider_info()
        print(f"Provider info: {provider_info}")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        print("Make sure you have the required API keys set in environment variables")

if __name__ == "__main__":
    asyncio.run(test_search_client())
