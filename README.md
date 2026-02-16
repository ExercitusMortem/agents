# LegalBot - LLM-Powered Legal Document Analysis Agent System

LegalBot is an orchestrator agent that manages a pipeline of specialized **LLM-powered sub-agents** to analyze statutes, codes, and case law. It provides comprehensive legal document analysis using Large Language Models, following a strict 5-step workflow.

## Key Features

- **🤖 LLM-Powered Agents**: Each agent uses AI/LLMs to intelligently understand and process legal text
- **Multi-Agent Pipeline**: Coordinates 5 specialized LLM agents for comprehensive analysis
- **Flexible LLM Support**: Works with OpenAI (GPT-4, etc.) or mock LLM for testing
- **Structured Analysis**: Breaks down complex legal documents into manageable sections
- **Intelligent Extraction**: AI-powered detection of obligations, deadlines, and penalties
- **Smart Research**: LLM-based identification of cross-references and case law
- **Professional Reports**: AI-generated Markdown analysis reports

## What Makes These "Real" LLM Agents?

Unlike rule-based pattern matching systems, LegalBot agents:

1. **Use Large Language Models**: Each agent makes actual API calls to LLMs (OpenAI GPT-4, etc.)
2. **Understand Context**: Agents use AI to understand legal context, not just keywords
3. **Generate Intelligent Responses**: Create structured JSON outputs based on understanding
4. **Adapt to Different Documents**: Work with various legal document formats without rigid rules
5. **Provide Reasoning**: LLMs can explain their analysis and confidence levels

## Pipeline Workflow

LegalBot follows a strict 5-step LLM-powered workflow:

1. **Safety & Scope Agent** (LLM-powered): 
   - Uses AI to validate jurisdiction and legal context
   - Intelligently classifies document types
   - Assesses readiness for analysis
   - Provides confidence ratings and reasoning

2. **Structuring Agent** (LLM-powered):
   - Uses AI to parse complex document structures
   - Identifies sections, articles, and subsections
   - Adapts to various formatting styles
   - Creates hierarchical content structure

3. **Annotation Agent** (LLM-powered):
   - AI identifies obligations (mandatory vs permissive)
   - Intelligently extracts time requirements and deadlines
   - Detects penalties and consequences
   - Understands legal language nuances

4. **Research Agent** (LLM-powered):
   - AI finds internal and external cross-references
   - Identifies statutory citations (U.S.C., C.F.R., etc.)
   - Extracts and validates case law citations
   - Determines relevance of related legal topics

5. **Formatting Agent** (LLM-powered):
   - AI generates comprehensive Markdown reports
   - Creates executive summaries
   - Organizes findings into readable sections
   - Produces professional legal analysis documents

## Installation

```bash
# Clone the repository
git clone https://github.com/ExercitusMortem/agents.git
cd agents

# Install dependencies
pip install -r requirements.txt

# Configure LLM provider (copy and edit .env.example)
cp .env.example .env
# Edit .env and set your API keys
```

## Configuration

Create a `.env` file with your LLM configuration:

```bash
# Choose your LLM provider
LLM_PROVIDER=openai  # Options: openai, mock

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4, gpt-3.5-turbo, etc.

# For testing without API keys, use:
LLM_PROVIDER=mock
```

## Usage

### Basic Example with OpenAI

```python
from agents import LegalBot

# Initialize LegalBot (reads from .env)
bot = LegalBot()

# Or specify provider explicitly
bot = LegalBot(llm_provider="openai")

# Analyze a legal document
result = bot.analyze(
    text=your_legal_text,
    jurisdiction="Federal",  # optional
    document_type="Statute"  # optional
)

# Check if analysis was successful
if result["success"]:
    # Access the AI-generated Markdown report
    report = result["report"]
    
    # Access summary statistics
    summary = result["summary"]
    print(f"Sections: {summary['total_sections']}")
    print(f"Obligations: {summary['total_obligations']}")
    
    # See which LLM was used
    print(f"LLM Provider: {result['llm_provider']}")
    
    # Save the report
    with open("analysis.md", "w") as f:
        f.write(report)
else:
    print(f"Analysis failed: {result['error']}")
```

### Testing Without API Keys (Mock LLM)

```python
from agents import LegalBot

# Use mock LLM for testing (no API key needed)
bot = LegalBot(llm_provider="mock")

result = bot.analyze(your_legal_text)
# Mock LLM generates simulated responses
```

### Running the Example

```bash
# With mock LLM (no API key needed)
export LLM_PROVIDER=mock
python examples/analyze_statute.py

# With OpenAI (requires API key in .env)
export LLM_PROVIDER=openai
python examples/analyze_statute.py
```

## Architecture

### LLM Integration Layer

```python
# LLM Client abstraction
from agents import create_llm_client, OpenAIClient, MockLLMClient

# Create a client
llm = create_llm_client("openai")  # or "mock"

# Use the client
response = llm.chat(
    system_prompt="You are a legal expert...",
    user_message="Analyze this document..."
)
```

### Individual LLM Agents

Each agent can be used independently with custom LLM clients:

```python
from agents import SafetyScopeAgent, OpenAIClient

# Create custom LLM client
llm = OpenAIClient(model="gpt-4")

# Use agent with custom LLM
safety_agent = SafetyScopeAgent(llm_client=llm)
result = safety_agent.process({"text": legal_text})
```

## Project Structure

```
agents/
├── src/
│   └── agents/
│       ├── __init__.py          # Package exports
│       ├── base.py              # Base classes (BaseAgent, AgentResult)
│       ├── llm_client.py        # LLM integration (OpenAI, Mock)
│       ├── legalbot.py          # Main orchestrator
│       ├── safety_scope.py      # Step 1: LLM-powered validation
│       ├── structuring.py       # Step 2: LLM-powered parsing
│       ├── annotation.py        # Step 3: LLM-powered annotation
│       ├── research.py          # Step 4: LLM-powered research
│       └── formatting.py        # Step 5: LLM-powered formatting
├── examples/
│   └── analyze_statute.py       # Example usage
├── tests/
│   └── test_legalbot.py         # Unit and integration tests
├── .env.example                 # Example configuration
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project metadata
└── README.md                   # This file
```

## Testing

Run the test suite:

```bash
# Install dev dependencies
pip install pytest

# Run tests with mock LLM (no API key needed)
export LLM_PROVIDER=mock
pytest tests/ -v

# Run specific test
pytest tests/test_legalbot.py::TestLegalBot::test_full_pipeline -v
```

## API Reference

### LegalBot

Main orchestrator class that manages the LLM-powered analysis pipeline.

**Constructor:**
```python
LegalBot(llm_provider: Optional[str] = None)
```
- `llm_provider`: "openai", "mock", or None (uses env var)

**Methods:**
- `analyze(text, jurisdiction=None, document_type=None)` - Analyze a legal document with LLMs
- `get_pipeline_status()` - Get the current status of the pipeline

**Returns:**
```python
{
    "success": bool,
    "report": str,                    # AI-generated Markdown report
    "validation": dict,               # AI validation results
    "sections": list,                 # AI-parsed sections
    "summary": dict,                  # AI-extracted statistics
    "pipeline_results": list,         # Per-agent results
    "llm_provider": str               # LLM client used
}
```

### LLM Clients

**OpenAIClient**: Production LLM client for OpenAI API
```python
from agents import OpenAIClient

llm = OpenAIClient(api_key="...", model="gpt-4o-mini")
response = llm.chat(system_prompt, user_message)
```

**MockLLMClient**: Testing LLM client (no API needed)
```python
from agents import MockLLMClient

llm = MockLLMClient()  # Generates contextual mock responses
response = llm.chat(system_prompt, user_message)
```

## Output Format

The LLM-powered analysis produces a comprehensive AI-generated Markdown report with:

- **Executive Summary**: AI-generated document metadata and statistics
- **Detailed Analysis**: AI-analyzed section-by-section breakdown
- **All Obligations**: AI-extracted list of all identified obligations
- **All Deadlines**: AI-extracted list of all time requirements
- **All Penalties**: AI-extracted list of all penalties and consequences
- **Cross-References**: AI-identified links to other legal materials
- **Relevant Case Law**: AI-extracted list of cited cases

## Requirements

- Python 3.9+
- pydantic >= 2.0.0
- openai >= 1.0.0 (for OpenAI integration)
- python-dotenv >= 1.0.0

## Environment Variables

- `LLM_PROVIDER`: Choose LLM provider ("openai", "mock")
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4o-mini)

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Acknowledgments

LegalBot uses a modular LLM-powered agent architecture for legal document analysis, leveraging Large Language Models to provide intelligent, context-aware legal analysis.
