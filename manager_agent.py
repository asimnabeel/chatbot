from openai import AsyncOpenAI
from prompts import prompt_for_manager_with_two_agents
import web_agent
import vectordb_agent
import asyncio
import os
import time


exe_time = {"sync_execution": [], "async_execution": []}

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def async_run(query):
    start = time.perf_counter()
    results = await asyncio.gather(
        web_agent.search_nd_synthesize_async(query),
        vectordb_agent.search_nd_synthesize_async(query)
        )
    end = time.perf_counter()
    exe_time['async_execution'].append(end - start)

    completion = await client.chat.completions.create(
        model='gpt-4.1',
        messages=[
            {
                'role': 'system',
                'content': prompt_for_manager_with_two_agents,

            },
            {
                'role': 'user',
                'content': f"Begin your task using the following inputs: Custom Web Search Agent's Answer: {results[0]}, Vector Database Agent's Answer: {results[1]}, Customer Query: {query}",
            }
        ]
    )


    return completion.choices[0].message.content


def run(query):
    return asyncio.run(async_run(query))

