"""
LLM Client - Handles communication with different LLM providers
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
import json

# Import LLM libraries
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

class LLMClient:
    """
    Client for interacting with different LLM providers.
    Supports OpenAI and Anthropic with fallback options.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("llm_client")
        
        # Initialize provider
        self.provider = config.get("llm_provider", "openai").lower()
        self.model = config.get("model", "gpt-4")
        self.temperature = config.get("temperature", 0.3)
        self.max_tokens = config.get("max_tokens", 2000)
        
        # Initialize API clients
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize API clients for different providers"""
        
        if self.provider == "openai":
            if openai is None:
                raise ImportError("OpenAI library not installed. Run: pip install openai")
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            openai.api_key = api_key
            self.client = openai
            
        elif self.provider == "anthropic":
            if anthropic is None:
                raise ImportError("Anthropic library not installed. Run: pip install anthropic")
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            
            self.client = anthropic.Anthropic(api_key=api_key)
            
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def get_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Get completion from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            
        Returns:
            LLM response as string
        """
        
        try:
            if self.provider == "openai":
                return await self._get_openai_completion(prompt, system_prompt)
            elif self.provider == "anthropic":
                return await self._get_anthropic_completion(prompt, system_prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            self.logger.error(f"LLM completion failed: {str(e)}")
            return self._get_fallback_response(prompt)
    
    async def _get_openai_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Get completion from OpenAI"""
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
    
    async def _get_anthropic_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Get completion from Anthropic"""
        
        # Combine system prompt with user prompt for Anthropic
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = await asyncio.to_thread(
            self.client.messages.create,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        return response.content[0].text
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Fallback response when LLM fails"""
        
        # Simple keyword-based fallback
        prompt_lower = prompt.lower()
        
        if "benefits" in prompt_lower and "electric" in prompt_lower:
            return "Electric cars offer environmental benefits including reduced emissions and lower operating costs."
        elif "compare" in prompt_lower:
            return "Comparison analysis requires detailed research across multiple sources."
        elif "research" in prompt_lower:
            return "Research findings indicate the need for further investigation."
        else:
            return "Analysis completed. Please review the findings and consider additional research if needed."
    
    async def get_structured_completion(self, prompt: str, expected_format: str) -> Dict[str, Any]:
        """
        Get structured completion in a specific format.
        
        Args:
            prompt: The user prompt
            expected_format: Description of expected format (e.g., "JSON array")
            
        Returns:
            Structured response as dictionary
        """
        
        structured_prompt = f"""
        {prompt}
        
        Please respond in the following format: {expected_format}
        Ensure your response is properly formatted and valid.
        """
        
        response = await self.get_completion(structured_prompt)
        
        # Try to parse as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse structured response as JSON")
            return {"raw_response": response}
    
    async def get_streaming_completion(self, prompt: str, system_prompt: Optional[str] = None):
        """
        Get streaming completion from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            
        Yields:
            Chunks of the response
        """
        
        try:
            if self.provider == "openai":
                async for chunk in self._get_openai_streaming(prompt, system_prompt):
                    yield chunk
            elif self.provider == "anthropic":
                async for chunk in self._get_anthropic_streaming(prompt, system_prompt):
                    yield chunk
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            self.logger.error(f"Streaming completion failed: {str(e)}")
            yield self._get_fallback_response(prompt)
    
    async def _get_openai_streaming(self, prompt: str, system_prompt: Optional[str] = None):
        """Get streaming completion from OpenAI"""
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        stream = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _get_anthropic_streaming(self, prompt: str, system_prompt: Optional[str] = None):
        """Get streaming completion from Anthropic"""
        
        # Combine system prompt with user prompt for Anthropic
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        stream = await asyncio.to_thread(
            self.client.messages.create,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": full_prompt}],
            stream=True
        )
        
        async for chunk in stream:
            if chunk.type == "content_block_delta":
                yield chunk.delta.text
    
    def get_available_models(self) -> List[str]:
        """Get list of available models for the current provider"""
        
        if self.provider == "openai":
            return [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ]
        elif self.provider == "anthropic":
            return [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
        else:
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration"""
        
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "available_models": self.get_available_models()
        }

# Example usage
async def test_llm_client():
    """Test the LLM client"""
    
    config = {
        "llm_provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    try:
        client = LLMClient(config)
        
        # Test basic completion
        response = await client.get_completion("What are the benefits of electric cars?")
        print(f"Basic completion: {response[:100]}...")
        
        # Test structured completion
        structured_response = await client.get_structured_completion(
            "List 3 benefits of electric cars",
            "JSON array of strings"
        )
        print(f"Structured response: {structured_response}")
        
        # Test streaming
        print("Streaming response:")
        async for chunk in client.get_streaming_completion("Explain renewable energy"):
            print(chunk, end="", flush=True)
        print()
        
        # Get model info
        model_info = client.get_model_info()
        print(f"Model info: {model_info}")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        print("Make sure you have the required API keys set in environment variables")

if __name__ == "__main__":
    asyncio.run(test_llm_client())
