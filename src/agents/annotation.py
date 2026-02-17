"""
Legal Document Annotation Agent

Applies the annotation schema to legal documents.
"""

import json
import re
from typing import Dict, List, Any, Optional
from .base import BaseAgent, AgentResult
from .schema import AnnotationSchema
from .llm_client import LLMClient


class AnnotationAgent(BaseAgent):
    """
    Agent for annotating legal documents with the defined schema.
    
    Uses LLM to identify and tag legal entities, obligations, rights,
    deadlines, and other elements according to the annotation schema.
    """
    
    def __init__(self, llm_client: LLMClient, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the annotation agent.
        
        Args:
            llm_client: LLM client for generating annotations
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self.llm_client = llm_client
        self.schema = AnnotationSchema()
    
    def execute(self, input_data: Any) -> AgentResult:
        """
        Execute annotation on legal text.
        
        Args:
            input_data: Dictionary with 'text' key containing legal document text
            
        Returns:
            AgentResult with annotations in data field
        """
        try:
            # Validate input
            if not self.validate_input(input_data):
                return AgentResult(
                    success=False,
                    error="Invalid input: expected dictionary with 'text' key"
                )
            
            # Extract text
            text = input_data.get('text', '')
            if not text:
                return AgentResult(
                    success=False,
                    error="Empty text provided"
                )
            
            # Generate annotations
            annotations = self._annotate_text(text)
            
            return AgentResult(
                success=True,
                data={
                    'text': text,
                    'annotations': annotations,
                    'schema_version': '1.0'
                },
                metadata={
                    'annotation_count': len(annotations),
                    'categories_used': list(set(a['category'] for a in annotations))
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Annotation failed: {str(e)}"
            )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data."""
        if not isinstance(input_data, dict):
            return False
        if 'text' not in input_data:
            return False
        return True
    
    def _annotate_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Annotate text using LLM and schema.
        
        Args:
            text: Legal document text to annotate
            
        Returns:
            List of annotation dictionaries
        """
        # Build prompt with schema information
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(text)
        
        # Get LLM response
        try:
            response = self.llm_client.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            # Extract annotations from response
            if isinstance(response, dict) and 'annotations' in response:
                annotations = response['annotations']
            elif isinstance(response, list):
                annotations = response
            else:
                # Fallback: apply rule-based annotations
                annotations = self._rule_based_annotation(text)
            
            # Validate and clean annotations
            return self._validate_annotations(annotations)
            
        except Exception as e:
            # Fallback to rule-based annotation
            return self._rule_based_annotation(text)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with schema information."""
        schema_dict = self.schema.to_dict()
        
        prompt = """You are a legal document annotation expert. Your task is to annotate legal text according to the following schema:

"""
        
        # Add category descriptions
        for category, info in schema_dict.items():
            prompt += f"\n{category}: {info['description']}\n"
            for subtype, subinfo in info['subtypes'].items():
                prompt += f"  - {subtype}: {subinfo['description']}\n"
        
        prompt += """
Return annotations as a JSON array with objects containing:
- category: Main category label
- subtype: Subtype label
- text: The exact text span being annotated
- start: Starting character position
- end: Ending character position
- context: Brief explanation of why this annotation applies

Format: {"annotations": [...]}
"""
        return prompt
    
    def _build_user_prompt(self, text: str) -> str:
        """Build user prompt for annotation."""
        return f"""Annotate the following legal text:

{text}

Identify and tag all relevant elements according to the schema. Be precise with text spans and positions."""
    
    def _rule_based_annotation(self, text: str) -> List[Dict[str, Any]]:
        """
        Apply rule-based annotation as fallback.
        
        Uses pattern matching to identify common legal elements.
        """
        annotations = []
        
        # Pattern definitions for each category
        patterns = {
            'OBLIGATION': {
                'AFFIRMATIVE': [
                    r'\b(shall|must|will|agrees to|required to|obligated to)\b.*?[.;]',
                    r'\b(responsible for|duty to)\b.*?[.;]'
                ],
                'PROHIBITIVE': [
                    r'\b(shall not|must not|may not|prohibited from|forbidden to)\b.*?[.;]',
                    r'\b(not permitted to|not allowed to)\b.*?[.;]'
                ],
                'PERMISSIVE': [
                    r'\b(may|can|permitted to|allowed to|has the option to)\b.*?[.;]'
                ]
            },
            'DEADLINE': {
                'ABSOLUTE': [
                    r'\b(by|before|on or before|no later than)\s+\w+\s+\d{1,2}(st|nd|rd|th)?,?\s+\d{4}\b',
                    r'\b(by|before|on or before|no later than)\s+\d{1,2}(st|nd|rd|th)?\s+\w+\s+\d{4}\b',
                    r'\b\d{1,2}/\d{1,2}/\d{4}\b'
                ],
                'RELATIVE': [
                    r'\b(within|after|upon)\s+\d+\s+(days?|weeks?|months?|years?)\b',
                    r'\b\d+\s+(days?|weeks?|months?|years?)\s+(of|from|after)\b'
                ]
            },
            'MONEY': {
                'AMOUNT': [
                    r'\$\s?\d+(?:,\d{3})*(?:\.\d{2})?',
                    r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s+(dollars?|USD|euros?|EUR|pounds?|GBP)\b'
                ],
                'PERCENTAGE': [
                    r'\b\d+(?:\.\d+)?%',
                    r'\b\d+(?:\.\d+)?\s+percent\b'
                ]
            },
            'PENALTY': {
                'FINANCIAL': [
                    r'\b(fine|penalty|fee|charge).*?\$\s?\d+',
                    r'\b(late|default|penalty)\s+(payment|fee|charge)\b.*?[.;]'
                ],
                'LEGAL': [
                    r'\b(injunction|imprisonment|prosecution|legal action)\b.*?[.;]'
                ]
            },
            'REFERENCE': {
                'STATUTE': [
                    r'\b(Section|Article|Clause|§)\s+\d+.*?(of the|under the).*?(Act|Code|Law|Regulation)',
                    r'\b\d+\s+U\.S\.C\.\s+§?\s*\d+\b'
                ],
                'INTERNAL': [
                    r'\b(see|refer to|as stated in)\s+(Section|Article|Clause|Appendix)\s+\d+',
                    r'\bClause\s+\d+(?:\.\d+)*\b'
                ]
            },
            'PARTIES': {
                'ROLE': [
                    r'\b(Plaintiff|Defendant|Tenant|Landlord|Buyer|Seller|Contractor|Client|Party|Parties)\b'
                ],
                'ORGANIZATION': [
                    r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\s+(Inc\.|Corp\.|LLC|Ltd\.|Company|Corporation)\b'
                ]
            }
        }
        
        # Apply patterns
        for category, subtypes in patterns.items():
            for subtype, pattern_list in subtypes.items():
                for pattern in pattern_list:
                    for match in re.finditer(pattern, text, re.IGNORECASE):
                        annotations.append({
                            'category': category,
                            'subtype': subtype,
                            'text': match.group(0),
                            'start': match.start(),
                            'end': match.end(),
                            'context': f'Pattern-based match for {category}/{subtype}'
                        })
        
        return annotations
    
    def _validate_annotations(self, annotations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean annotations.
        
        Ensures all annotations have required fields and valid categories.
        """
        validated = []
        
        for ann in annotations:
            # Check required fields
            if not all(k in ann for k in ['category', 'subtype', 'text']):
                continue
            
            # Validate category exists in schema
            if ann['category'] not in self.schema.categories:
                continue
            
            # Validate subtype exists
            category = self.schema.categories[ann['category']]
            if ann['subtype'] not in category.subtypes:
                continue
            
            # Add default values for optional fields
            if 'start' not in ann:
                ann['start'] = -1
            if 'end' not in ann:
                ann['end'] = -1
            if 'context' not in ann:
                ann['context'] = ''
            
            validated.append(ann)
        
        return validated
    
    def get_annotations_by_category(self, annotations: List[Dict[str, Any]], 
                                   category: str) -> List[Dict[str, Any]]:
        """Filter annotations by category."""
        return [a for a in annotations if a['category'] == category]
    
    def get_annotations_by_subtype(self, annotations: List[Dict[str, Any]], 
                                  category: str, subtype: str) -> List[Dict[str, Any]]:
        """Filter annotations by category and subtype."""
        return [a for a in annotations 
                if a['category'] == category and a['subtype'] == subtype]
