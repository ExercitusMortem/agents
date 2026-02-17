"""
Base Agent Infrastructure

Provides abstract base classes and data structures for legal document agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class AgentResult:
    """
    Standard result structure for all agents.
    
    Attributes:
        success: Whether the agent execution was successful
        data: The agent's output data
        error: Error message if execution failed
        metadata: Additional metadata about the execution
    """
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAgent(ABC):
    """
    Abstract base class for all legal document agents.
    
    All agents must implement the execute method which takes input
    and returns an AgentResult.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    @abstractmethod
    def execute(self, input_data: Any) -> AgentResult:
        """
        Execute the agent's main task.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            AgentResult with success status and output data
        """
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data before execution.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if input is valid, False otherwise
        """
        return True
    
    def preprocess(self, input_data: Any) -> Any:
        """
        Preprocess input data before execution.
        
        Args:
            input_data: Raw input data
            
        Returns:
            Preprocessed input data
        """
        return input_data
    
    def postprocess(self, output_data: Any) -> Any:
        """
        Postprocess output data after execution.
        
        Args:
            output_data: Raw output data
            
        Returns:
            Postprocessed output data
        """
        return output_data
