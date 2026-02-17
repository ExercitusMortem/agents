"""
Tests for Legal Document Annotation System
"""

import pytest
import json
from src.agents.schema import AnnotationSchema, AnnotationCategory, AnnotationSubtype
from src.agents.base import BaseAgent, AgentResult
from src.agents.llm_client import MockLLMClient, create_llm_client
from src.agents.annotation import AnnotationAgent


class TestAnnotationSchema:
    """Tests for AnnotationSchema class."""
    
    def test_schema_initialization(self):
        """Test that schema initializes with all 11 categories."""
        schema = AnnotationSchema()
        
        expected_categories = [
            'PARTIES', 'OBLIGATION', 'RIGHTS', 'DEADLINE', 'CONDITION',
            'DEFINITION', 'PENALTY', 'PROCEDURE', 'REFERENCE', 'MONEY', 'TIME'
        ]
        
        assert len(schema.categories) == 11
        for cat in expected_categories:
            assert cat in schema.categories
    
    def test_get_category(self):
        """Test getting a category by label."""
        schema = AnnotationSchema()
        
        parties = schema.get_category('PARTIES')
        assert isinstance(parties, AnnotationCategory)
        assert parties.label == 'PARTIES'
        assert parties.description == 'Entities involved in the legal text'
    
    def test_get_subtype(self):
        """Test getting a subtype from a category."""
        schema = AnnotationSchema()
        
        person = schema.get_subtype('PARTIES', 'PERSON')
        assert isinstance(person, AnnotationSubtype)
        assert person.name == 'PERSON'
        assert person.description == 'Individual mentioned'
    
    def test_get_all_categories(self):
        """Test getting list of all category labels."""
        schema = AnnotationSchema()
        categories = schema.get_all_categories()
        
        assert len(categories) == 11
        assert 'PARTIES' in categories
        assert 'OBLIGATION' in categories
    
    def test_get_category_subtypes(self):
        """Test getting subtypes for a category."""
        schema = AnnotationSchema()
        
        obligation_subtypes = schema.get_category_subtypes('OBLIGATION')
        assert len(obligation_subtypes) == 3
        assert 'AFFIRMATIVE' in obligation_subtypes
        assert 'PROHIBITIVE' in obligation_subtypes
        assert 'PERMISSIVE' in obligation_subtypes
    
    def test_parties_category(self):
        """Test PARTIES category structure."""
        schema = AnnotationSchema()
        parties = schema.get_category('PARTIES')
        
        assert len(parties.subtypes) == 3
        assert 'PERSON' in parties.subtypes
        assert 'ORGANIZATION' in parties.subtypes
        assert 'ROLE' in parties.subtypes
    
    def test_obligation_category(self):
        """Test OBLIGATION category structure."""
        schema = AnnotationSchema()
        obligation = schema.get_category('OBLIGATION')
        
        assert len(obligation.subtypes) == 3
        assert 'AFFIRMATIVE' in obligation.subtypes
        assert 'PROHIBITIVE' in obligation.subtypes
        assert 'PERMISSIVE' in obligation.subtypes
    
    def test_rights_category(self):
        """Test RIGHTS category structure."""
        schema = AnnotationSchema()
        rights = schema.get_category('RIGHTS')
        
        assert len(rights.subtypes) == 3
        assert 'FINANCIAL' in rights.subtypes
        assert 'ACCESS' in rights.subtypes
        assert 'LEGAL' in rights.subtypes
    
    def test_deadline_category(self):
        """Test DEADLINE category structure."""
        schema = AnnotationSchema()
        deadline = schema.get_category('DEADLINE')
        
        assert len(deadline.subtypes) == 3
        assert 'ABSOLUTE' in deadline.subtypes
        assert 'RELATIVE' in deadline.subtypes
        assert 'RECURRENT' in deadline.subtypes
    
    def test_condition_category(self):
        """Test CONDITION category structure."""
        schema = AnnotationSchema()
        condition = schema.get_category('CONDITION')
        
        assert len(condition.subtypes) == 3
        assert 'TRIGGER' in condition.subtypes
        assert 'EXEMPTION' in condition.subtypes
        assert 'PRECEDENT' in condition.subtypes
    
    def test_definition_category(self):
        """Test DEFINITION category structure."""
        schema = AnnotationSchema()
        definition = schema.get_category('DEFINITION')
        
        assert len(definition.subtypes) == 2
        assert 'TERM' in definition.subtypes
        assert 'SCOPE' in definition.subtypes
    
    def test_penalty_category(self):
        """Test PENALTY category structure."""
        schema = AnnotationSchema()
        penalty = schema.get_category('PENALTY')
        
        assert len(penalty.subtypes) == 3
        assert 'FINANCIAL' in penalty.subtypes
        assert 'LEGAL' in penalty.subtypes
        assert 'OPERATIONAL' in penalty.subtypes
    
    def test_procedure_category(self):
        """Test PROCEDURE category structure."""
        schema = AnnotationSchema()
        procedure = schema.get_category('PROCEDURE')
        
        assert len(procedure.subtypes) == 3
        assert 'FILING' in procedure.subtypes
        assert 'NOTIFICATION' in procedure.subtypes
        assert 'COMPLIANCE' in procedure.subtypes
    
    def test_reference_category(self):
        """Test REFERENCE category structure."""
        schema = AnnotationSchema()
        reference = schema.get_category('REFERENCE')
        
        assert len(reference.subtypes) == 3
        assert 'STATUTE' in reference.subtypes
        assert 'CASE' in reference.subtypes
        assert 'INTERNAL' in reference.subtypes
    
    def test_money_category(self):
        """Test MONEY category structure."""
        schema = AnnotationSchema()
        money = schema.get_category('MONEY')
        
        assert len(money.subtypes) == 3
        assert 'AMOUNT' in money.subtypes
        assert 'PERCENTAGE' in money.subtypes
        assert 'THRESHOLD' in money.subtypes
    
    def test_time_category(self):
        """Test TIME category structure."""
        schema = AnnotationSchema()
        time = schema.get_category('TIME')
        
        assert len(time.subtypes) == 2
        assert 'EVENT' in time.subtypes
        assert 'DURATION' in time.subtypes
    
    def test_to_dict(self):
        """Test converting schema to dictionary."""
        schema = AnnotationSchema()
        schema_dict = schema.to_dict()
        
        assert isinstance(schema_dict, dict)
        assert len(schema_dict) == 11
        assert 'PARTIES' in schema_dict
        assert 'description' in schema_dict['PARTIES']
        assert 'subtypes' in schema_dict['PARTIES']
    
    def test_annotation_guidelines(self):
        """Test getting annotation guidelines."""
        schema = AnnotationSchema()
        guidelines = schema.get_annotation_guidelines()
        
        assert isinstance(guidelines, str)
        assert 'Span-based tagging' in guidelines
        assert 'Hierarchical tagging' in guidelines
        assert 'Cross-linking' in guidelines


class TestBaseAgent:
    """Tests for BaseAgent class."""
    
    def test_agent_result_creation(self):
        """Test creating AgentResult."""
        result = AgentResult(success=True, data={'key': 'value'})
        
        assert result.success is True
        assert result.data == {'key': 'value'}
        assert result.error is None
        assert result.metadata == {}
    
    def test_agent_result_with_error(self):
        """Test AgentResult with error."""
        result = AgentResult(success=False, error='Test error')
        
        assert result.success is False
        assert result.error == 'Test error'
    
    def test_agent_result_with_metadata(self):
        """Test AgentResult with metadata."""
        result = AgentResult(
            success=True,
            data={'test': 'data'},
            metadata={'count': 5}
        )
        
        assert result.metadata == {'count': 5}


class TestMockLLMClient:
    """Tests for MockLLMClient."""
    
    def test_mock_client_creation(self):
        """Test creating mock LLM client."""
        client = MockLLMClient()
        assert client is not None
        assert client.call_count == 0
    
    def test_mock_generate(self):
        """Test generating text with mock client."""
        client = MockLLMClient()
        response = client.generate("Test prompt")
        
        assert isinstance(response, str)
        assert client.call_count == 1
    
    def test_mock_generate_json(self):
        """Test generating JSON with mock client."""
        client = MockLLMClient()
        response = client.generate_json("Test prompt")
        
        assert isinstance(response, dict)
        assert client.call_count == 1
    
    def test_mock_annotation_response(self):
        """Test mock annotation response."""
        client = MockLLMClient()
        response = client.generate_json(
            "Annotate this text",
            system_prompt="You are an annotation expert"
        )
        
        assert 'annotations' in response or 'response' in response


class TestAnnotationAgent:
    """Tests for AnnotationAgent."""
    
    def test_agent_creation(self):
        """Test creating annotation agent."""
        client = MockLLMClient()
        agent = AnnotationAgent(llm_client=client)
        
        assert agent is not None
        assert isinstance(agent.schema, AnnotationSchema)
    
    def test_validate_input(self):
        """Test input validation."""
        client = MockLLMClient()
        agent = AnnotationAgent(llm_client=client)
        
        # Valid input
        assert agent.validate_input({'text': 'test'}) is True
        
        # Invalid inputs
        assert agent.validate_input('not a dict') is False
        assert agent.validate_input({}) is False
        assert agent.validate_input({'wrong_key': 'value'}) is False
    
    def test_execute_with_valid_input(self):
        """Test executing annotation with valid input."""
        client = MockLLMClient()
        agent = AnnotationAgent(llm_client=client)
        
        result = agent.execute({
            'text': 'The contractor shall deliver the goods by 15th March.'
        })
        
        assert result.success is True
        assert 'text' in result.data
        assert 'annotations' in result.data
        assert 'schema_version' in result.data
    
    def test_execute_with_invalid_input(self):
        """Test executing annotation with invalid input."""
        client = MockLLMClient()
        agent = AnnotationAgent(llm_client=client)
        
        result = agent.execute('not a dict')
        
        assert result.success is False
        assert result.error is not None
    
    def test_execute_with_empty_text(self):
        """Test executing annotation with empty text."""
        client = MockLLMClient()
        agent = AnnotationAgent(llm_client=client)
        
        result = agent.execute({'text': ''})
        
        assert result.success is False
        assert 'empty' in result.error.lower()
    
    def test_rule_based_annotation_obligation(self):
        """Test rule-based annotation for obligations."""
        client = MockLLMClient()
        agent = AnnotationAgent(llm_client=client)
        
        text = "The contractor shall deliver the goods by March 15th."
        annotations = agent._rule_based_annotation(text)
        
        # Should find OBLIGATION and DEADLINE
        assert len(annotations) > 0
        
        # Check for obligation
        obligations = [a for a in annotations if a['category'] == 'OBLIGATION']
        assert len(obligations) > 0
    
    def test_rule_based_annotation_money(self):
        """Test rule-based annotation for money."""
        client = MockLLMClient()
        agent = AnnotationAgent(llm_client=client)
        
        text = "The fee is $10,000 with a 5% late charge."
        annotations = agent._rule_based_annotation(text)
        
        # Should find MONEY annotations
        money = [a for a in annotations if a['category'] == 'MONEY']
        assert len(money) >= 2  # Amount and percentage
    
    def test_rule_based_annotation_parties(self):
        """Test rule-based annotation for parties."""
        client = MockLLMClient()
        agent = AnnotationAgent(llm_client=client)
        
        text = "The Tenant and Landlord agree to the terms."
        annotations = agent._rule_based_annotation(text)
        
        # Should find PARTIES
        parties = [a for a in annotations if a['category'] == 'PARTIES']
        assert len(parties) >= 2
    
    def test_get_annotations_by_category(self):
        """Test filtering annotations by category."""
        client = MockLLMClient()
        agent = AnnotationAgent(llm_client=client)
        
        annotations = [
            {'category': 'OBLIGATION', 'subtype': 'AFFIRMATIVE', 'text': 'shall'},
            {'category': 'MONEY', 'subtype': 'AMOUNT', 'text': '$100'},
            {'category': 'OBLIGATION', 'subtype': 'PROHIBITIVE', 'text': 'shall not'}
        ]
        
        obligations = agent.get_annotations_by_category(annotations, 'OBLIGATION')
        assert len(obligations) == 2
        
        money = agent.get_annotations_by_category(annotations, 'MONEY')
        assert len(money) == 1
    
    def test_get_annotations_by_subtype(self):
        """Test filtering annotations by subtype."""
        client = MockLLMClient()
        agent = AnnotationAgent(llm_client=client)
        
        annotations = [
            {'category': 'OBLIGATION', 'subtype': 'AFFIRMATIVE', 'text': 'shall'},
            {'category': 'OBLIGATION', 'subtype': 'PROHIBITIVE', 'text': 'shall not'}
        ]
        
        affirmative = agent.get_annotations_by_subtype(
            annotations, 'OBLIGATION', 'AFFIRMATIVE'
        )
        assert len(affirmative) == 1
        assert affirmative[0]['subtype'] == 'AFFIRMATIVE'
    
    def test_annotation_with_complex_text(self):
        """Test annotation with complex legal text."""
        client = MockLLMClient()
        agent = AnnotationAgent(llm_client=client)
        
        text = """
        The Tenant shall pay rent of $1,500 by the 1st of each month.
        The Tenant shall not sublease without written consent.
        Late payment will incur a $50 fee per day.
        As per Section 12 of the Lease Agreement, the Landlord may 
        inspect the premises with 24-hour notice.
        """
        
        result = agent.execute({'text': text})
        
        assert result.success is True
        assert len(result.data['annotations']) > 0
        
        # Should have metadata
        assert 'annotation_count' in result.metadata
        assert 'categories_used' in result.metadata


class TestLLMClientFactory:
    """Tests for LLM client factory."""
    
    def test_create_mock_client(self):
        """Test creating mock client via factory."""
        client = create_llm_client('mock')
        assert isinstance(client, MockLLMClient)
    
    def test_create_invalid_provider(self):
        """Test creating client with invalid provider."""
        with pytest.raises(ValueError):
            create_llm_client('invalid_provider')


def test_end_to_end_annotation():
    """End-to-end test of the annotation system."""
    # Create client and agent
    client = MockLLMClient()
    agent = AnnotationAgent(llm_client=client)
    
    # Sample legal text
    legal_text = """
    Article 1: Payment Terms
    
    The Buyer shall pay the Seller $50,000 within 30 days of delivery.
    Late payment will incur a penalty of 5% per month.
    
    Article 2: Obligations
    
    The Seller must deliver the goods by March 31st, 2026.
    The Buyer may inspect the goods upon delivery.
    Neither party shall disclose confidential information.
    
    Article 3: References
    
    This agreement is governed by Section 12 of the Commercial Act 2020.
    See Clause 4.2 for dispute resolution procedures.
    """
    
    # Execute annotation
    result = agent.execute({'text': legal_text})
    
    # Verify result
    assert result.success is True
    assert 'annotations' in result.data
    assert len(result.data['annotations']) > 0
    
    # Verify schema version
    assert result.data['schema_version'] == '1.0'
    
    # Verify metadata
    assert result.metadata['annotation_count'] > 0
    assert len(result.metadata['categories_used']) > 0
    
    # Get schema information
    schema = agent.schema
    assert len(schema.get_all_categories()) == 11
