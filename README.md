# Legal Document Annotation System

A comprehensive system for annotating legal documents using a structured schema with 11 main categories and their subtypes.

## Features

- **Comprehensive Schema**: 11 main annotation categories covering all aspects of legal documents
- **LLM Integration**: Support for multiple LLM providers (OpenAI, Mock for testing)
- **Rule-Based Fallback**: Pattern matching for reliable annotation
- **Extensible Architecture**: Easy to add new categories or subtypes

## Annotation Categories

1. **PARTIES** - Entities involved (Person, Organization, Role)
2. **OBLIGATION** - Duties and requirements (Affirmative, Prohibitive, Permissive)
3. **RIGHTS** - Entitlements (Financial, Access, Legal)
4. **DEADLINE** - Timeframes (Absolute, Relative, Recurrent)
5. **CONDITION** - Triggers and contingencies (Trigger, Exemption, Precedent)
6. **DEFINITION** - Defined terms (Term, Scope)
7. **PENALTY** - Sanctions (Financial, Legal, Operational)
8. **PROCEDURE** - Processes (Filing, Notification, Compliance)
9. **REFERENCE** - Citations (Statute, Case, Internal)
10. **MONEY** - Financial data (Amount, Percentage, Threshold)
11. **TIME** - Temporal references (Event, Duration)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Annotation

```python
from src.agents import AnnotationAgent, MockLLMClient

# Create LLM client and agent
client = MockLLMClient()
agent = AnnotationAgent(llm_client=client)

# Annotate legal text
legal_text = "The Tenant shall pay rent of $1,500 by the 1st of each month."
result = agent.execute({'text': legal_text})

if result.success:
    annotations = result.data['annotations']
    for ann in annotations:
        print(f"{ann['category']}/{ann['subtype']}: {ann['text']}")
```

### Using the Schema

```python
from src.agents import AnnotationSchema

# Load schema
schema = AnnotationSchema()

# Get all categories
categories = schema.get_all_categories()
print(f"Categories: {categories}")

# Get category information
obligation = schema.get_category('OBLIGATION')
print(f"Description: {obligation.description}")

# Get subtypes
subtypes = schema.get_category_subtypes('OBLIGATION')
print(f"Subtypes: {subtypes}")

# Get annotation guidelines
guidelines = schema.get_annotation_guidelines()
print(guidelines)
```

### With OpenAI

```python
from src.agents import AnnotationAgent, create_llm_client

# Create OpenAI client (requires API key)
client = create_llm_client('openai', api_key='your-api-key', model='gpt-4')
agent = AnnotationAgent(llm_client=client)

# Use the same way as above
result = agent.execute({'text': legal_text})
```

## Testing

Run the test suite:

```bash
pytest tests/
```

## Annotation Guidelines

- **Span-based tagging**: Highlight exact words or phrases
- **Hierarchical tagging**: Subtypes nested under main labels
- **Cross-linking**: Connect related annotations (OBLIGATION → DEADLINE → PENALTY)
- **Granularity**: Annotate each element separately
- **Consistency**: Use uniform label names across the dataset

## Project Structure

```
├── src/
│   └── agents/
│       ├── __init__.py
│       ├── schema.py          # Annotation schema definition
│       ├── base.py            # Base agent infrastructure
│       ├── llm_client.py      # LLM client abstraction
│       └── annotation.py      # Annotation agent
├── tests/
│   └── test_annotation_system.py
├── requirements.txt
└── README.md
```

## License

MIT
