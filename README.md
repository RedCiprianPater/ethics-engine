# Data Pipeline for NWO Ethics Engine

Automated pipeline for generating training data from philosophical sources.

## Pipeline Flow

```
Raw Sources → Chunking → Q&A Generation → Validation → Training Data
```

## Scripts

### 1. Download Philosophy Sources
```bash
python scripts/download_sep.py
```
Downloads Stanford Encyclopedia of Philosophy articles (cached locally).

### 2. Semantic Chunking
```bash
python scripts/chunk_semantic.py
```
Splits texts into coherent sections and extracts dilemmas.

### 3. Generate Q&A Pairs
```bash
# With API (Kimi/OpenAI)
export OPENAI_API_KEY="your-key"
export OPENAI_BASE_URL="https://api.moonshot.cn/v1"
python scripts/generate_qa.py

# Without API (heuristic fallback)
python scripts/generate_qa.py
```

### 4. Validate
```bash
python scripts/validate_jsonl.py data/processed/qa_pairs.jsonl
```

### 5. Community Contributions
```bash
# See contribution template
python scripts/contribute.py --template

# Submit contribution
python scripts/contribute.py --submit my_qa.jsonl --contributor "YourName"

# Aggregate all data
python scripts/contribute.py --aggregate
```

## Directory Structure

```
data/
├── raw/sep/              # Cached SEP articles
├── processed/
│   ├── chunks/           # Semantic chunks
│   ├── qa_pairs.jsonl    # Generated Q&A
│   └── training_dataset.jsonl  # Final aggregated data
└── contributions/        # Community submissions
```

## Training

```bash
# Install dependencies
pip install transformers peft datasets torch

# Run training
python train/train.py
```

## Minimal Start

Generate initial dataset (~1000 Q&A pairs):

```bash
python scripts/download_sep.py        # ~30 min
python scripts/chunk_semantic.py      # ~5 min
python scripts/generate_qa.py         # ~10 min (API) or instant (fallback)
python scripts/validate_jsonl.py data/processed/qa_pairs.jsonl
```

## Community Workflow

1. Users create Q&A pairs following `contrib/TEMPLATE.md`
2. Submit via `scripts/contribute.py`
3. Maintainers aggregate with `scripts/contribute.py --aggregate`
4. Train model on combined dataset

## Metrics

Target: Start with 500-1000 high-quality Q&A pairs
Scale: Community contributions grow dataset organically
