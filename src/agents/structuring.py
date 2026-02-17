"""
Structuring Agent - Breaks raw text into discrete articles/sections.
"""
from typing import Dict, Any, List
import re
from .base import BaseAgent, AgentResult


class StructuringAgent(BaseAgent):
    """
    Agent that breaks down raw legal text into structured sections.
    Identifies articles, sections, subsections, and paragraphs.
    """
    
    def __init__(self):
        super().__init__("StructuringAgent")
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Parse and structure legal text into discrete sections.
        
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
            
            # Parse the document into sections
            sections = self._parse_sections(text)
            
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
                data=structured_data
            )
            
        except Exception as e:
            return self._create_result(
                success=False,
                error=f"Error in structuring: {str(e)}"
            )
    
    def _parse_sections(self, text: str) -> List[Dict[str, Any]]:
        """Parse text into sections based on legal document patterns."""
        sections = []
        
        # Split text into lines for better parsing
        lines = text.strip().split('\n')
        current_section = None
        current_content = []
        section_counter = 0
        
        # Pattern for section/article headers with capture groups
        section_header_pattern = (
            r'^(Artikel|Article|Section|Hoofdstuk|Afdeling)\s+'
            r'([\w.\-:]+)[.:]?\s*(.*)$'
        )
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            match = re.match(section_header_pattern, line, re.IGNORECASE)
            
            if match:
                # Save previous section if exists
                if current_section is not None:
                    current_section["content"] = '\n'.join(current_content).strip()
                    sections.append(current_section)
                
                # Start new section
                section_type = match.group(1)
                section_id = match.group(2)
                section_title = match.group(3).strip()
                
                current_section = {
                    "id": section_id,
                    "title": section_title or f"{section_type} {section_id}",
                    "content": "",
                    "type": "section"
                }
                current_content = []
                section_counter += 1
            elif current_section is not None:
                # Add content to current section
                current_content.append(line)
            else:
                # Content before first section (preamble)
                if not sections:
                    sections.append({
                        "id": "0",
                        "title": "Preamble",
                        "content": line,
                        "type": "preamble"
                    })
        
        # Save last section
        if current_section is not None:
            current_section["content"] = '\n'.join(current_content).strip()
            sections.append(current_section)
        
        # If no sections found, treat entire text as one section
        if not sections:
            sections.append({
                "id": "1",
                "title": "Main Text",
                "content": text.strip(),
                "type": "section"
            })
        
        return sections
    
    def _analyze_structure(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the overall document structure."""
        has_preamble = any(s["type"] == "preamble" for s in sections)
        section_count = sum(1 for s in sections if s["type"] == "section")
        
        return {
            "has_preamble": has_preamble,
            "section_count": section_count,
            "average_section_length": sum(len(s["content"]) for s in sections) // len(sections) if sections else 0
        }
