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


class DummyResponse:
    def __init__(self, content: str):
        self._content = content.encode("utf-8")
        self.headers = {"Content-Type": "text/html; charset=utf-8"}

    def read(self):
        return self._content

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TestSafetyScopeAgent:
    """Test the SafetyScopeAgent"""
    
    def test_valid_document(self):
        agent = SafetyScopeAgent()
        result = agent.process({
            "text": "Artikel 1. Dit is een juridische tekst met voldoende inhoud voor analyse."
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

    def test_detect_dutch_jurisdiction(self):
        agent = SafetyScopeAgent()
        result = agent.process({
            "text": "Artikel 2 van de Wet bepaalt dat de minister een vergunning kan verlenen."
        })
        assert result.success
        assert result.data["jurisdiction_identified"] == "Nederland"


class TestStructuringAgent:
    """Test the StructuringAgent"""
    
    def test_parse_sections(self):
        agent = StructuringAgent()
        text = """
        Artikel 1: Begripsbepalingen
        Dit is de inhoud van het eerste artikel.
        
        Artikel 2: Verplichtingen
        Dit is de inhoud van het tweede artikel.
        """
        result = agent.process({"text": text})
        assert result.success
        assert result.data["total_sections"] >= 2
        sections = result.data["sections"]
        assert any("Begripsbepalingen" in s["title"] or "Begripsbepalingen" in s["content"] for s in sections)
    
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
            "content": "De aanvrager moet de gegevens verstrekken. Het bestuursorgaan mag nadere regels stellen."
        }]
        result = agent.process({"sections": sections})
        assert result.success
        assert result.data["summary"]["total_obligations"] >= 2
    
    def test_identify_deadlines(self):
        agent = AnnotationAgent()
        sections = [{
            "id": "1",
            "title": "Test",
            "content": "Het bezwaar moet binnen 6 weken worden ingediend. Uiterlijk 1 januari wordt beslist."
        }]
        result = agent.process({"sections": sections})
        assert result.success
        assert result.data["summary"]["total_deadlines"] >= 2
    
    def test_identify_penalties(self):
        agent = AnnotationAgent()
        sections = [{
            "id": "1",
            "title": "Test",
            "content": "Overtreding kan leiden tot een bestuurlijke boete. Bij recidive volgt gevangenisstraf."
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
            "content": "Zoals bepaald in Artikel 5 zijn de eisen van toepassing. Zie ook BWBV0001506.",
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
            "content": "Zie ECLI:NL:HR:2020:1234 voor de uitleg van deze norm.",
            "annotations": {"obligations": [], "deadlines": [], "penalties": []}
        }]
        result = agent.process({"annotated_sections": sections})
        assert result.success
        assert result.data["summary"]["total_case_citations"] >= 1
    
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
            "validation_data": {"document_type": "Wet", "jurisdiction_identified": "Nederland"},
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
        Artikel 1: Verplichtingen
        De aanvrager moet de aanvraag binnen 6 weken indienen.
        Overtreding leidt tot een bestuurlijke boete.
        
        Artikel 2: Verwijzingen
        Zie Artikel 1 voor details. Zie ook ECLI:NL:HR:2020:1234.
        """
        result = bot.analyze(text, jurisdiction="Nederland", document_type="Wet")
        assert result["success"]
        assert "report" in result
        assert len(result["pipeline_results"]) == 5
        assert all(r["success"] for r in result["pipeline_results"])

    def test_url_pipeline_with_mocked_source(self, monkeypatch):
        from agents import legalbot as legalbot_module

        html = """
        <html><body>
            <h1>Wet voorbeeld</h1>
            <p>Artikel 1. De aanvrager moet binnen 6 weken reageren.</p>
            <p>Artikel 2. Overtreding leidt tot een bestuurlijke boete. Zie ECLI:NL:HR:2020:1234.</p>
        </body></html>
        """

        monkeypatch.setattr(legalbot_module, "urlopen", lambda *args, **kwargs: DummyResponse(html))

        bot = LegalBot()
        result = bot.analyze(
            text="",
            source_url="https://wetten.overheid.nl/BWBV0001506/2013-07-01",
            jurisdiction="Nederland",
            document_type="Wet"
        )

        assert result["success"]
        assert result.get("source_url") == "https://wetten.overheid.nl/BWBV0001506/2013-07-01"
        assert result["summary"]["total_sections"] >= 1
    
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
