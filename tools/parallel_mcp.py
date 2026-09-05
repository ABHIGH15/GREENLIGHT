import os
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger("greenlight.tools.parallel")

# Parallel Search MCP Endpoint
PARALLEL_MCP_URL = "https://search-mcp.parallel.ai/mcp"


def create_parallel_toolset():
    """Creates a shared Parallel MCP toolset for Google ADK clearance agents.
    
    The hosted endpoint https://search-mcp.parallel.ai/mcp requires zero authentication
    for the search MCP by default. If a PARALLEL_API_KEY is provided, it is included
    as a Bearer token to lift anonymous rate limits.
    """
    try:
        try:
            from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
        except ImportError:
            from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
        
        headers: Dict[str, str] = {}
        api_key = os.environ.get("PARALLEL_API_KEY", "").strip()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            logger.info("Configured Parallel MCP with Bearer token authentication.")
        else:
            logger.info("Configured Parallel MCP with zero-auth default endpoint.")
            
        toolset = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=PARALLEL_MCP_URL,
                headers=headers
            ),
            tool_filter=["web_search", "web_fetch"]
        )
        return toolset
    except ImportError as e:
        logger.warning(f"ADK MCPToolset import failed ({e}); fallback direct tools will be used.")
        return None


# Standalone Direct Parallel Search Client for custom ADK tool calls or fallback
class DirectParallelSearcher:
    """Direct Parallel Search API client using httpx or parallel-web SDK."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("PARALLEL_API_KEY", "").strip()
        self.endpoint = "https://api.parallel.ai/v1/search"
        self.mcp_url = PARALLEL_MCP_URL

    async def search(self, objective: str, search_queries: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """Executes a search via Parallel and returns ranked excerpts with URLs."""
        import httpx
        
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        payload = {
            "objective": objective,
            "search_queries": search_queries[:4],
            "mode": "fast",
            "max_results": max_results
        }
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(self.endpoint, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    return [
                        {
                            "title": r.get("title", "Untitled Source"),
                            "url": r.get("url", ""),
                            "excerpts": r.get("excerpts", []),
                            "publish_date": r.get("publish_date", "")
                        }
                        for r in results
                    ]
                else:
                    logger.warning(f"Parallel search returned HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"Error querying Parallel API: {e}")
            
        return []
