"""
LegalBot Agent System

A pipeline-based system for analyzing legal documents including statutes,
codes, and case law using Large Language Model (LLM) agents.
"""
from .base import BaseAgent, AgentResult
from .llm_client import BaseLLMClient, OpenAIClient, MockLLMClient, create_llm_client
from .safety_scope import SafetyScopeAgent
from .structuring import StructuringAgent
from .annotation import AnnotationAgent
from .research import ResearchAgent
from .formatting import FormattingAgent
from .legalbot import LegalBot

__all__ = [
    "BaseAgent",
    "AgentResult",
    "BaseLLMClient",
    "OpenAIClient",
    "MockLLMClient",
    "create_llm_client",
    "SafetyScopeAgent",
    "StructuringAgent",
    "AnnotationAgent",
    "ResearchAgent",
    "FormattingAgent",
    "LegalBot"
]