# Ethics Engine

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

> A distributed, open-source language model exposing philosophical reasoning as an agentic API—moving beyond Asimov's rigid Three Laws to provide contextual, discourse-based ethical guidance for autonomous agents & robots.

## Phase 2 Updates (NEW)

The training infrastructure is now live! Community-driven model development with real inference:

### ☁️ Cloud Training Support

Train on any GPU provider:

```bash
# Lambda Labs (recommended)
python training/finetune.py --gpu lambda

# RunPod
python training/finetune.py --gpu runpod

# Google Colab (free tier)
python training/finetune.py --gpu colab --epochs 3

# AWS SageMaker
python training/finetune.py --gpu sagemaker
```

### 🆕 Simplified Training Script (RECOMMENDED)

We now provide a streamlined training script that works out of the box:

```bash
python training/simple_train_working.py
```

This script handles:
- 4-bit quantization for memory efficiency
- Proper dataset formatting with labels
- LoRA fine-tuning on Mistral-7B
- Tested on Google Colab with Tesla T4 GPU

*Note: The original finetune.py requires updates for newer transformers versions. See [TRAINING_FIXES.md](TRAINING_FIXES.md) for details.*

### 🔄 Training Roadmap

**Current Status:**
- ✅ Initial model trained on 6 ethical scenarios
- ✅ Working training pipeline established
- ✅ 4-bit quantization for efficient training

**Next Training Sessions:**
- Week 1: +20 scenarios covering medical ethics
- Week 2: +30 scenarios on AI alignment and safety
- Week 3: +25 scenarios on environmental ethics
- Week 4: Evaluation and refinement

### 🧠 Real Model Inference

API now connects to actual fine-tuned models:

```bash
# Load your trained model
MODEL_PATH=models/ethics-v1 python -m ethics_engine.api.app
```

Features:
- LoRA adapter support - Efficient fine-tuning (only 1% of weights)
- Heuristic fallback - Works without GPU using keyword matching
- Auto-framework selection - Chooses relevant ethical frameworks automatically
- 8-bit quantization - Run on consumer hardware

### 🤝 Community Contributions

Submit your own ethical scenarios:

```bash
# See contribution template
python scripts/contribute.py --template

# Submit Q&A pairs
python scripts/contribute.py --submit my_scenarios.jsonl --contributor "YourName"

# Aggregate all contributions
python scripts/contribute.py --aggregate
```

### 📊 Training Data Pipeline

Sample dataset included (6 frameworks, 6 Q&A pairs):
- Consequentialism
- Deontology (Kant)
- Virtue Ethics
- Care Ethics
- Contractarianism
- Applied Ethics

```bash
# View sample data
cat data/processed/qa_pairs.jsonl

# Validate format
python scripts/validate_jsonl.py data/processed/qa_pairs.jsonl
```

---

## 🎯 Why This Matters

Asimov's Three Laws are inadequate for real robots. This engine provides:

- ✅ **Context-aware reasoning** — Not binary rules
- ✅ **Transparent decision chains** — Every conclusion is explainable
- ✅ **Philosophy-grounded** — Based on centuries of ethical theory
- ✅ **Continuously improving** — Learns from real-world decisions
- ✅ **Community-driven** — Anyone can contribute training data

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

## Training Your Own Model

### 1. Prepare Data

```bash
# Load philosophy sources
python scripts/load_sources.py

# Chunk and extract dilemmas
python scripts/chunk_semantic.py

# Generate Q&A pairs
python scripts/generate_qa.py
```

### 2. Train

```bash
# Simple script (recommended)
python training/simple_train_working.py

# Or use the original script on Colab (free)
python training/finetune.py --gpu colab --epochs 3

# On Lambda Labs (~$2 for full training)
python training/finetune.py --gpu lambda --epochs 5
```

### 3. Deploy

```bash
MODEL_PATH=models/ethics-v1 python -m ethics_engine.api.app
```

See [docs/TRAINING.md](docs/TRAINING.md) for full guide.

## Features

- 🧠 **Philosophical Grounding**: Based on Stanford Encyclopedia of Philosophy
- 🔌 **Agent API**: REST + gRPC + WebSocket endpoints
- 📊 **Structured Output**: JSON reasoning chains with confidence scores
- 🎯 **Framework Routing**: Automatically selects relevant ethical frameworks
- 🔍 **Explainability**: Full transparency into decision-making
- 🧪 **Scenario Testing**: Curated dilemma datasets
- ☁️ **Cloud Training**: Lambda, RunPod, SageMaker, Colab support
- 🤝 **Community**: Contribute training data via JSONL

## Architecture

```
┌─────────────┐ ┌──────────────┐ ┌─────────────────┐
│   Agent     │─────▶│ Ethics API │─────▶│ LoRA Adapter │
│  Request    │      │ /resolve   │      │ (Fine-tuned) │
└─────────────┘      └──────────────┘      └─────────────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │  Mistral-7B      │
                      │ (Base Model)     │
                      └──────────────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │  Heuristic       │ (Fallback if no GPU)
                      │  Fallback        │
                      └──────────────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │ JSON Response    │
                      │ + Reasoning      │
                      └──────────────────┘
```

## How It Differs from Asimov's Laws

| Criterion | Asimov Laws | Ethics Engine |
|-----------|-------------|---------------|
| Flexibility | Fixed, universal | Context-adaptive |
| Reasoning | Binary output | Full chain of thought |
| Frameworks | 3 rigid laws | 10+ philosophical frameworks |
| Explainability | None | Complete transparency |
| Conflict Resolution | Hierarchical (often fails) | Multi-framework synthesis |
| Learning | None | Can learn from outcomes |
| Auditability | No trail | Full audit log |
| Community | Closed | Open contributions |

## Documentation

- [API Reference](docs/API_REFERENCE.md)
- [Agent Integration](docs/AGENT_INTEGRATION.md)
- [Training Guide](docs/TRAINING.md) ⭐ NEW
- [Philosophy Framework](docs/PHILOSOPHY_FRAMEWORK.md)
- [Asimov Comparison](docs/ASIMOV_COMPARISON.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Roadmap](docs/ROADMAP.md)
- [Contributing](docs/CONTRIBUTING.md)

## Model Training

The ethics model is fine-tuned on:
- Stanford Encyclopedia of Philosophy (~2,500 articles)
- Internet Encyclopedia of Philosophy
- Classic texts: Aristotle, Kant, Mill
- Contemporary applied ethics journals
- Community contributions (JSONL format)

See [training/](training/) for the full pipeline.

## Contributing

We welcome contributions!

- **Training Data**: Submit ethical scenarios via `scripts/contribute.py`
- **Code**: Open PRs for features or bug fixes
- **Models**: Train and share your fine-tuned models
- **Documentation**: Improve docs and examples

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## Contact

- GitHub: [github.com/RedCiprianPater/ethics-engine](https://github.com/RedCiprianPater/ethics-engine)
- Email: robotics@nwo.capital
- Landing Page: [nwo.capital/webapp/ethics-engine.html](https://nwo.capital/webapp/ethics-engine.html)

---

Built with 💚 for ethical AI and robotics
