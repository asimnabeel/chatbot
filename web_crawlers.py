from bs4 import BeautifulSoup
import asyncio
import httpx
import json


async def crawler(urls, separator=' '):

        
    # Headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    
    results = []

    # Create an async HTTP client
    async with httpx.AsyncClient() as client:
        # Create a list of coroutines for fetching URLs
        coroutines = [client.get(url, headers=headers, timeout=30.0, follow_redirects=True) for url in urls]
        # Execute all requests concurrently
        responses = await asyncio.gather(*coroutines, return_exceptions=True)
    
    # Process each response
    for url, response in zip(urls, responses):
        try:
            if isinstance(response, Exception):
                print(f'Failed to fetch {url}: {str(response)}')
                results.append('')
                continue
            
            # Check for successful response
            if response.status_code != 200:
                print(f'Failed to fetch {url}: HTTP {response.status_code}')
                results.append('')
                continue
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')

            # Tags to remove
            tags_to_decompose = [
                'script', 'style', 'noscript', 'meta', 'link',
                'head', 'footer', 'nav', 'header', 'aside',
                'form', 'iframe', 'template', 'svg', 'canvas',
                'object', 'embed', 'img', 'video', 'audio',
                'button', 'input', 'hr', 'br', 'map', 'area', 'base'
            ]
        
            # Remove script and style elements
            for element in soup(tags_to_decompose):
                element.decompose()
            
            # Extract text
            text = soup.get_text(separator=separator, strip=True)
            results.append(text)
        
        except Exception as e:
            results.append('')
            raise e

    return results

def crawl_urls(urls: str, sep: str = ' '):
    return asyncio.run(crawler(urls, sep))


