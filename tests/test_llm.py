import asyncio
from agents.mistralllm import MistralLLM 

async def test_llm():
    llm = MistralLLM.from_env()
    response = await llm._call("What is the capital of France?")
    print(response)

if __name__ == "__main__":
    asyncio.run(test_llm())