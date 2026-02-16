"""
Safety and Scope Agent - Validates jurisdiction and legal context.
"""
from typing import Dict, Any
from .base import BaseAgent, AgentResult


class SafetyScopeAgent(BaseAgent):
    """
    Agent that validates jurisdiction and legal context before processing.
    Ensures the input is appropriate for legal analysis.
    """
    
    def __init__(self):
        super().__init__("SafetyScopeAgent")
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Validate the legal document for jurisdiction and context.
        
        Expected input_data keys:
            - text: The raw legal text to analyze
            - jurisdiction: (optional) Specific jurisdiction to validate
            - document_type: (optional) Type of legal document
            
        Returns:
            AgentResult with validation results
        """
        try:
            text = input_data.get("text", "")
            if not text or not text.strip():
                return self._create_result(
                    success=False,
                    error="No text provided for analysis"
                )
            
            # Analyze the document for safety and scope
            validation_results = {
                "is_legal_document": True,
                "contains_personal_info": self._check_personal_info(text),
                "jurisdiction_identified": self._identify_jurisdiction(text, input_data.get("jurisdiction")),
                "document_type": self._identify_document_type(text, input_data.get("document_type")),
                "word_count": len(text.split()),
                "ready_for_processing": True
            }
            
            # Check if document is ready for processing
            if validation_results["word_count"] < 10:
                validation_results["ready_for_processing"] = False
                return self._create_result(
                    success=False,
                    data=validation_results,
                    error="Document too short for meaningful analysis"
                )
            
            return self._create_result(
                success=True,
                data=validation_results,
                metadata={"original_text": text}
            )
            
        except Exception as e:
            return self._create_result(
                success=False,
                error=f"Error in safety and scope validation: {str(e)}"
            )
    
    def _check_personal_info(self, text: str) -> bool:
        """Check if text contains potential personal information."""
        # Simple heuristic - in real implementation would use NER
        pii_indicators = ["SSN", "social security", "date of birth", "DOB"]
        text_lower = text.lower()
        return any(indicator.lower() in text_lower for indicator in pii_indicators)
    
    def _identify_jurisdiction(self, text: str, provided_jurisdiction: Any) -> str:
        """Identify the legal jurisdiction from the text or use provided."""
        if provided_jurisdiction:
            return str(provided_jurisdiction)
        
        # Simple heuristic - look for jurisdiction indicators
        text_lower = text.lower()
        if "federal" in text_lower or "united states code" in text_lower:
            return "Federal (US)"
        elif "state of" in text_lower:
            # Try to extract state name
            return "State (Unspecified)"
        else:
            return "Unknown"
    
    def _identify_document_type(self, text: str, provided_type: Any) -> str:
        """Identify the type of legal document."""
        if provided_type:
            return str(provided_type)
        
        text_lower = text.lower()
        if "§" in text or "section" in text_lower:
            return "Statute/Code"
        elif "plaintiff" in text_lower or "defendant" in text_lower:
            return "Case Law"
        elif "ordinance" in text_lower:
            return "Ordinance"
        else:
            return "General Legal Document"
