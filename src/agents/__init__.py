"""
LegalBot Agent System

A pipeline-based system for analyzing legal documents including statutes,
codes, and case law.
"""
from .base import BaseAgent, AgentResult
from .safety_scope import SafetyScopeAgent
from .structuring import StructuringAgent
from .annotation import AnnotationAgent
from .research import ResearchAgent
from .formatting import FormattingAgent
from .legalbot import LegalBot

__all__ = [
    "BaseAgent",
    "AgentResult",
    "SafetyScopeAgent",
    "StructuringAgent",
    "AnnotationAgent",
    "ResearchAgent",
    "FormattingAgent",
    "LegalBot"
]