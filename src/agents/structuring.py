"""
Structuring Agent - Breaks raw text into discrete articles/sections using LLM.
"""
from typing import Dict, Any, List, Optional
import json
from .base import BaseAgent, AgentResult
from .llm_client import BaseLLMClient, create_llm_client


class StructuringAgent(BaseAgent):
    """
    LLM-powered agent that breaks down raw legal text into structured sections.
    Uses AI to intelligently identify and parse document structure.
    """
    
    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        super().__init__("StructuringAgent")
        self.llm_client = llm_client or create_llm_client()
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Parse and structure legal text into discrete sections using LLM.
        
        Expected input_data keys:
            - text: The raw legal text to structure
            - metadata: (optional) Metadata from previous agents
            
        Returns:
            AgentResult with structured sections
        """
        try:
            text = input_data.get("text", "")
            if not text:
                return self._create_result(
                    success=False,
                    error="No text provided for structuring"
                )
            
            # Use LLM to parse the document structure
            system_prompt = """You are a legal document structuring expert. Analyze the provided legal text and break it down into logical sections.

For each section, identify:
- Section ID/number (e.g., "1", "I", "A")
- Section title (if present)
- Section content (the actual text)
- Section type (preamble, section, article, subsection, etc.)

Respond in JSON format:
{
    "sections": [
        {
            "id": "section identifier",
            "title": "section title or description",
            "content": "section content",
            "type": "section|article|preamble|subsection"
        }
    ],
    "structure_type": "description of document structure",
    "has_preamble": true/false
}

Be thorough and capture all sections. Preserve the original text content."""

            user_message = f"""Parse this legal document into sections:

{text}"""

            response = self.llm_client.chat(system_prompt, user_message)
            
            # Parse LLM response
            try:
                parsed_data = json.loads(response.content)
                sections = parsed_data.get("sections", [])
            except json.JSONDecodeError:
                # Fallback: create a single section if parsing fails
                sections = [{
                    "id": "1",
                    "title": "Full Document",
                    "content": text,
                    "type": "section"
                }]
            
            if not sections:
                return self._create_result(
                    success=False,
                    error="Could not identify any sections in the document"
                )
            
            structured_data = {
                "sections": sections,
                "total_sections": len(sections),
                "document_structure": self._analyze_structure(sections)
            }
            
            return self._create_result(
                success=True,
                data=structured_data,
                metadata={"llm_metadata": response.metadata}
            )
            
        except Exception as e:
            return self._create_result(
                success=False,
                error=f"Error in structuring: {str(e)}"
            )
    
    def _analyze_structure(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the overall document structure."""
        has_preamble = any(s.get("type") == "preamble" for s in sections)
        section_count = sum(1 for s in sections if s.get("type") == "section")
        
        return {
            "has_preamble": has_preamble,
            "section_count": section_count,
            "average_section_length": sum(len(s.get("content", "")) for s in sections) // len(sections) if sections else 0
        }
