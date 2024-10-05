from mistralai import Mistral
import os
from ..agents.mistralllm import SystemMessage, UserMessage  # Updated import from mistralllm
import asyncio

async def test_api():
    llm = Mistral(
        api_key=os.environ["GITHUB_TOKEN"],  # Use environment variable for security
        server_url="https://models.inference.ai.azure.com"  # Set to your server URL
    )
    response = await llm("What is the capital of France?")
    print(response)

async def test_chat_complete():
    llm = Mistral(
        api_key=os.environ["GITHUB_TOKEN"],  # Use environment variable for security
        server_url="https://models.inference.ai.azure.com"  # Set to your server URL
    )
    response = await llm.chat.complete(
        model="Mistral-large-2407",  # Specify your model name
        messages=[
            SystemMessage(content="You are a helpful assistant."),
            UserMessage(content="What is the capital of France?"),
        ],
        temperature=1.0,
        max_tokens=1000,
        top_p=1.0
    )
    print(response["choices"][0]["message"]["content"])

asyncio.run(test_api())
asyncio.run(test_chat_complete())

def test_mistral_request():
    mistral = Mistral(
        api_key="test_github_token",  # Use a test GitHub token
        server_url="https://models.inference.ai.azure.com"
    )
    response = asyncio.run(mistral("Test prompt for API connectivity."))
    assert "Paris" in response  # Replace with expected output based on your model's response