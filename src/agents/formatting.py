"""
Formatting Agent - Compiles everything into a structured Markdown report using LLM.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseAgent, AgentResult
from .llm_client import BaseLLMClient, create_llm_client


class FormattingAgent(BaseAgent):
    """
    LLM-powered agent that compiles all analysis results into a structured Markdown report.
    Uses AI to create a comprehensive, well-formatted legal analysis document.
    """
    
    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        super().__init__("FormattingAgent")
        self.llm_client = llm_client or create_llm_client()
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Format all research results into a Markdown report using LLM.
        
        Expected input_data keys:
            - researched_sections: List of fully researched sections
            - validation_data: Data from SafetyScopeAgent
            - summary: Aggregated summary data
            
        Returns:
            AgentResult with formatted Markdown report
        """
        try:
            sections = input_data.get("researched_sections", [])
            validation = input_data.get("validation_data", {})
            summary = input_data.get("summary", {})
            
            if not sections:
                return self._create_result(
                    success=False,
                    error="No sections provided for formatting"
                )
            
            # Prepare data for LLM
            sections_summary = []
            for section in sections:
                section_data = {
                    "id": section.get("id"),
                    "title": section.get("title"),
                    "content_preview": section.get("content", "")[:200],
                    "annotations": section.get("annotations", {}),
                    "research": section.get("research", {})
                }
                sections_summary.append(section_data)
            
            # Use LLM to generate a professional report
            system_prompt = """You are a legal document formatting expert. Create a comprehensive, professional Markdown report from the analyzed legal document data.

The report should include:
1. Title and metadata
2. Executive summary with key statistics
3. Detailed section-by-section analysis
4. Aggregated findings (obligations, deadlines, penalties)
5. Cross-references and case law
6. Professional formatting with headers, lists, and emphasis

Use proper Markdown syntax. Be thorough but concise. Make the report easy to navigate and understand."""

            user_message = f"""Generate a legal analysis report for this document:

VALIDATION DATA:
{validation}

SUMMARY STATISTICS:
{summary}

SECTIONS:
{sections_summary}

Create a complete, professional Markdown report."""

            try:
                response = self.llm_client.chat(system_prompt, user_message)
                markdown_report = response.content
            except Exception:
                # Fallback to template-based report if LLM fails
                markdown_report = self._generate_fallback_report(sections, validation, summary)
            
            format_data = {
                "report": markdown_report,
                "format": "markdown",
                "sections_formatted": len(sections),
                "report_length": len(markdown_report)
            }
            
            return self._create_result(
                success=True,
                data=format_data
            )
            
        except Exception as e:
            return self._create_result(
                success=False,
                error=f"Error in formatting: {str(e)}"
            )
    
    def _generate_fallback_report(
        self,
        sections: list,
        validation: Dict[str, Any],
        summary: Dict[str, Any]
    ) -> str:
        """Generate a fallback template-based report if LLM fails."""
        lines = []
        
        # Header
        lines.append("# Legal Document Analysis Report")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        
        if validation:
            lines.append(f"**Document Type:** {validation.get('document_type', 'Unknown')}")
            lines.append(f"**Jurisdiction:** {validation.get('jurisdiction_identified', validation.get('jurisdiction', 'Unknown'))}")
            lines.append(f"**Word Count:** {validation.get('word_count', 0)}")
            lines.append("")
        
        if summary:
            lines.append(f"**Total Sections:** {summary.get('total_sections', 0)}")
            lines.append(f"**Obligations Identified:** {summary.get('total_obligations', 0)}")
            lines.append(f"**Deadlines Identified:** {summary.get('total_deadlines', 0)}")
            lines.append(f"**Penalties Identified:** {summary.get('total_penalties', 0)}")
            lines.append(f"**Cross-References Found:** {summary.get('total_cross_references', 0)}")
            lines.append(f"**Case Citations Found:** {summary.get('total_case_citations', 0)}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Detailed Analysis
        lines.append("## Detailed Analysis")
        lines.append("")
        
        for section in sections:
            lines.extend(self._format_section(section))
            lines.append("")
        
        # Aggregated findings
        self._add_aggregated_findings(lines, sections)
        
        lines.append("---")
        lines.append("")
        lines.append("*Report generated by LegalBot - LLM-Powered Legal Document Analysis System*")
        
        return "\n".join(lines)
    
    def _format_section(self, section: Dict[str, Any]) -> list:
        """Format a single section for the report."""
        lines = []
        
        section_id = section.get("id", "")
        title = section.get("title", "Untitled Section")
        content = section.get("content", "")
        
        # Section header
        lines.append(f"### Section {section_id}: {title}")
        lines.append("")
        
        # Section content (truncated if too long)
        if len(content) > 500:
            lines.append(f"*{content[:500]}...*")
        else:
            lines.append(f"*{content}*")
        lines.append("")
        
        # Annotations
        annotations = section.get("annotations", {})
        
        obligations = annotations.get("obligations", [])
        if obligations:
            lines.append("**Obligations:**")
            for obligation in obligations:
                lines.append(f"- {obligation.get('text', '')} *(Type: {obligation.get('type', 'unknown')})*")
            lines.append("")
        
        deadlines = annotations.get("deadlines", [])
        if deadlines:
            lines.append("**Deadlines:**")
            for deadline in deadlines:
                lines.append(f"- {deadline.get('text', '')}")
            lines.append("")
        
        penalties = annotations.get("penalties", [])
        if penalties:
            lines.append("**Penalties:**")
            for penalty in penalties:
                lines.append(f"- {penalty.get('text', '')}")
            lines.append("")
        
        # Research findings
        research = section.get("research", {})
        
        related_topics = research.get("related_topics", [])
        if related_topics:
            lines.append(f"**Related Topics:** {', '.join(related_topics)}")
            lines.append("")
        
        return lines
    
    def _add_aggregated_findings(self, lines: list, sections: list):
        """Add aggregated findings to the report."""
        # Collect all items
        obligations = []
        deadlines = []
        penalties = []
        cross_refs = []
        cases = []
        
        for section in sections:
            annotations = section.get("annotations", {})
            research = section.get("research", {})
            
            obligations.extend(annotations.get("obligations", []))
            deadlines.extend(annotations.get("deadlines", []))
            penalties.extend(annotations.get("penalties", []))
            cross_refs.extend(research.get("cross_references", []))
            cases.extend(research.get("case_law", []))
        
        if obligations:
            lines.append("---")
            lines.append("")
            lines.append("## All Obligations")
            lines.append("")
            for i, obligation in enumerate(obligations, 1):
                lines.append(f"{i}. **[Section {obligation.get('section_id', 'N/A')}]** {obligation.get('text', '')} *(Type: {obligation.get('type', 'unknown')})*")
            lines.append("")
        
        if deadlines:
            lines.append("---")
            lines.append("")
            lines.append("## All Deadlines")
            lines.append("")
            for i, deadline in enumerate(deadlines, 1):
                lines.append(f"{i}. **[Section {deadline.get('section_id', 'N/A')}]** {deadline.get('text', '')}")
            lines.append("")
        
        if penalties:
            lines.append("---")
            lines.append("")
            lines.append("## All Penalties")
            lines.append("")
            for i, penalty in enumerate(penalties, 1):
                lines.append(f"{i}. **[Section {penalty.get('section_id', 'N/A')}]** {penalty.get('text', '')}")
            lines.append("")
        
        if cross_refs:
            lines.append("---")
            lines.append("")
            lines.append("## Cross-References")
            lines.append("")
            for ref in cross_refs:
                lines.append(f"- **[Section {ref.get('section_id', 'N/A')}]** → {ref.get('reference', '')}")
            lines.append("")
        
        if cases:
            lines.append("---")
            lines.append("")
            lines.append("## Relevant Case Law")
            lines.append("")
            for case in cases:
                lines.append(f"- **[Section {case.get('section_id', 'N/A')}]** {case.get('citation', '')}")
            lines.append("")
