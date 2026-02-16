"""
LegalBot - Orchestrator agent for legal document analysis.

This agent manages a pipeline of specialized LLM-powered sub-agents to analyze 
statutes, codes, and case law following a strict 5-step workflow.
"""
from typing import Dict, Any, List, Optional
from .base import AgentResult
from .safety_scope import SafetyScopeAgent
from .structuring import StructuringAgent
from .annotation import AnnotationAgent
from .research import ResearchAgent
from .formatting import FormattingAgent
from .llm_client import BaseLLMClient, create_llm_client


class LegalBot:
    """
    Orchestrator agent that manages the LLM-powered legal document analysis pipeline.
    
    Workflow:
    1. Safety & Scope: Validates jurisdiction and legal context using LLM
    2. Structuring: Breaks raw text into discrete articles/sections using LLM
    3. Annotation: Identifies obligations, deadlines, and penalties using LLM
    4. Research: Finds cross-references and relevant case law using LLM
    5. Formatting: Compiles everything into a structured Markdown report using LLM
    """
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize LegalBot with LLM-powered sub-agents.
        
        Args:
            llm_provider: LLM provider to use ('openai', 'mock', or None for env-based)
        """
        # Create shared LLM client
        self.llm_client = create_llm_client(llm_provider)
        
        # Initialize all sub-agents with LLM client
        self.pipeline = [
            SafetyScopeAgent(self.llm_client),
            StructuringAgent(self.llm_client),
            AnnotationAgent(self.llm_client),
            ResearchAgent(self.llm_client),
            FormattingAgent(self.llm_client)
        ]
        self.results: List[AgentResult] = []
    
    def analyze(
        self,
        text: str,
        jurisdiction: Optional[str] = None,
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a legal document through the complete LLM-powered pipeline.
        
        Args:
            text: The raw legal text to analyze
            jurisdiction: (optional) Specific jurisdiction
            document_type: (optional) Type of legal document
            
        Returns:
            Dictionary containing the final analysis and all intermediate results
        """
        self.results = []
        
        # Prepare initial input
        current_data = {
            "text": text,
            "jurisdiction": jurisdiction,
            "document_type": document_type
        }
        
        # Execute pipeline
        try:
            # Step 1: Safety & Scope
            result = self._execute_step(0, current_data)
            if not result.success:
                return self._create_error_response(
                    "Safety & Scope validation failed",
                    result.error
                )
            validation_data = result.data
            
            # Step 2: Structuring
            current_data = {
                "text": text,
                "metadata": validation_data
            }
            result = self._execute_step(1, current_data)
            if not result.success:
                return self._create_error_response(
                    "Text structuring failed",
                    result.error
                )
            sections = result.data.get("sections", [])
            
            # Step 3: Annotation
            current_data = {"sections": sections}
            result = self._execute_step(2, current_data)
            if not result.success:
                return self._create_error_response(
                    "Annotation failed",
                    result.error
                )
            annotated_sections = result.data.get("annotated_sections", [])
            annotation_summary = result.data.get("summary", {})
            
            # Step 4: Research
            current_data = {"annotated_sections": annotated_sections}
            result = self._execute_step(3, current_data)
            if not result.success:
                return self._create_error_response(
                    "Research failed",
                    result.error
                )
            researched_sections = result.data.get("researched_sections", [])
            research_summary = result.data.get("summary", {})
            
            # Step 5: Formatting
            current_data = {
                "researched_sections": researched_sections,
                "validation_data": validation_data,
                "summary": {
                    "total_sections": len(sections),
                    **annotation_summary,
                    **research_summary
                }
            }
            result = self._execute_step(4, current_data)
            if not result.success:
                return self._create_error_response(
                    "Formatting failed",
                    result.error
                )
            
            # Success! Return comprehensive results
            return {
                "success": True,
                "report": result.data.get("report", ""),
                "validation": validation_data,
                "sections": researched_sections,
                "summary": {
                    "total_sections": len(sections),
                    **annotation_summary,
                    **research_summary
                },
                "pipeline_results": [
                    {
                        "agent": r.agent_name,
                        "success": r.success,
                        "error": r.error
                    }
                    for r in self.results
                ],
                "llm_provider": type(self.llm_client).__name__
            }
            
        except Exception as e:
            return self._create_error_response(
                "Pipeline execution failed",
                str(e)
            )
    
    def _execute_step(self, step_index: int, input_data: Dict[str, Any]) -> AgentResult:
        """Execute a single pipeline step and store the result."""
        agent = self.pipeline[step_index]
        result = agent.process(input_data)
        self.results.append(result)
        return result
    
    def _create_error_response(self, stage: str, error: str) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            "success": False,
            "error": error,
            "stage": stage,
            "pipeline_results": [
                {
                    "agent": r.agent_name,
                    "success": r.success,
                    "error": r.error
                }
                for r in self.results
            ],
            "llm_provider": type(self.llm_client).__name__
        }
    
    def get_pipeline_status(self) -> List[Dict[str, Any]]:
        """Get the status of all pipeline steps."""
        return [
            {
                "step": i + 1,
                "agent": agent.name,
                "status": "completed" if i < len(self.results) else "pending",
                "success": self.results[i].success if i < len(self.results) else None
            }
            for i, agent in enumerate(self.pipeline)
        ]
