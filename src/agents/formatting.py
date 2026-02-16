"""
Formatting Agent - Compiles everything into a structured Markdown report.
"""
from typing import Dict, Any
from datetime import datetime
from .base import BaseAgent, AgentResult


class FormattingAgent(BaseAgent):
    """
    Agent that compiles all analysis results into a structured Markdown report.
    Creates a comprehensive, well-formatted legal analysis document.
    """
    
    def __init__(self):
        super().__init__("FormattingAgent")
    
    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Format all research results into a Markdown report.
        
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
            
            # Generate the Markdown report
            markdown_report = self._generate_report(sections, validation, summary)
            
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
    
    def _generate_report(
        self,
        sections: list,
        validation: Dict[str, Any],
        summary: Dict[str, Any]
    ) -> str:
        """Generate a comprehensive Markdown report."""
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
            lines.append(f"**Jurisdiction:** {validation.get('jurisdiction_identified', 'Unknown')}")
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
        
        # Obligations Summary
        obligations = []
        deadlines = []
        penalties = []
        
        for section in sections:
            annotations = section.get("annotations", {})
            obligations.extend(annotations.get("obligations", []))
            deadlines.extend(annotations.get("deadlines", []))
            penalties.extend(annotations.get("penalties", []))
        
        if obligations:
            lines.append("---")
            lines.append("")
            lines.append("## All Obligations")
            lines.append("")
            for i, obligation in enumerate(obligations, 1):
                lines.append(f"{i}. **[Section {obligation['section_id']}]** {obligation['text']} *(Type: {obligation['type']})*")
            lines.append("")
        
        if deadlines:
            lines.append("---")
            lines.append("")
            lines.append("## All Deadlines")
            lines.append("")
            for i, deadline in enumerate(deadlines, 1):
                lines.append(f"{i}. **[Section {deadline['section_id']}]** {deadline['text']}")
            lines.append("")
        
        if penalties:
            lines.append("---")
            lines.append("")
            lines.append("## All Penalties")
            lines.append("")
            for i, penalty in enumerate(penalties, 1):
                lines.append(f"{i}. **[Section {penalty['section_id']}]** {penalty['text']}")
            lines.append("")
        
        # Cross-References
        all_cross_refs = []
        for section in sections:
            research = section.get("research", {})
            all_cross_refs.extend(research.get("cross_references", []))
        
        if all_cross_refs:
            lines.append("---")
            lines.append("")
            lines.append("## Cross-References")
            lines.append("")
            for ref in all_cross_refs:
                lines.append(f"- **[Section {ref['section_id']}]** → {ref['reference']}")
            lines.append("")
        
        # Case Law
        all_cases = []
        for section in sections:
            research = section.get("research", {})
            all_cases.extend(research.get("case_law", []))
        
        if all_cases:
            lines.append("---")
            lines.append("")
            lines.append("## Relevant Case Law")
            lines.append("")
            for case in all_cases:
                lines.append(f"- **[Section {case['section_id']}]** {case['citation']}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("*Report generated by LegalBot - Legal Document Analysis System*")
        
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
                lines.append(f"- {obligation['text']} *(Type: {obligation['type']})*")
            lines.append("")
        
        deadlines = annotations.get("deadlines", [])
        if deadlines:
            lines.append("**Deadlines:**")
            for deadline in deadlines:
                lines.append(f"- {deadline['text']}")
            lines.append("")
        
        penalties = annotations.get("penalties", [])
        if penalties:
            lines.append("**Penalties:**")
            for penalty in penalties:
                lines.append(f"- {penalty['text']}")
            lines.append("")
        
        # Research findings
        research = section.get("research", {})
        
        related_topics = research.get("related_topics", [])
        if related_topics:
            lines.append(f"**Related Topics:** {', '.join(related_topics)}")
            lines.append("")
        
        return lines
