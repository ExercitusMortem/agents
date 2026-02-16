"""
Annotation Agent - Identifies obligations, deadlines, and penalties.
"""
from typing import Dict, Any, List
import re
from .base import BaseAgent, AgentResult


class AnnotationAgent(BaseAgent):
    """
    Agent that annotates legal text with obligations, deadlines, and penalties.
    Identifies key legal requirements and their implications.
    """
    
    def __init__(self):
        super().__init__("AnnotationAgent")
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Annotate structured sections with legal elements.
        
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
            
            # Annotate each section
            annotated_sections = []
            all_obligations = []
            all_deadlines = []
            all_penalties = []
            
            for section in sections:
                annotations = self._annotate_section(section)
                annotated_section = {
                    **section,
                    "annotations": annotations
                }
                annotated_sections.append(annotated_section)
                
                all_obligations.extend(annotations["obligations"])
                all_deadlines.extend(annotations["deadlines"])
                all_penalties.extend(annotations["penalties"])
            
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
    
    def _annotate_section(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Annotate a single section with legal elements."""
        content = section.get("content", "")
        
        return {
            "obligations": self._identify_obligations(content, section.get("id", "")),
            "deadlines": self._identify_deadlines(content, section.get("id", "")),
            "penalties": self._identify_penalties(content, section.get("id", ""))
        }
    
    def _identify_obligations(self, text: str, section_id: str) -> List[Dict[str, str]]:
        """Identify obligations using modal verbs and legal language."""
        obligations = []
        
        # Split into sentences for better matching
        sentences = re.split(r'[.!?]+', text)
        
        # Patterns for obligations
        obligation_patterns = [
            (r'\bshall\b', 'mandatory'),
            (r'\bmust\b', 'mandatory'),
            (r'\bis required to\b', 'mandatory'),
            (r'\bhas a duty to\b', 'mandatory'),
            (r'\bis obligated to\b', 'mandatory'),
            (r'\bmay\b', 'permissive'),
            (r'\bis permitted to\b', 'permissive')
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 5:
                continue
                
            for pattern, obligation_type in obligation_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    obligations.append({
                        "section_id": section_id,
                        "text": sentence.strip(),
                        "type": obligation_type
                    })
                    break  # Only match once per sentence
        
        return obligations
    
    def _identify_deadlines(self, text: str, section_id: str) -> List[Dict[str, str]]:
        """Identify deadlines and time requirements."""
        deadlines = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Patterns for deadlines
        deadline_patterns = [
            r'within\s+\d+\s+(?:day|week|month|year)s?',
            r'not later than',
            r'\d+\s+days?\s+(?:after|before)',
            r'\d+\s+(?:day|week|month|year)s?\s+(?:of|after|before)'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 5:
                continue
                
            for pattern in deadline_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    deadlines.append({
                        "section_id": section_id,
                        "text": sentence.strip(),
                        "type": "deadline"
                    })
                    break  # Only match once per sentence
        
        return deadlines
    
    def _identify_penalties(self, text: str, section_id: str) -> List[Dict[str, str]]:
        """Identify penalties and consequences."""
        penalties = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Patterns for penalties
        penalty_patterns = [
            r'fine of\s+\$?[\d,]+',
            r'imprisonment',
            r'penalty of',
            r'subject to',
            r'liable for',
            r'shall be punished',
            r'suspension',
            r'revocation'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 5:
                continue
                
            for pattern in penalty_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    penalties.append({
                        "section_id": section_id,
                        "text": sentence.strip(),
                        "type": "penalty"
                    })
                    break  # Only match once per sentence
        
        return penalties
