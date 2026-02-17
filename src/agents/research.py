"""
Research Agent - Finds cross-references and relevant case law.
"""
from typing import Dict, Any, List
import re
from .base import BaseAgent, AgentResult


class ResearchAgent(BaseAgent):
    """
    Agent that identifies cross-references and finds relevant case law.
    Links sections to related legal materials.
    """
    
    def __init__(self):
        super().__init__("ResearchAgent")
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Research cross-references and case law for annotated sections.
        
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
            
            # Research each section
            researched_sections = []
            all_cross_refs = []
            all_cases = []
            
            for section in sections:
                research = self._research_section(section)
                researched_section = {
                    **section,
                    "research": research
                }
                researched_sections.append(researched_section)
                
                all_cross_refs.extend(research["cross_references"])
                all_cases.extend(research["case_law"])
            
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
    
    def _research_section(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Research a single section for cross-references and case law."""
        content = section.get("content", "")
        section_id = section.get("id", "")
        
        return {
            "cross_references": self._find_cross_references(content, section_id),
            "case_law": self._find_case_citations(content, section_id),
            "related_topics": self._identify_related_topics(content)
        }
    
    def _find_cross_references(self, text: str, section_id: str) -> List[Dict[str, str]]:
        """Find references to other sections or statutes."""
        cross_refs = []
        seen_refs = set()  # Avoid duplicates
        
        # Patterns for cross-references
        ref_patterns = [
            (r'Artikel\s+([\w.\-:]+)', 'Artikel'),
            (r'Hoofdstuk\s+([\w.\-:]+)', 'Hoofdstuk'),
            (r'Afdeling\s+([\w.\-:]+)', 'Afdeling'),
            (r'BWB[RV]\d{7}', 'Wetten-ID'),
            (r'Section\s+([IVXivx\d]+)', 'Section'),
            (r'§\s*([IVXivx\d]+)', 'Section'),
            (r'Article\s+([IVXivx\d]+)', 'Article'),
            (r'(\d+)\s+U\.?\s?S\.?\s?C\.?\s+§?\s*(\d+)', 'USC'),  # US Code
            (r'(\d+)\s+C\.?\s?F\.?\s?R\.?\s+§?\s*(\d+)', 'CFR'),  # Code of Federal Regulations
        ]
        
        for pattern, ref_type in ref_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ref_text = match.group(0).strip()
                # Avoid duplicates
                if ref_text.lower() not in seen_refs:
                    seen_refs.add(ref_text.lower())
                    cross_refs.append({
                        "section_id": section_id,
                        "reference": ref_text,
                        "type": ref_type
                    })
        
        return cross_refs
    
    def _find_case_citations(self, text: str, section_id: str) -> List[Dict[str, str]]:
        """Find legal case citations."""
        cases = []
        seen_cases = set()  # Avoid duplicates

        # Pattern for Dutch case law (ECLI)
        ecli_pattern = r'\bECLI:[A-Z]{2}:[A-Z0-9]+:\d{4}:\d+\b'
        for match in re.finditer(ecli_pattern, text, re.IGNORECASE):
            citation = match.group(0).upper()
            if citation.lower() not in seen_cases:
                seen_cases.add(citation.lower())
                cases.append({
                    "section_id": section_id,
                    "citation": citation,
                    "type": "case_law"
                })
        
        # Pattern for case names: "Smith v. Jones"
        case_name_pattern = r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+v\.?\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)'
        
        matches = re.finditer(case_name_pattern, text)
        for match in matches:
            case_text = match.group(0).strip()
            # Look ahead for full citation (e.g., "123 F.3d 456")
            remainder = text[match.end():match.end()+100]
            citation_pattern = r'\s*,?\s*(\d+\s+[A-Z][a-zA-Z.]*\s+\d+)'
            citation_match = re.match(citation_pattern, remainder)
            
            if citation_match:
                full_citation = case_text + citation_match.group(0).strip()
            else:
                full_citation = case_text
            
            # Avoid duplicates
            if full_citation.lower() not in seen_cases:
                seen_cases.add(full_citation.lower())
                cases.append({
                    "section_id": section_id,
                    "citation": full_citation,
                    "type": "case_law"
                })
        
        return cases
    
    def _identify_related_topics(self, text: str) -> List[str]:
        """Identify related legal topics and keywords."""
        topics = []
        
        # Common legal topic keywords
        topic_keywords = [
            "contract", "tort", "criminal", "civil", "constitutional",
            "property", "liability", "negligence", "damages", "jurisdiction",
            "procedure", "evidence", "appeal", "compliance", "enforcement",
            "bestuursrecht", "strafrecht", "civiel", "vergunning", "handhaving",
            "bezwaar", "beroep", "aansprakelijkheid", "toezicht"
        ]
        
        text_lower = text.lower()
        for keyword in topic_keywords:
            if keyword in text_lower:
                topics.append(keyword.title())
        
        return list(set(topics))  # Remove duplicates
