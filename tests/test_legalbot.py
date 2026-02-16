"""
Tests for LegalBot LLM-powered agent system
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Force mock LLM for testing
os.environ['LLM_PROVIDER'] = 'mock'

import pytest
from agents import (
    LegalBot,
    SafetyScopeAgent,
    StructuringAgent,
    AnnotationAgent,
    ResearchAgent,
    FormattingAgent,
    AgentResult,
    MockLLMClient
)


class TestMockLLMClient:
    """Test the MockLLMClient"""
    
    def test_mock_client_creation(self):
        client = MockLLMClient()
        assert client is not None
        assert client.call_count == 0
    
    def test_mock_client_chat(self):
        client = MockLLMClient()
        response = client.chat("You are a test agent", "Test message")
        assert response.content is not None
        assert client.call_count == 1


class TestSafetyScopeAgent:
    """Test the SafetyScopeAgent with LLM"""
    
    def test_valid_document(self):
        agent = SafetyScopeAgent(MockLLMClient())
        result = agent.process({
            "text": "Section 1: This is a legal document with sufficient content for analysis."
        })
        assert result.success
        assert "jurisdiction" in result.data or "jurisdiction_identified" in result.data
        assert result.data.get("word_count", 0) > 0
    
    def test_empty_text(self):
        agent = SafetyScopeAgent(MockLLMClient())
        result = agent.process({"text": ""})
        assert not result.success
        assert "No text provided" in result.error
    
    def test_short_document(self):
        agent = SafetyScopeAgent(MockLLMClient())
        result = agent.process({"text": "Too short"})
        assert not result.success
        assert "too short" in result.error.lower()


class TestStructuringAgent:
    """Test the StructuringAgent with LLM"""
    
    def test_parse_sections(self):
        agent = StructuringAgent(MockLLMClient())
        text = """
        Section 1: First Section
        This is the content of the first section.
        
        Section 2: Second Section
        This is the content of the second section.
        """
        result = agent.process({"text": text})
        assert result.success
        assert result.data["total_sections"] >= 1
        sections = result.data["sections"]
        assert len(sections) >= 1
    
    def test_single_section(self):
        agent = StructuringAgent(MockLLMClient())
        result = agent.process({"text": "This is a document without explicit sections."})
        assert result.success
        assert result.data["total_sections"] >= 1
    
    def test_empty_text(self):
        agent = StructuringAgent(MockLLMClient())
        result = agent.process({"text": ""})
        assert not result.success


class TestAnnotationAgent:
    """Test the AnnotationAgent with LLM"""
    
    def test_annotate_sections(self):
        agent = AnnotationAgent(MockLLMClient())
        sections = [{
            "id": "1",
            "title": "Test",
            "content": "The contractor shall complete the work. The owner must pay within 30 days."
        }]
        result = agent.process({"sections": sections})
        assert result.success
        assert "annotated_sections" in result.data
        assert "summary" in result.data
    
    def test_no_sections(self):
        agent = AnnotationAgent(MockLLMClient())
        result = agent.process({"sections": []})
        assert not result.success


class TestResearchAgent:
    """Test the ResearchAgent with LLM"""
    
    def test_research_sections(self):
        agent = ResearchAgent(MockLLMClient())
        sections = [{
            "id": "1",
            "title": "Test",
            "content": "As stated in Section 5, the requirements apply. See also 42 U.S.C. § 1983.",
            "annotations": {"obligations": [], "deadlines": [], "penalties": []}
        }]
        result = agent.process({"annotated_sections": sections})
        assert result.success
        assert "researched_sections" in result.data
        assert "summary" in result.data
    
    def test_no_sections(self):
        agent = ResearchAgent(MockLLMClient())
        result = agent.process({"annotated_sections": []})
        assert not result.success


class TestFormattingAgent:
    """Test the FormattingAgent with LLM"""
    
    def test_generate_report(self):
        agent = FormattingAgent(MockLLMClient())
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
        assert "report" in result.data
        assert len(result.data["report"]) > 0
    
    def test_no_sections(self):
        agent = FormattingAgent(MockLLMClient())
        result = agent.process({
            "researched_sections": [],
            "validation_data": {},
            "summary": {}
        })
        assert not result.success


class TestLegalBot:
    """Test the LegalBot orchestrator with LLM"""
    
    def test_full_pipeline(self):
        bot = LegalBot(llm_provider="mock")
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
        assert result["llm_provider"] == "MockLLMClient"
    
    def test_empty_text_fails_early(self):
        bot = LegalBot(llm_provider="mock")
        result = bot.analyze("")
        assert not result["success"]
        assert "Safety & Scope" in result.get("stage", "")
    
    def test_pipeline_status(self):
        bot = LegalBot(llm_provider="mock")
        status = bot.get_pipeline_status()
        assert len(status) == 5
        assert all("agent" in s for s in status)
        assert all(s["status"] == "pending" for s in status)
    
    def test_short_document(self):
        bot = LegalBot(llm_provider="mock")
        result = bot.analyze("Too short")
        assert not result["success"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
