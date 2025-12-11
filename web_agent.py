from web_crawlers import crawl_urls, crawler
from openai import AsyncOpenAI, OpenAI
import json
import os
from prompts import web_agent_ki_prompt
import asyncio


urls =  [
    "https://ukmegashop.com/",
    "https://ukmegashop.com/compare/",
    "https://ukmegashop.com/wishlist/",
    "https://ukmegashop.com/apple-shopping-event/",
    "https://ukmegashop.com/cart/",
    "https://ukmegashop.com/checkout/",
    "https://ukmegashop.com/my-account/",
    "https://ukmegashop.com/privacy-policy/",
    "https://ukmegashop.com/delivery-return-2/",
    "https://ukmegashop.com/terms-and-conditions/",
    "https://ukmegashop.com/about-us/",
    "https://ukmegashop.com/all-2/",
    "https://ukmegashop.com/faq/",
    "https://ukmegashop.com/shop/",
    "https://ukmegashop.com/new-offers/",
    "https://ukmegashop.com/promotions/",
    "https://ukmegashop.com/refund_returns/",
    "https://ukmegashop.com/support-2/"
  ]


# Global variables
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
async_openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
urls_file = './inputs/urls.json'


def define_crawl_function():
    """Define the crawl_urls function schema for OpenAI API."""
    return [{
        "type": "function",
        "function": {
            "name": "crawl_urls",
            "description": "Fetches and extracts clean text from a list of web page URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "A full URL of a page to fetch (e.g., 'https://example.com')."
                        },
                        "description": "A list of URLs to fetch."
                    }
                },
                "required": ["urls"],
                "additionalProperties": False
            },
            "strict": True
        }
    }]

async def search_nd_synthesize_async(user_query):
    functions = define_crawl_function()
    
    # Initialize messages
    messages = [
        {
            'role': 'system',
            'content': f"""
                You are an intelligent and helpful customer support chatbot for UK Mega Shop.

                You have access to a full list of website URLs: {urls}

                Whenever a user asks a question, you must:
                1. Identify which URLs from the list are most likely to contain an answer.
                2. Always include and crawl **https://ukmegashop.com/faq/** along with any other relevant URLs.
                3. Use the `crawl_urls` function to fetch and extract clean text content from those selected URLs.
                4. Use the extracted content to provide an accurate, helpful, and concise answer to the user's query.

                Important: Never skip crawling the FAQ page, even if the query seems unrelated — it may still contain useful information.

                Note: Only answer to the asked question for example 
                User question: Is the website secure?
                You answer: Yes, the website is registered as an LLC and encrypts information end-to-end for security.
                Keep short and simple.
                """
        },
        {
            'role': 'user',
            'content': user_query
        }
    ]

    # First API call to get assistant response with tool calls
    completion = await async_openai_client.chat.completions.create(
        model='gpt-4o',
        messages=messages,
        tools=functions
    )

    # Append assistant's response to messages
    messages.append(completion.choices[0].message)

    # Handle tool calls
    if completion.choices[0].message.tool_calls:
        for tool_call in completion.choices[0].message.tool_calls:
            if tool_call.function.name == 'crawl_urls':
                args = json.loads(tool_call.function.arguments)
      
                crawler_output = await (crawler(args['urls'])) #crawl_urls(args['urls'])
                messages.append(
                    {
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'content': json.dumps(crawler_output)
                    }
                )

    # Second API call to get final response
    completion2 = await async_openai_client.chat.completions.create(
        model='gpt-4o',
        messages=messages,
        tools=functions,
    )

    response = completion2.choices[0].message.content

   
    return response

