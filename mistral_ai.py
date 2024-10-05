import aiohttp

class Mistral:
    def __init__(self, api_key: str, server_url: str):
        self.api_key = api_key
        self.server_url = server_url
        self.endpoint = f"{self.server_url}/v1/chat/completions"  # Updated endpoint for chat completions

    async def send_request(self, prompt: str) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "model": "Mistral-large-2407",  # Specify your model name here
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 1.0,
            "max_tokens": 1000,
            "top_p": 1.0
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.endpoint, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"GitHub API Error: {error_data.get('message', 'Unknown error')}")
                response_data = await response.json()
                return response_data

    async def __call__(self, prompt: str) -> str:
        response = await self.send_request(prompt)
        if "error" in response:
            raise Exception(response["error"]["message"])
        return response["choices"][0]["message"]["content"]