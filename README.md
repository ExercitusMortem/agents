# LegalBot - Legal Document Analysis Agent System

LegalBot is an orchestrator agent that manages a pipeline of specialized sub-agents to analyze statutes, codes, and case law. It provides comprehensive legal document analysis following a strict 5-step workflow.

## Features

- **Multi-Agent Pipeline**: Coordinates 5 specialized agents for comprehensive analysis
- **Structured Analysis**: Breaks down complex legal documents into manageable sections
- **Obligation Detection**: Identifies mandatory and permissive obligations
- **Deadline Tracking**: Extracts time-sensitive requirements
- **Penalty Identification**: Highlights consequences of non-compliance
- **Cross-Reference Detection**: Finds references to other legal materials
- **Case Law Citation**: Identifies relevant case citations
- **Markdown Reports**: Generates professional, structured analysis reports

## Pipeline Workflow

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
   - Finds statutory citations (U.S.C., C.F.R.)
   - Extracts case law citations
   - Identifies related legal topics

5. **Formatting Agent**: Compiles everything into a structured Markdown report
   - Generates executive summary
   - Creates detailed section analysis
   - Aggregates obligations, deadlines, and penalties
   - Lists cross-references and case law

## Installation

```bash
# Clone the repository
git clone https://github.com/ExercitusMortem/agents.git
cd agents

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from agents import LegalBot

# Initialize LegalBot
bot = LegalBot()

# Analyze a legal document
result = bot.analyze(
    text=your_legal_text,
    jurisdiction="Federal",  # optional
    document_type="Statute"  # optional
)

# Check if analysis was successful
if result["success"]:
    # Access the Markdown report
    report = result["report"]
    
    # Access summary statistics
    summary = result["summary"]
    print(f"Sections: {summary['total_sections']}")
    print(f"Obligations: {summary['total_obligations']}")
    
    # Save the report
    with open("analysis.md", "w") as f:
        f.write(report)
else:
    print(f"Analysis failed: {result['error']}")
```

### Running the Example

```bash
python examples/analyze_statute.py
```

This will analyze a sample statute and generate a detailed report saved as `legal_analysis_report.md`.

## Project Structure

```
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
```

## Testing

Run the test suite:

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/agents --cov-report=html
```

## API Reference

### LegalBot

Main orchestrator class that manages the analysis pipeline.

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
```

## Output Format

The analysis produces a comprehensive Markdown report with:

- **Executive Summary**: Document metadata and statistics
- **Detailed Analysis**: Section-by-section breakdown with annotations
- **All Obligations**: Aggregated list of all identified obligations
- **All Deadlines**: Aggregated list of all time requirements
- **All Penalties**: Aggregated list of all penalties and consequences
- **Cross-References**: Links to other legal materials
- **Relevant Case Law**: List of cited cases

## Requirements

- Python 3.9+
- pydantic >= 2.0.0

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Acknowledgments

LegalBot uses a modular agent architecture for legal document analysis, making it easy to extend and customize for specific legal domains.
