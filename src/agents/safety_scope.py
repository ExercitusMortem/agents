"""
Safety and Scope Agent - Validates jurisdiction and legal context using LLM.
"""
from typing import Dict, Any, Optional
import json
from .base import BaseAgent, AgentResult
from .llm_client import BaseLLMClient, create_llm_client


class SafetyScopeAgent(BaseAgent):
    """
    LLM-powered agent that validates jurisdiction and legal context before processing.
    Uses AI to understand and classify legal documents intelligently.
    """
    
    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        super().__init__("SafetyScopeAgent")
        self.llm_client = llm_client or create_llm_client()
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Validate the legal document for jurisdiction and context using LLM.
        
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
            
            # Basic length check
            if len(text.split()) < 10:
                return self._create_result(
                    success=False,
                    error="Document too short for meaningful analysis"
                )
            
            # Use LLM to analyze the document
            system_prompt = """You are a legal document validation expert. Analyze the provided text and determine:
1. Whether it is a legal document
2. The jurisdiction (Federal, State, International, etc.)
3. The document type (Statute, Regulation, Case Law, Contract, etc.)
4. Whether it contains sensitive personal information
5. Whether it is ready for detailed legal analysis

Respond in JSON format with these fields:
{
    "is_legal_document": true/false,
    "jurisdiction": "identified jurisdiction",
    "document_type": "type of document",
    "contains_sensitive_info": true/false,
    "ready_for_processing": true/false,
    "confidence": "high/medium/low",
    "reasoning": "brief explanation"
}"""

            user_message = f"""Analyze this document:

Provided context:
- Jurisdiction hint: {input_data.get('jurisdiction', 'Not specified')}
- Document type hint: {input_data.get('document_type', 'Not specified')}

Document text:
{text[:2000]}{'...' if len(text) > 2000 else ''}"""

            response = self.llm_client.chat(system_prompt, user_message)
            
            # Parse LLM response
            try:
                validation_results = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback if LLM doesn't return valid JSON
                validation_results = {
                    "is_legal_document": True,
                    "jurisdiction": input_data.get("jurisdiction", "Unknown"),
                    "document_type": input_data.get("document_type", "Legal Document"),
                    "contains_sensitive_info": False,
                    "ready_for_processing": True,
                    "confidence": "low",
                    "reasoning": "LLM response parsing failed, using defaults"
                }
            
            # Add basic stats
            validation_results["word_count"] = len(text.split())
            validation_results["jurisdiction_identified"] = validation_results.get("jurisdiction", "Unknown")
            
            # Check if ready for processing
            if not validation_results.get("ready_for_processing", True):
                return self._create_result(
                    success=False,
                    data=validation_results,
                    error=validation_results.get("reasoning", "Document not ready for processing")
                )
            
            return self._create_result(
                success=True,
                data=validation_results,
                metadata={"original_text": text, "llm_metadata": response.metadata}
            )
            
        except Exception as e:
            return self._create_result(
                success=False,
                error=f"Error in safety and scope validation: {str(e)}"
            )
