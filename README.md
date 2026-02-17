# Legal Document Annotation System

<<<<<<< Updated upstream
A comprehensive system for annotating legal documents using a structured schema with 11 main categories and their subtypes.

## Features

- **Comprehensive Schema**: 11 main annotation categories covering all aspects of legal documents
- **LLM Integration**: Support for multiple LLM providers (OpenAI, Mock for testing)
- **Rule-Based Fallback**: Pattern matching for reliable annotation
- **Extensible Architecture**: Easy to add new categories or subtypes
=======
LegalBot is an orchestrator agent that manages a pipeline of specialized sub-agents to analyze statutes, codes, and case law. It provides comprehensive legal document analysis following a strict 5-step workflow, with Dutch-law support for sources published on wetten.overheid.nl.

## Features

- **Multi-Agent Pipeline**: Coordinates 5 specialized agents for comprehensive analysis
- **Structured Analysis**: Breaks down complex legal documents into manageable sections
- **Obligation Detection**: Identifies mandatory and permissive obligations
- **Deadline Tracking**: Extracts time-sensitive requirements
- **Penalty Identification**: Highlights consequences of non-compliance
- **Cross-Reference Detection**: Finds references to other legal materials
- **Case Law Citation**: Identifies relevant case citations (including ECLI)
- **Dutch-Law Support**: Detects Dutch legal structure and terminology (Artikel, Hoofdstuk, Besluit, Wet)
- **Source URL Ingestion**: Can fetch legal text directly from wetten.overheid.nl URLs
- **Markdown Reports**: Generates professional, structured analysis reports
>>>>>>> Stashed changes

## Annotation Categories

<<<<<<< Updated upstream
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
=======
LegalBot follows a strict 5-step workflow:

1. **Safety & Scope Agent**: Validates jurisdiction and legal context
   - Checks document validity
   - Identifies jurisdiction
   - Classifies document type
   - Screens for sensitive information

2. **Structuring Agent**: Breaks raw text into discrete articles/sections
   - Parses section markers
   - Identifies preambles
   - Structures hierarchical content

3. **Annotation Agent**: Identifies obligations, deadlines, and penalties
   - Extracts mandatory obligations (shall, must)
   - Extracts permissive obligations (may)
   - Identifies time requirements and deadlines
   - Detects penalties and consequences

4. **Research Agent**: Finds cross-references and relevant case law
   - Identifies internal cross-references
   - Finds statutory citations (Dutch and international patterns)
   - Extracts case law citations (including ECLI)
   - Identifies related legal topics

5. **Formatting Agent**: Compiles everything into a structured Markdown report
   - Generates executive summary
   - Creates detailed section analysis
   - Aggregates obligations, deadlines, and penalties
   - Lists cross-references and case law
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
# Annotate legal text
legal_text = "The Tenant shall pay rent of $1,500 by the 1st of each month."
result = agent.execute({'text': legal_text})
=======
# Analyze a legal document
result = bot.analyze(
    text=your_legal_text,
   jurisdiction="Nederland",  # optional
   document_type="Wet"  # optional
)
>>>>>>> Stashed changes

if result.success:
    annotations = result.data['annotations']
    for ann in annotations:
        print(f"{ann['category']}/{ann['subtype']}: {ann['text']}")
```

<<<<<<< Updated upstream
### Using the Schema
=======
### Analyze Directly from wetten.overheid.nl

```python
from agents import LegalBot

bot = LegalBot()
result = bot.analyze(
   text="",  # leave empty when using source_url
   source_url="https://wetten.overheid.nl/BWBV0001506/2013-07-01",
   jurisdiction="Nederland",
   document_type="Wet"
)
```

### Running the Example
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
### With OpenAI
=======
This will analyze a sample Dutch legal text and generate a detailed report saved as `legal_analysis_report.md`.
>>>>>>> Stashed changes

```python
from src.agents import AnnotationAgent, create_llm_client

<<<<<<< Updated upstream
# Create OpenAI client (requires API key)
client = create_llm_client('openai', api_key='your-api-key', model='gpt-4')
agent = AnnotationAgent(llm_client=client)

# Use the same way as above
result = agent.execute({'text': legal_text})
=======
```txt
agents/
├── src/
│   └── agents/
│       ├── __init__.py          # Package exports
│       ├── base.py              # Base classes (BaseAgent, AgentResult)
│       ├── legalbot.py          # Main orchestrator
│       ├── safety_scope.py      # Step 1: Safety & Scope Agent
│       ├── structuring.py       # Step 2: Structuring Agent
│       ├── annotation.py        # Step 3: Annotation Agent
│       ├── research.py          # Step 4: Research Agent
│       └── formatting.py        # Step 5: Formatting Agent
├── examples/
│   └── analyze_statute.py       # Example usage
├── tests/
│   └── test_legalbot.py         # Unit and integration tests
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project metadata
└── README.md                   # This file
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
=======
**Methods:**

- `analyze(text, jurisdiction=None, document_type=None)` - Analyze a legal document
- `get_pipeline_status()` - Get the current status of the pipeline

### Individual Agents

Each agent can be used independently:

```python
from agents import SafetyScopeAgent, StructuringAgent, AnnotationAgent

# Use individual agents
safety_agent = SafetyScopeAgent()
result = safety_agent.process({"text": legal_text})
>>>>>>> Stashed changes
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
