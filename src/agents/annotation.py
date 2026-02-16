"""
Annotation Agent - Identifies obligations, deadlines, and penalties using LLM.
"""
from typing import Dict, Any, List, Optional
import json
from .base import BaseAgent, AgentResult
from .llm_client import BaseLLMClient, create_llm_client


class AnnotationAgent(BaseAgent):
    """
    LLM-powered agent that annotates legal text with obligations, deadlines, and penalties.
    Uses AI to intelligently identify and extract key legal requirements.
    """
    
    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        super().__init__("AnnotationAgent")
        self.llm_client = llm_client or create_llm_client()
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Annotate structured sections with legal elements using LLM.
        
        Expected input_data keys:
            - sections: List of structured sections from StructuringAgent
            
        Returns:
            AgentResult with annotated sections
        """
        try:
            sections = input_data.get("sections", [])
            if not sections:
                return self._create_result(
                    success=False,
                    error="No sections provided for annotation"
                )
            
            # Annotate each section using LLM
            annotated_sections = []
            all_obligations = []
            all_deadlines = []
            all_penalties = []
            
            for section in sections:
                annotations = self._annotate_section_with_llm(section)
                annotated_section = {
                    **section,
                    "annotations": annotations
                }
                annotated_sections.append(annotated_section)
                
                all_obligations.extend(annotations.get("obligations", []))
                all_deadlines.extend(annotations.get("deadlines", []))
                all_penalties.extend(annotations.get("penalties", []))
            
            annotation_data = {
                "annotated_sections": annotated_sections,
                "summary": {
                    "total_obligations": len(all_obligations),
                    "total_deadlines": len(all_deadlines),
                    "total_penalties": len(all_penalties)
                },
                "obligations": all_obligations,
                "deadlines": all_deadlines,
                "penalties": all_penalties
            }
            
            return self._create_result(
                success=True,
                data=annotation_data
            )
            
        except Exception as e:
            return self._create_result(
                success=False,
                error=f"Error in annotation: {str(e)}"
            )
    
    def _annotate_section_with_llm(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Annotate a single section using LLM."""
        content = section.get("content", "")
        section_id = section.get("id", "")
        
        if not content or len(content.strip()) < 10:
            return {
                "obligations": [],
                "deadlines": [],
                "penalties": []
            }
        
        system_prompt = """You are a legal document annotation expert. Analyze the provided section and identify:

1. OBLIGATIONS - Requirements or duties (mandatory or permissive)
   - Mandatory: uses "shall", "must", "is required to"
   - Permissive: uses "may", "is permitted to"

2. DEADLINES - Time-sensitive requirements
   - Specific dates or time periods
   - Relative deadlines (within X days/weeks/months)

3. PENALTIES - Consequences for non-compliance
   - Fines, fees, or monetary penalties
   - Criminal penalties (imprisonment, etc.)
   - Administrative penalties (license suspension, etc.)

For each item found, extract the relevant text.

Respond in JSON format:
{
    "obligations": [
        {"text": "extracted obligation text", "type": "mandatory|permissive", "section_id": "section id"}
    ],
    "deadlines": [
        {"text": "extracted deadline text", "type": "deadline", "section_id": "section id"}
    ],
    "penalties": [
        {"text": "extracted penalty text", "type": "penalty", "section_id": "section id"}
    ]
}"""

        user_message = f"""Analyze this legal section:

Section ID: {section_id}
Section Title: {section.get('title', 'Untitled')}

Content:
{content}"""

        try:
            response = self.llm_client.chat(system_prompt, user_message)
            annotations = json.loads(response.content)
            
            # Ensure section_id is set for all items
            for obligation in annotations.get("obligations", []):
                obligation["section_id"] = section_id
            for deadline in annotations.get("deadlines", []):
                deadline["section_id"] = section_id
            for penalty in annotations.get("penalties", []):
                penalty["section_id"] = section_id
            
            return annotations
        except (json.JSONDecodeError, Exception):
            # Fallback to empty annotations if LLM fails
            return {
                "obligations": [],
                "deadlines": [],
                "penalties": []
            }
