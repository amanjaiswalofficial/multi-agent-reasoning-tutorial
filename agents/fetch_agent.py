from typing import List, Optional
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup
import re

class Article(BaseModel):
    title: str
    url: str
    time: int
    content: Optional[str] = None
    word_count: int = 0
    summary: Optional[str] = None

HN_TOP = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"

async def extract_content(url: str, client: httpx.AsyncClient) -> tuple[str, int]:
    """Extract readable content from article URL"""
    try:
        response = await client.get(url, timeout=10, follow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'article', 'main', '.content', '.post-content', 
            '.entry-content', '.article-content', 'p'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([elem.get_text() for elem in elements])
                break
        
        if not content:
            content = soup.get_text()
        
        # Clean up text
        content = re.sub(r'\s+', ' ', content).strip()
        word_count = len(content.split())
        
        # Create summary if content is long
        summary = content[:500] + "..." if len(content) > 500 else content
        
        return summary, word_count
        
    except Exception as e:
        print(f"Failed to extract content from {url}: {e}")
        return "Content extraction failed", 0

async def fetch_articles(n=10) -> List[Article]:
    async with httpx.AsyncClient() as client:
        ids = (await client.get(HN_TOP)).json()[:n]
        posts = []
        for post_id in ids:
            item = (await client.get(HN_ITEM.format(post_id))).json()
            if item and "title" in item and "url" in item:
                content, word_count = await extract_content(item["url"], client)
                article_data = {
                    **item,
                    "content": content,
                    "word_count": word_count,
                    "summary": content[:200] + "..." if len(content) > 200 else content
                }
                posts.append(Article.model_validate(article_data))
        return posts
