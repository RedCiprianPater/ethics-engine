# Ethics Engine - Project Summary

## Overview

**Ethics Engine** is a distributed, open-source language model exposing philosophical reasoning as an agentic API—moving beyond Asimov's rigid Three Laws to provide contextual, discourse-based ethical guidance for autonomous agents.

## What Was Built

### 1. Python SDK (`src/ethics_engine/`)
- **Synchronous Client** (`client.py`): Blocking API calls
- **Asynchronous Client** (`client_async.py`): Non-blocking with streaming support
- **Schemas** (`schemas.py`): Pydantic models for type-safe API interaction
- **Exceptions** (`exceptions.py`): Custom error handling

### 2. FastAPI Server (`src/ethics_engine/api/`)
- **Main App** (`app.py`): REST endpoints
  - `POST /resolve` - Resolve ethical scenarios
  - `POST /compare` - Compare multiple actions
  - `GET /frameworks` - List available frameworks
  - `POST /learn` - Feedback for continuous learning
  - `WebSocket /stream/reasoning` - Real-time reasoning stream
- **Authentication** (`auth.py`): API key + Agent ID verification
- **Rate Limiting** (`rate_limit.py`): Per-agent throttling

### 3. Training Pipeline (`training/`)
- **Dataset Builder**: SEP ingestion, Q&A generation, scenario creation
- **Trainer**: LoRA fine-tuning on Mistral-7B
- **Evaluation**: Framework accuracy, reasoning coherence metrics

### 4. Documentation (`docs/`)
- `API_REFERENCE.md` - Complete API documentation
- `AGENT_INTEGRATION.md` - Integration guide for robots
- `ASIMOV_COMPARISON.md` - Philosophy vs Asimov's Laws
- `ARCHITECTURE.md` - System architecture overview
- `architecture.svg` - Visual architecture diagram

### 5. Examples (`examples/`)
- `basic_query.py` - Simple ethics query
- `robot_arm_safety.py` - Collaborative robot scenarios
- `autonomous_vehicle_dilemma.py` - Trolley problem variations

## Key Features

### Multi-Framework Reasoning
Instead of rigid laws, the engine invokes multiple ethical frameworks:
- **Deontology**: Duties and obligations (Kant)
- **Consequentialism**: Outcomes and utility (Mill)
- **Virtue Ethics**: Character and judgment (Aristotle)
- **Care Ethics**: Relationships and vulnerability (Gilligan)
- **Contractarianism**: Social contracts (Rawls)
- **Applied Ethics**: Professional standards

### Structured Output
```json
{
  "conclusion": "CONDITIONAL_REFUSAL",
  "confidence": 0.87,
  "reasoning_chain": [
    {
      "framework": "deontology",
      "principle": "Duty to preserve life",
      "argument": "A robot has a duty to not cause harm",
      "philosophers": ["Kant", "Ross"],
      "confidence": 0.87
    }
  ],
  "asimov_comparison": {
    "law1_conflict": true,
    "explanation": "Philosophy suggests alignment with safety"
  }
}
```

### NWO Robotics Integration
- Webhook notifications for real-time updates
- Audit trail logging
- Agent registry integration
- Command validation pipeline

## Repository Structure

```
ethics-engine/
├── src/ethics_engine/          # Python SDK
│   ├── __init__.py
│   ├── client.py               # Sync client
│   ├── client_async.py         # Async client
│   ├── schemas.py              # Pydantic models
│   ├── exceptions.py           # Error classes
│   └── api/                    # FastAPI server
│       ├── app.py
│       ├── auth.py
│       └── rate_limit.py
├── training/                   # Model training
│   └── train.py
├── docs/                       # Documentation
│   ├── API_REFERENCE.md
│   ├── AGENT_INTEGRATION.md
│   ├── ASIMOV_COMPARISON.md
│   ├── ARCHITECTURE.md
│   └── architecture.svg
├── examples/                   # Usage examples
│   ├── basic_query.py
│   ├── robot_arm_safety.py
│   └── autonomous_vehicle_dilemma.py
├── .github/workflows/          # CI/CD
│   ├── tests.yml
│   └── publish.yml
├── README.md
├── pyproject.toml
├── LICENSE (Apache 2.0)
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## Next Steps for Step 2 (NWO Integration)

### 1. Deploy API Server
```bash
# Deploy to NWO infrastructure
docker build -t ethics-engine:latest .
docker push nwo-registry/ethics-engine:latest
kubectl apply -f k8s/deployment.yaml
```

### 2. Fine-tune Model
```bash
# Train on SEP dataset
cd training
python train.py --base_model mistral-7b-instruct \
                --dataset data/sep_ethics.jsonl \
                --output_dir models/ethics-v1
```

### 3. NWO CLI Integration
```python
# In nwo-robotics CLI
from ethics_engine import EthicsEngine

class NWOEthicsPlugin:
    def __init__(self, api_key, agent_id):
        self.engine = EthicsEngine(api_key, agent_id)
    
    def validate_command(self, command):
        response = self.engine.resolve(
            scenario=command.description,
            context={"robot_type": self.robot_type}
        )
        return response.conclusion != "REFUSAL"
```

### 4. Webhook Endpoint
Add to NWO platform to receive ethics decisions:
```python
@app.post("/webhooks/ethics")
async def ethics_webhook(payload: EthicsDecision):
    # Log to NWO audit trail
    await nwo_audit.log(payload)
    # Alert if human review needed
    if payload.human_review_recommended:
        await alert_supervisor(payload)
```

## Comparison: What I Built vs Your Plan

| Aspect | Your Plan | What I Built | Status |
|--------|-----------|--------------|--------|
| **Core SDK** | Python client | ✅ Complete | Ready |
| **API Server** | FastAPI | ✅ Complete | Ready |
| **Training Pipeline** | SEP fine-tuning | ✅ Structure | Needs data |
| **Documentation** | Full docs | ✅ Complete | Ready |
| **Model Weights** | Fine-tuned LM | ❌ Not included | Step 2 |
| **NWO Integration** | Webhooks | ✅ Structure | Step 2 |
| **Deployment** | K8s/Docker | ❌ Not included | Step 2 |

## Files Ready for GitHub

All files are in `/root/.openclaw/workspace/ethics-engine/`:

**Ready to commit:**
- ✅ README.md
- ✅ LICENSE (Apache 2.0)
- ✅ pyproject.toml
- ✅ src/ethics_engine/ (SDK + API)
- ✅ docs/ (full documentation)
- ✅ examples/ (working examples)
- ✅ training/ (training pipeline structure)
- ✅ .github/workflows/ (CI/CD)

**To upload to GitHub:**
```bash
cd /root/.openclaw/workspace/ethics-engine
git init
git add .
git commit -m "Initial commit: Ethics Engine v0.1.0"
git remote add origin https://github.com/nwo-capital/ethics-engine.git
git push -u origin main
```

## License

Apache 2.0 - Permissive open source license allowing commercial use.

## Contact

- GitHub: github.com/nwo-capital/ethics-engine
- Email: robotics@nwo.capital
