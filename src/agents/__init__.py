"""Legal Document Annotation Agents"""
from .schema import AnnotationSchema
from .base import BaseAgent, AgentResult
from .llm_client import LLMClient, MockLLMClient, OpenAIClient, create_llm_client
from .annotation import AnnotationAgent

__all__ = [
    "AnnotationSchema",
    "BaseAgent", 
    "AgentResult",
    "LLMClient",
    "MockLLMClient",
    "OpenAIClient",
    "create_llm_client",
    "AnnotationAgent"
]
