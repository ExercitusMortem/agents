"""
LLM Client Abstraction Layer

Provides a unified interface for interacting with different LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Generate text from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate JSON response from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Parsed JSON response
        """
        pass


class MockLLMClient(LLMClient):
    """
    Mock LLM client for testing.
    
    Generates contextual responses based on system prompt keywords
    without requiring API keys.
    """
    
    def __init__(self, response_mode: str = 'auto'):
        """
        Initialize mock client.
        
        Args:
            response_mode: 'auto' for contextual responses, 'fixed' for predefined responses
        """
        self.response_mode = response_mode
        self.call_count = 0
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate mock text response."""
        self.call_count += 1
        
        # Generate contextual response based on keywords
        if system_prompt:
            combined = f"{system_prompt}\n{prompt}".lower()
        else:
            combined = prompt.lower()
        
        # Detect what kind of response is expected
        if 'annotation' in combined or 'annotate' in combined:
            return self._generate_annotation_response(prompt)
        elif 'structure' in combined or 'parse' in combined:
            return self._generate_structure_response(prompt)
        elif 'safety' in combined or 'risk' in combined:
            return self._generate_safety_response(prompt)
        else:
            return "Mock LLM response"
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate mock JSON response."""
        response = self.generate(prompt, system_prompt, **kwargs)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # If response is not JSON, wrap it
            return {"response": response, "mock": True}
    
    def _generate_annotation_response(self, prompt: str) -> str:
        """Generate mock annotation response."""
        # Extract text from prompt
        text = prompt.strip()
        
        # Generate basic annotations
        annotations = {
            "annotations": [
                {
                    "category": "OBLIGATION",
                    "subtype": "AFFIRMATIVE",
                    "text": "shall deliver",
                    "start": 0,
                    "end": 13
                }
            ],
            "text": text[:100] if len(text) > 100 else text
        }
        return json.dumps(annotations)
    
    def _generate_structure_response(self, prompt: str) -> str:
        """Generate mock structure response."""
        structure = {
            "sections": [
                {
                    "id": "1",
                    "title": "Introduction",
                    "content": "Sample content"
                }
            ]
        }
        return json.dumps(structure)
    
    def _generate_safety_response(self, prompt: str) -> str:
        """Generate mock safety response."""
        safety = {
            "risk_level": "low",
            "issues": [],
            "recommendations": []
        }
        return json.dumps(safety)


class OpenAIClient(LLMClient):
    """
    OpenAI LLM client.
    
    Requires openai package and API key.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4", **default_kwargs):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
            **default_kwargs: Default parameters for API calls
        """
        self.api_key = api_key
        self.model = model
        self.default_kwargs = default_kwargs
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text using OpenAI API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Merge default kwargs with call-specific kwargs
        params = {**self.default_kwargs, **kwargs}
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **params
        )
        
        return response.choices[0].message.content
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate JSON using OpenAI API."""
        # Add instruction to return JSON
        json_prompt = f"{prompt}\n\nPlease respond with valid JSON only."
        
        # Force JSON response format if supported
        if 'response_format' not in kwargs:
            kwargs['response_format'] = {"type": "json_object"}
        
        response = self.generate(json_prompt, system_prompt, **kwargs)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response}")


def create_llm_client(provider: str = 'mock', **kwargs) -> LLMClient:
    """
    Factory function to create LLM clients.
    
    Args:
        provider: 'mock' or 'openai'
        **kwargs: Provider-specific parameters
        
    Returns:
        LLMClient instance
    """
    if provider == 'mock':
        return MockLLMClient(**kwargs)
    elif provider == 'openai':
        return OpenAIClient(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")
