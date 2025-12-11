import os
from pinecone import Pinecone, PineconeAsyncio
from openai import OpenAI, AsyncOpenAI
import asyncio

pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
async_openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

index = pinecone_client.Index("ukmegashop-final")


def generate_embeddigns(text):
    response = openai_client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding
    return embedding

def retrieve_context(query):
        query_embeddings = generate_embeddigns(query)
        result = index.query(
            vector=query_embeddings,
            top_k=3,
            include_metadata=True
        )
        return result.to_str()


async def search_nd_synthesize_async(query):
    completion = await async_openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
             {
                  "role": "system",
                  "content": "You are a customer support agent at UK Mega Shop (ukmegashop.com). Answer to the customer quries using the retrieved context"
             },
             {
                'role': 'user',
                'content': f"Customer Query: {query} + Retrieved Context: {retrieve_context(query)}."
             }
        ]
    )

    return completion.choices[0].message.content