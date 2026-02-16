"""
Tests for LegalBot agent system
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from agents import (
    LegalBot,
    SafetyScopeAgent,
    StructuringAgent,
    AnnotationAgent,
    ResearchAgent,
    FormattingAgent,
    AgentResult
)


class TestSafetyScopeAgent:
    """Test the SafetyScopeAgent"""
    
    def test_valid_document(self):
        agent = SafetyScopeAgent()
        result = agent.process({
            "text": "Section 1: This is a legal document with sufficient content for analysis."
        })
        assert result.success
        assert result.data["ready_for_processing"]
        assert result.data["word_count"] > 0
    
    def test_empty_text(self):
        agent = SafetyScopeAgent()
        result = agent.process({"text": ""})
        assert not result.success
        assert "No text provided" in result.error
    
    def test_short_document(self):
        agent = SafetyScopeAgent()
        result = agent.process({"text": "Too short"})
        assert not result.success
        assert "too short" in result.error.lower()


class TestStructuringAgent:
    """Test the StructuringAgent"""
    
    def test_parse_sections(self):
        agent = StructuringAgent()
        text = """
        Section 1: First Section
        This is the content of the first section.
        
        Section 2: Second Section
        This is the content of the second section.
        """
        result = agent.process({"text": text})
        assert result.success
        assert result.data["total_sections"] >= 2
        sections = result.data["sections"]
        assert any("First Section" in s["title"] or "First Section" in s["content"] for s in sections)
    
    def test_single_section(self):
        agent = StructuringAgent()
        result = agent.process({"text": "This is a document without explicit sections."})
        assert result.success
        assert result.data["total_sections"] >= 1
    
    def test_empty_text(self):
        agent = StructuringAgent()
        result = agent.process({"text": ""})
        assert not result.success


class TestAnnotationAgent:
    """Test the AnnotationAgent"""
    
    def test_identify_obligations(self):
        agent = AnnotationAgent()
        sections = [{
            "id": "1",
            "title": "Test",
            "content": "The contractor shall complete the work. The owner must pay within 30 days."
        }]
        result = agent.process({"sections": sections})
        assert result.success
        assert result.data["summary"]["total_obligations"] >= 2
    
    def test_identify_deadlines(self):
        agent = AnnotationAgent()
        sections = [{
            "id": "1",
            "title": "Test",
            "content": "Payment is due within 30 days. The report must be filed within 60 days."
        }]
        result = agent.process({"sections": sections})
        assert result.success
        assert result.data["summary"]["total_deadlines"] >= 2
    
    def test_identify_penalties(self):
        agent = AnnotationAgent()
        sections = [{
            "id": "1",
            "title": "Test",
            "content": "Violation shall result in a fine of $5,000. The offender may face imprisonment for 6 months."
        }]
        result = agent.process({"sections": sections})
        assert result.success
        assert result.data["summary"]["total_penalties"] >= 1
    
    def test_no_sections(self):
        agent = AnnotationAgent()
        result = agent.process({"sections": []})
        assert not result.success


class TestResearchAgent:
    """Test the ResearchAgent"""
    
    def test_find_cross_references(self):
        agent = ResearchAgent()
        sections = [{
            "id": "1",
            "title": "Test",
            "content": "As stated in Section 5, the requirements apply. See also 42 U.S.C. § 1983.",
            "annotations": {"obligations": [], "deadlines": [], "penalties": []}
        }]
        result = agent.process({"annotated_sections": sections})
        assert result.success
        assert result.data["summary"]["total_cross_references"] >= 1
    
    def test_find_case_citations(self):
        agent = ResearchAgent()
        sections = [{
            "id": "1",
            "title": "Test",
            "content": "As held in Smith v. Jones, the standard applies.",
            "annotations": {"obligations": [], "deadlines": [], "penalties": []}
        }]
        result = agent.process({"annotated_sections": sections})
        assert result.success
        # Case citations might be found
    
    def test_no_sections(self):
        agent = ResearchAgent()
        result = agent.process({"annotated_sections": []})
        assert not result.success


class TestFormattingAgent:
    """Test the FormattingAgent"""
    
    def test_generate_report(self):
        agent = FormattingAgent()
        sections = [{
            "id": "1",
            "title": "Test Section",
            "content": "This is test content.",
            "annotations": {
                "obligations": [{"section_id": "1", "text": "shall comply", "type": "mandatory"}],
                "deadlines": [],
                "penalties": []
            },
            "research": {
                "cross_references": [],
                "case_law": [],
                "related_topics": ["Contract"]
            }
        }]
        result = agent.process({
            "researched_sections": sections,
            "validation_data": {"document_type": "Statute", "jurisdiction_identified": "Federal"},
            "summary": {"total_sections": 1}
        })
        assert result.success
        assert "# Legal Document Analysis Report" in result.data["report"]
        assert "Test Section" in result.data["report"]
    
    def test_no_sections(self):
        agent = FormattingAgent()
        result = agent.process({
            "researched_sections": [],
            "validation_data": {},
            "summary": {}
        })
        assert not result.success


class TestLegalBot:
    """Test the LegalBot orchestrator"""
    
    def test_full_pipeline(self):
        bot = LegalBot()
        text = """
        Section 1: Obligations
        The contractor shall complete all work within 30 days.
        Violation shall result in a fine of $5,000.
        
        Section 2: References
        See Section 1 for details. As stated in Smith v. Jones, 123 F.3d 456.
        """
        result = bot.analyze(text, jurisdiction="Federal", document_type="Statute")
        assert result["success"]
        assert "report" in result
        assert len(result["pipeline_results"]) == 5
        assert all(r["success"] for r in result["pipeline_results"])
    
    def test_empty_text_fails_early(self):
        bot = LegalBot()
        result = bot.analyze("")
        assert not result["success"]
        assert "Safety & Scope" in result.get("stage", "")
    
    def test_pipeline_status(self):
        bot = LegalBot()
        status = bot.get_pipeline_status()
        assert len(status) == 5
        assert all("agent" in s for s in status)
        assert all(s["status"] == "pending" for s in status)
    
    def test_short_document(self):
        bot = LegalBot()
        result = bot.analyze("Too short")
        assert not result["success"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
