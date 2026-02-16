"""
Research Agent - Finds cross-references and relevant case law using LLM.
"""
from typing import Dict, Any, List, Optional
import json
from .base import BaseAgent, AgentResult
from .llm_client import BaseLLMClient, create_llm_client


class ResearchAgent(BaseAgent):
    """
    LLM-powered agent that identifies cross-references and finds relevant case law.
    Uses AI to intelligently link sections to related legal materials.
    """
    
    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        super().__init__("ResearchAgent")
        self.llm_client = llm_client or create_llm_client()
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Research cross-references and case law for annotated sections using LLM.
        
        Expected input_data keys:
            - annotated_sections: List of annotated sections
            
        Returns:
            AgentResult with research findings
        """
        try:
            sections = input_data.get("annotated_sections", [])
            if not sections:
                return self._create_result(
                    success=False,
                    error="No annotated sections provided for research"
                )
            
            # Research each section using LLM
            researched_sections = []
            all_cross_refs = []
            all_cases = []
            
            for section in sections:
                research = self._research_section_with_llm(section)
                researched_section = {
                    **section,
                    "research": research
                }
                researched_sections.append(researched_section)
                
                all_cross_refs.extend(research.get("cross_references", []))
                all_cases.extend(research.get("case_law", []))
            
            research_data = {
                "researched_sections": researched_sections,
                "summary": {
                    "total_cross_references": len(all_cross_refs),
                    "total_case_citations": len(all_cases)
                },
                "cross_references": all_cross_refs,
                "case_law": all_cases
            }
            
            return self._create_result(
                success=True,
                data=research_data
            )
            
        except Exception as e:
            return self._create_result(
                success=False,
                error=f"Error in research: {str(e)}"
            )
    
    def _research_section_with_llm(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Research a single section using LLM."""
        content = section.get("content", "")
        section_id = section.get("id", "")
        
        if not content or len(content.strip()) < 10:
            return {
                "cross_references": [],
                "case_law": [],
                "related_topics": []
            }
        
        system_prompt = """You are a legal research expert. Analyze the provided section and identify:

1. CROSS-REFERENCES - References to other sections or statutes
   - Internal references (Section X, Article Y)
   - External statutory references (U.S.C. §, C.F.R. §)
   - Other legal code references

2. CASE LAW - Legal case citations
   - Case names (Party v. Party)
   - Full citations with reporters (e.g., 123 F.3d 456)
   - Assess relevance if possible

3. RELATED TOPICS - Legal topics and practice areas
   - Contract law, tort law, criminal law, etc.
   - Specific legal concepts mentioned

Respond in JSON format:
{
    "cross_references": [
        {"reference": "citation text", "type": "internal|external|statutory", "section_id": "section id"}
    ],
    "case_law": [
        {"citation": "case citation", "relevance": "high|medium|low", "section_id": "section id"}
    ],
    "related_topics": ["topic1", "topic2"]
}"""

        user_message = f"""Analyze this legal section for references and case law:

Section ID: {section_id}
Section Title: {section.get('title', 'Untitled')}

Content:
{content}"""

        try:
            response = self.llm_client.chat(system_prompt, user_message)
            research = json.loads(response.content)
            
            # Ensure section_id is set for all items
            for ref in research.get("cross_references", []):
                ref["section_id"] = section_id
            for case in research.get("case_law", []):
                case["section_id"] = section_id
            
            return research
        except (json.JSONDecodeError, Exception):
            # Fallback to empty research if LLM fails
            return {
                "cross_references": [],
                "case_law": [],
                "related_topics": []
            }
