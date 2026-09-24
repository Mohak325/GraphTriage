from __future__ import annotations
import os
import json
import abc
from typing import Any
from dotenv import load_dotenv

load_dotenv()

class LLMProvider(abc.ABC):
    def __init__(self, model: str, temperature: float = 0.1, max_tokens: int = 4096):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abc.abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        pass

    @abc.abstractmethod
    async def generate_structured(self, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, temperature: float = 0.1, max_tokens: int = 4096):
        super().__init__(model, temperature, max_tokens)
        import openai
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content or ""

    async def generate_structured(self, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict:
        extended_prompt = f"{user_prompt}\n\nPlease return a JSON object matching the following schema:\n{json.dumps(schema)}"
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": extended_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

class GeminiProvider(LLMProvider):
    def __init__(self, model: str, temperature: float = 0.1, max_tokens: int = 4096):
        super().__init__(model, temperature, max_tokens)
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel(
            model_name=self.model,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }
        )

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        import google.generativeai as genai
        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_prompt,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }
        )
        response = await model.generate_content_async(user_prompt)
        return response.text

    async def generate_structured(self, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict:
        extended_prompt = f"{user_prompt}\n\nPlease return a JSON object matching the following schema:\n{json.dumps(schema)}"
        import google.generativeai as genai
        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_prompt,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
                "response_mime_type": "application/json"
            }
        )
        response = await model.generate_content_async(extended_prompt)
        return json.loads(response.text)

class LLMProviderFactory:
    @staticmethod
    def create(provider_name: str | None = None, model: str | None = None, **kwargs) -> LLMProvider:
        provider = provider_name or os.getenv("LLM_PROVIDER", "openai")
        model_name = model or os.getenv("LLM_MODEL", "gpt-4-turbo")
        
        if provider.lower() == "openai":
            return OpenAIProvider(model=model_name, **kwargs)
        elif provider.lower() == "gemini":
            return GeminiProvider(model=model_name, **kwargs)
        elif provider.lower() == "bedrock":
            from ai_models.llm.bedrock_provider import BedrockLLMProvider
            return BedrockLLMProvider(model_id=model_name, **kwargs)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
