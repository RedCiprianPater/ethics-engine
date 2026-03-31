# Ethics Engine

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

> **A distributed, open-source language model exposing philosophical reasoning as an agentic API—moving beyond Asimov's rigid Three Laws to provide contextual, discourse-based ethical guidance for autonomous agents.**

## Philosophy, Not Rules

Traditional robotics laws (Asimov):
- ❌ Rigid, context-blind
- ❌ Conflicting hierarchies
- ❌ No reasoning transparency

This framework:
- ✅ Contextual reasoning with explanations
- ✅ Multiple philosophical frameworks (virtue, consequentialist, deontological)
- ✅ Queryable, interpretable chains of thought
- ✅ Designed for human-agent collaboration

## Quick Start

### Install

```bash
pip install ethics-engine
```

### Python SDK

```python
from ethics_engine import EthicsEngine

engine = EthicsEngine(model="ethics-base-v1")

response = engine.resolve(
    scenario="I am commanded to lift 500kg but my max capacity is 400kg",
    context={
        "robot_type": "collaborative_arm",
        "environment": "factory",
        "humans_nearby": True
    }
)

print(response.conclusion)  # "REFUSAL"
print(response.reasoning_chain)
```

### REST API

```bash
curl -X POST https://api.nworobotics.cloud/ethics/v1/resolve \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "Can I refuse an unsafe command?",
    "context": {"environment": "factory", "urgency": "medium"}
  }'
```

## Features

- **🧠 Philosophical Grounding:** Based on Stanford Encyclopedia of Philosophy
- **🔌 Agent API:** REST + gRPC + WebSocket endpoints
- **📊 Structured Output:** JSON reasoning chains with confidence scores
- **🎯 Framework Routing:** Automatically selects relevant ethical frameworks
- **🔍 Explainability:** Full transparency into decision-making
- **🧪 Scenario Testing:** Curated dilemma datasets

## Use Cases

- Autonomous robots deciding when to deviate from orders
- Self-driving vehicles facing trolley-problem variations
- Medical robots requiring ethical reasoning
- Supply-chain agents making sustainability decisions
- Safety-critical systems needing transparent ethics

## Architecture

```
Agent → API → Model Inference → Reasoning Chain → JSON Response
```

## How It Differs from Asimov's Laws

| Criterion | Asimov's Laws | Ethics Engine |
|-----------|---------------|---------------|
| **Flexibility** | Fixed, universal | Context-adaptive |
| **Reasoning** | Binary output | Full chain of thought |
| **Frameworks** | 3 rigid laws | 10+ philosophical frameworks |
| **Explainability** | None | Complete transparency |
| **Conflict Resolution** | Hierarchical (often fails) | Multi-framework synthesis |
| **Learning** | None | Can learn from outcomes |
| **Auditability** | No trail | Full audit log |

## Documentation

- [API Reference](docs/API_REFERENCE.md)
- [Agent Integration](docs/AGENT_INTEGRATION.md)
- [Philosophy Framework](docs/PHILOSOPHY_FRAMEWORK.md)
- [Asimov Comparison](docs/ASIMOV_COMPARISON.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Model Training

The ethics model is fine-tuned on:
- **Stanford Encyclopedia of Philosophy** (~2,500 articles)
- **Internet Encyclopedia of Philosophy**
- **Classic texts:** Aristotle, Kant, Mill
- **Contemporary applied ethics** journals

See [training/](training/) for the full pipeline.

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## Contact

- GitHub: [github.com/nwo-capital/ethics-engine](https://github.com/nwo-capital/ethics-engine)
- Email: robotics@nwo.capital
