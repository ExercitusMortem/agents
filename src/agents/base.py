"""
Base classes and models for the agent system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    """Result returned by an agent after processing."""
    
    agent_name: str = Field(..., description="Name of the agent that produced this result")
    success: bool = Field(..., description="Whether the agent completed successfully")
    data: Dict[str, Any] = Field(default_factory=dict, description="Output data from the agent")
    error: Optional[str] = Field(None, description="Error message if agent failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"[{self.agent_name}] {status}"


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Process input data and return a result.
        
        Args:
            input_data: Dictionary containing input data for the agent
            
        Returns:
            AgentResult containing the processed output
        """
        pass
    
    def _create_result(
        self, 
        success: bool, 
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Helper method to create an AgentResult."""
        return AgentResult(
            agent_name=self.name,
            success=success,
            data=data or {},
            error=error,
            metadata=metadata or {}
        )
