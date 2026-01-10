import openai
from typing import List, Dict, Any, Optional, AsyncGenerator
import tiktoken
from domain.services.ai_service import IAIService
from infrastructure.config.environment import config

class OpenAiService(IAIService):
    def __init__(self):
        self.client=openai.AsyncOpenAI(api_key=config["openai"]["api_key"])
        self.model=config["openai"]["model"]
        self.embedding_model = config["openai"]["embedding_model"]

    
    async def generate_chat_completion(
            self, 
            messages, 
            system_prompt = None, 
            temperature = 0.7, 
            max_tokens = None, 
            stream = False
        ) -> str | AsyncGenerator[str, None]:

        formatted_messages = []

        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })

        formatted_messages.extend(messages)

        if stream:
            return self._handle_streaming(
                formatted_messages, temperature, max_tokens
            )
        else:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
    async def _handle_streaming(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def generate_embeedings(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.embeddings.create(
            model=self.embedding_model,
            inputs=texts
        )

        return [embedding.embedding for embedding in response.data]
        

    def count_tokens(self, text: str) -> int:
        try:
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except:
            return len(text.split()) * 1.3

