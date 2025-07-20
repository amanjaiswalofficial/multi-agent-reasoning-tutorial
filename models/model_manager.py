import httpx

class SimpleOllamaAgent:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        
    async def generate(self, prompt: str, system: str = None) -> str:
        """Generate text using Ollama API"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            }
            
            if system:
                payload["system"] = system
                
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["response"]