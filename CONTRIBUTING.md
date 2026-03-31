# Contributing to Ethics Engine

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone repository
git clone https://github.com/nwo-capital/ethics-engine.git
cd ethics-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate

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

- Follow PEP 8
- Use type hints
- Write docstrings
- Maximum line length: 100

## Testing

- Write tests for new features
- Maintain >80% coverage
- Use pytest

## Areas for Contribution

- Additional ethical frameworks
- Training data curation
- Model evaluation benchmarks
- Integration examples
- Documentation improvements

## License

Apache 2.0
