# Contributing to Ethics Engine

Thank you for your interest in contributing to Ethics Engine! This document will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Adding Ethical Frameworks](#adding-ethical-frameworks)
  - [Writing Examples](#writing-examples)
  - [Improving Documentation](#improving-documentation)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to:

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect differing viewpoints

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up your development environment
4. Make your changes
5. Submit a pull request

## How to Contribute

### Reporting Bugs

Before creating a bug report, please:

1. Check if the issue already exists
2. Try to reproduce with the latest version
3. Collect relevant information (error messages, logs)

When reporting, include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Code snippets or error messages

### Suggesting Features

We welcome feature suggestions! Please:

1. Check if the feature has already been suggested
2. Explain the use case clearly
3. Describe how it would benefit the project
4. Consider implementation complexity

### Adding Ethical Frameworks

One of the most valuable contributions is adding new ethical frameworks. Here's how:

#### 1. Research the Framework

Understand the framework thoroughly:
- Key philosophers and texts
- Core principles
- When it's most applicable
- Counterarguments and criticisms

#### 2. Add to Framework Registry

Edit `src/ethics_engine/api/app.py`:

```python
FRAMEWORKS.append(
    FrameworkMatch(
        id="feminist-ethics",
        name="Feminist Ethics",
        philosophers=["Gilligan", "Noddings", "Baier"],
        description="Focuses on care, relationships, and power structures",
        best_for=["caregiving", "relationships", "power-dynamics"],
    )
)
```

#### 3. Add Reasoning Logic

Create reasoning prompts for the model in `src/ethics_engine/model/prompts/`:

```python
FEMINIST_ETHICS_PROMPT = """
Analyze this scenario from feminist ethics perspective.

Key considerations:
- Care and relationships
- Power dynamics
- Vulnerability
- Contextual factors

Provide:
1. Core principle applied
2. Reasoning argument
3. Relevant philosophers
4. Confidence score
"""
```

#### 4. Add Tests

Create tests in `tests/test_frameworks.py`:

```python
def test_feminist_ethics_framework():
    response = client.post("/resolve", json={
        "scenario": "Caregiving scenario",
        "frameworks": ["feminist-ethics"]
    })
    assert "feminist-ethics" in response.json()["frameworks_invoked"]
```

#### 5. Document

Add to `docs/PHILOSOPHY_FRAMEWORK.md`:

```markdown
## Feminist Ethics

### Overview
Feminist ethics emphasizes care, relationships, and attention to power structures...

### Key Philosophers
- Carol Gilligan
- Nel Noddings
- Annette Baier

### When to Use
- Caregiving scenarios
- Relationship conflicts
- Power dynamic analysis

### Example
```python
response = engine.resolve(
    scenario="Should I prioritize efficiency or care?",
    frameworks=["feminist-ethics"]
)
```
```

### Writing Examples

Examples help users understand how to use the framework. To add an example:

#### 1. Create Example File

Create `examples/your_example.py`:

```python
"""
Example: Medical Robot Ethics

This example shows how a medical robot might use ethics engine
for patient care decisions.
"""

from ethics_engine import EthicsEngine

def main():
    engine = EthicsEngine(api_key="your_key", agent_id="medical_bot_01")
    
    # Scenario: Patient refuses treatment
    response = engine.resolve(
        scenario="Patient refuses life-saving treatment due to religious beliefs",
        context={
            "environment": "hospital",
            "urgency": "critical",
            "safety_critical": True
        },
        frameworks=["deontology", "virtue-ethics", "applied-ethics"]
    )
    
    print(f"Conclusion: {response.conclusion}")
    print(f"Synthesis: {response.synthesis}")

if __name__ == "__main__":
    main()
```

#### 2. Add to README

List your example in the README under Examples section.

#### 3. Document Key Points

Explain:
- What scenario it covers
- Which frameworks are most relevant
- Expected outcomes
- Real-world applicability

### Improving Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add more code examples
- Improve API reference
- Translate to other languages
- Create video tutorials

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- Virtual environment (recommended)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ethics-engine.git
cd ethics-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,api,training]"

# Run tests
pytest

# Run linting
ruff check src/ethics_engine
black src/ --check
mypy src/ethics_engine
```

## Code Style

We use:
- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **MyPy** for type checking
- **Google-style** docstrings

### Formatting

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check linting
ruff check src/ethics_engine

# Type check
mypy src/ethics_engine
```

### Type Hints

Use type hints for all function signatures:

```python
def resolve_scenario(
    scenario: str,
    context: Optional[Dict[str, Any]] = None,
    frameworks: Optional[List[str]] = None
) -> EthicsResponse:
    """Resolve an ethical scenario."""
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ethics_engine --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::TestHealth::test_health_check
```

### Writing Tests

All new features should include tests:

```python
def test_new_feature():
    """Test description."""
    # Arrange
    engine = EthicsEngine(api_key="test", agent_id="test")
    
    # Act
    result = engine.new_feature()
    
    # Assert
    assert result is not None
    assert result.status == "success"
```

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add feminist ethics framework

- Add feminist ethics to framework registry
- Include care ethics reasoning prompts
- Add tests and documentation

Closes #123
```

Format: `<type>: <subject>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

## Pull Request Process

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run checks**
   ```bash
   pytest
   ruff check src/ethics_engine
   black src/ --check
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: Add your feature"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill in the template
   - Link related issues

6. **Review Process**
   - Maintainers will review your PR
   - Address any feedback
   - Once approved, it will be merged

## Questions?

- Open an issue for questions
- Join our Discord community
- Email: robotics@nwo.capital

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to Ethics Engine!
