import logging

import aiohttp
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults


logger = logging.getLogger("ai")

async def fetch_page_text(url: str) -> str:
    """Safely fetches and cleans a webpage."""
    
    try:
        logger.info("Fetching page: {}".format(url))
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, 
                timeout=8, 
                headers={
                    "User-Agent": "Mozilla/5.0",
                },
                auto_decompress=True
            ) as response:
                response.raise_for_status()
                soup = BeautifulSoup(await response.text(), "html.parser")

                # Remove scripts + styles
                for tag in soup(["script", "style", "noscript"]):
                    tag.extract()

                text = soup.get_text(separator=" ")
                return " ".join(text.split())
    except Exception as e:
        logger.info("Failed to fetch: {}".format(url))
        return ""



@tool("market_research_tool", return_direct=False)
async def market_research_tool(query: str) -> dict:
    """
    Real-time market analysis tool using DuckDuckGo + scraping.
    Input: user query (e.g., 'gamified recycling education apps market size')
    
    Returns:
        {
          "query": "...",
          "results": [ { "title", "url", "content" }, ... ]
        }
    """
    logger.info("Start marketing research tools")

    # ddg = DDGS()
    search = DuckDuckGoSearchResults(output_format="list")

    search_results = await search.ainvoke(query, max_results=5)
    logger.info("Searched result: {}".format(search_results))
    cleaned_results = []
    

    for result in search_results:
        url = result.get("link")
        title = result.get("title", "No Title")

        if not url:
            continue

        content = await fetch_page_text(url)

        cleaned_results.append({
            "title": title,
            "url": url,
            "content": content[:3000],
        })

    return {
        "query": query,
        "results": cleaned_results
    }