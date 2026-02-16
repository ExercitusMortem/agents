"""
LLM Client - Abstraction layer for Large Language Model interactions.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMResponse:
    """Represents a response from an LLM."""
    
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.metadata = metadata or {}
    
    def __str__(self) -> str:
        return self.content


class BaseLLMClient(ABC):
    """Base class for LLM clients."""
    
    @abstractmethod
    def chat(self, system_prompt: str, user_message: str, **kwargs) -> LLMResponse:
        """
        Send a chat message to the LLM.
        
        Args:
            system_prompt: System message that sets the context/role
            user_message: The user's message/query
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse containing the model's response
        """
        pass


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o-mini)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
    
    def chat(self, system_prompt: str, user_message: str, **kwargs) -> LLMResponse:
        """Send a chat message to OpenAI."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        
        content = response.choices[0].message.content
        metadata = {
            "model": self.model,
            "usage": response.usage.model_dump() if response.usage else {},
            "finish_reason": response.choices[0].finish_reason
        }
        
        return LLMResponse(content=content, metadata=metadata)


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing without API keys."""
    
    def __init__(self):
        """Initialize mock client."""
        self.call_count = 0
    
    def chat(self, system_prompt: str, user_message: str, **kwargs) -> LLMResponse:
        """Generate mock responses based on the system prompt context."""
        self.call_count += 1
        
        # Generate contextual mock responses
        content = self._generate_mock_response(system_prompt, user_message)
        
        metadata = {
            "model": "mock",
            "call_count": self.call_count
        }
        
        return LLMResponse(content=content, metadata=metadata)
    
    def _generate_mock_response(self, system_prompt: str, user_message: str) -> str:
        """Generate a mock response based on the context."""
        system_lower = system_prompt.lower()
        message_lower = user_message.lower()
        
        # Safety and Scope responses
        if "safety" in system_lower or "validate" in system_lower:
            return json.dumps({
                "is_legal_document": True,
                "jurisdiction": "Federal (US)",
                "document_type": "Statute",
                "contains_sensitive_info": False,
                "ready_for_processing": True,
                "confidence": "high",
                "reasoning": "Document appears to be a legal statute with clear structure and professional language."
            })
        
        # Structuring responses
        elif "structure" in system_lower or "parse" in system_lower or "section" in system_lower:
            return json.dumps({
                "sections": [
                    {
                        "id": "1",
                        "title": "Definitions",
                        "content": "This section contains key definitions for terms used throughout the statute.",
                        "type": "section"
                    },
                    {
                        "id": "2",
                        "title": "Requirements",
                        "content": "This section outlines the main requirements and obligations.",
                        "type": "section"
                    }
                ],
                "structure_type": "numbered_sections",
                "has_preamble": False
            })
        
        # Annotation responses
        elif "annotate" in system_lower or "obligation" in system_lower or "deadline" in system_lower:
            return json.dumps({
                "obligations": [
                    {
                        "text": "Contractor shall obtain proper licensing",
                        "type": "mandatory",
                        "section_id": "2"
                    }
                ],
                "deadlines": [
                    {
                        "text": "Within 30 days of commencing operations",
                        "type": "deadline",
                        "section_id": "2"
                    }
                ],
                "penalties": [
                    {
                        "text": "Fine of not less than $5,000",
                        "type": "penalty",
                        "section_id": "3"
                    }
                ]
            })
        
        # Research responses
        elif "research" in system_lower or "reference" in system_lower or "case" in system_lower:
            return json.dumps({
                "cross_references": [
                    {
                        "reference": "Section 5",
                        "type": "internal",
                        "section_id": "2"
                    }
                ],
                "case_law": [
                    {
                        "citation": "Smith v. Jones, 123 F.3d 456",
                        "relevance": "high",
                        "section_id": "2"
                    }
                ],
                "related_topics": ["Contract Law", "Liability"]
            })
        
        # Formatting responses
        elif "format" in system_lower or "report" in system_lower:
            return """# Legal Document Analysis Report

## Executive Summary
This document has been analyzed and structured for review.

## Key Findings
- Multiple obligations identified
- Time-sensitive requirements noted
- Cross-references documented

## Detailed Analysis
[Full analysis follows...]"""
        
        # Default response
        else:
            return json.dumps({
                "response": "Analysis completed successfully.",
                "confidence": "medium"
            })


def create_llm_client(provider: Optional[str] = None) -> BaseLLMClient:
    """
    Factory function to create an LLM client based on the provider.
    
    Args:
        provider: LLM provider name ('openai', 'mock', or None for env-based)
        
    Returns:
        BaseLLMClient instance
    """
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "mock")
    
    provider = provider.lower()
    
    if provider == "openai":
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return OpenAIClient(model=model)
    elif provider == "mock":
        return MockLLMClient()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
