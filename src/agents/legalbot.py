"""
LegalBot - Orchestrator agent for legal document analysis.

This agent manages a pipeline of specialized sub-agents to analyze
statutes, codes, and case law following a strict 5-step workflow.
"""
from typing import Dict, Any, List, Optional
import re
from urllib.request import Request, urlopen
from .base import AgentResult
from .safety_scope import SafetyScopeAgent
from .structuring import StructuringAgent
from .annotation import AnnotationAgent
from .research import ResearchAgent
from .formatting import FormattingAgent


class LegalBot:
    """
    Orchestrator agent that manages the legal document analysis pipeline.
    
    Workflow:
    1. Safety & Scope: Validates jurisdiction and legal context
    2. Structuring: Breaks raw text into discrete articles/sections
    3. Annotation: Identifies obligations, deadlines, and penalties
    4. Research: Finds cross-references and relevant case law
    5. Formatting: Compiles everything into a structured Markdown report
    """
    
    def __init__(self):
        """Initialize LegalBot with all sub-agents."""
        self.pipeline = [
            SafetyScopeAgent(),
            StructuringAgent(),
            AnnotationAgent(),
            ResearchAgent(),
            FormattingAgent()
        ]
        self.results: List[AgentResult] = []
    
    def analyze(
        self,
        text: str,
        jurisdiction: Optional[str] = None,
        document_type: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a legal document through the complete pipeline.
        
        Args:
            text: The raw legal text to analyze
            jurisdiction: (optional) Specific jurisdiction
            document_type: (optional) Type of legal document
            source_url: (optional) Source URL to fetch legal text from,
                        e.g. wetten.overheid.nl
            
        Returns:
            Dictionary containing the final analysis and all intermediate results
        """
        self.results = []
        
        source_url = source_url or self._extract_url_from_text(text)
        document_text = text

        if source_url and not document_text.strip():
            try:
                document_text = self._fetch_legal_text_from_url(source_url)
            except Exception as error:
                return self._create_error_response(
                    "Source retrieval failed",
                    str(error)
                )

        # Prepare initial input
        current_data = {
            "text": document_text,
            "jurisdiction": jurisdiction,
            "document_type": document_type,
            "source_url": source_url
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
                "text": document_text,
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
                "source_url": source_url,
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
                ]
            }

        except Exception as e:
            return self._create_error_response(
                "Pipeline execution failed",
                str(e)
            )

    def _extract_url_from_text(self, text: str) -> Optional[str]:
        """Extract a URL from text if the input is a plain URL string."""
        candidate = text.strip()
        if re.match(r"^https?://", candidate, re.IGNORECASE):
            return candidate
        return None

    def _fetch_legal_text_from_url(self, source_url: str) -> str:
        """Fetch and normalize legal text content from a source URL."""
        request = Request(
            source_url,
            headers={
                "User-Agent": "LegalBot/0.1 (+https://github.com/ExercitusMortem/agents)"
            }
        )

        with urlopen(request, timeout=20) as response:
            raw_bytes = response.read()
            content_type = response.headers.get("Content-Type", "")

        encoding = "utf-8"
        if "charset=" in content_type:
            encoding = content_type.split("charset=", 1)[1].split(";", 1)[0].strip()

        html = raw_bytes.decode(encoding, errors="replace")
        extracted = self._extract_text_from_html(html)

        if len(extracted.split()) < 10:
            raise ValueError("Fetched source did not contain enough legal text for analysis")

        return extracted

    def _extract_text_from_html(self, html: str) -> str:
        """Extract visible text content from HTML using lightweight cleaning."""
        text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
        text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
        text = re.sub(r"(?is)<noscript.*?>.*?</noscript>", " ", text)
        text = re.sub(r"(?is)<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    
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
            ]
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
