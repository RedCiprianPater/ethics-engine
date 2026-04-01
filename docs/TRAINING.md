# Training Guide for Ethics Engine

Community guide for fine-tuning the Ethics Engine model on your own hardware or cloud GPU.

## Quick Start

```bash
# Install dependencies
pip install transformers peft datasets torch wandb

# Basic training (local GPU)
python training/finetune.py \
  --dataset data/processed/training_dataset.jsonl \
  --output models/my-ethics-model

# With custom settings
python training/finetune.py \
  --model mistralai/Mistral-7B-Instruct-v0.1 \
  --dataset data/processed/training_dataset.jsonl \
  --output models/ethics-v2 \
  --epochs 5 \
  --batch-size 2 \
  --learning-rate 1e-4
```

## Hardware Requirements

| Environment | GPU | VRAM | Config |
|-------------|-----|------|--------|
| **Local** | RTX 3090/4090 | 24GB | Full precision |
| **Lambda Labs** | A10/A100 | 24-80GB | bf16, fast |
| **RunPod** | A100/RTX A6000 | 48-80GB | bf16 |
| **SageMaker** | ml.g5.xlarge+ | 24GB+ | Managed |
| **Colab (Free)** | T4 | 16GB | 8-bit quantized |

## Cloud Providers

### Lambda Labs (Recommended)

```bash
# SSH into Lambda instance
ssh ubuntu@your.lambda.ip

# Clone repo
git clone https://github.com/RedCiprianPater/ethics-engine.git
cd ethics-engine

# Install deps
pip install -r requirements-train.txt

# Run training
python training/finetune.py \
  --gpu lambda \
  --model mistralai/Mistral-7B-Instruct-v0.1 \
  --output models/ethics-lambda-v1
```

**Cost**: ~$0.50-1.50/hour for A10/A100

### RunPod

```bash
# Start pod with PyTorch template
# SSH or use Jupyter

python training/finetune.py \
  --gpu runpod \
  --wandb-project ethics-engine \
  --output models/ethics-runpod-v1
```

**Cost**: ~$0.40-1.20/hour

### Google Colab (Free)

```python
# In Colab notebook
!git clone https://github.com/RedCiprianPater/ethics-engine.git
%cd ethics-engine
!pip install -q transformers peft datasets torch

# 8-bit training for T4 GPU
!python training/finetune.py \
  --gpu colab \
  --epochs 1 \
  --batch-size 1 \
  --gradient-accumulation 8 \
  --output models/ethics-colab
```

**Limit**: 12-hour sessions, T4 GPU

### AWS SageMaker

```python
# sagemaker_training.py
import sagemaker
from sagemaker.pytorch import PyTorch

estimator = PyTorch(
    entry_point='training/finetune.py',
    source_dir='.',
    role=sagemaker.get_execution_role(),
    instance_type='ml.g5.xlarge',
    instance_count=1,
    framework_version='2.0',
    py_version='py310',
    hyperparameters={
        'gpu': 'sagemaker',
        'epochs': 3,
        'batch-size': 4
    }
)

estimator.fit('s3://your-bucket/ethics-data/')
```

## Training Parameters

### LoRA Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--lora-r` | 16 | LoRA rank (8-32) |
| `--lora-alpha` | 32 | Scaling factor (2×r) |
| `--lora-dropout` | 0.05 | Regularization |

Higher rank = more capacity, more VRAM needed.

### Training Hyperparameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--epochs` | 3 | Training epochs |
| `--batch-size` | 4 | Per-device batch |
| `--gradient-accumulation` | 4 | Steps before update |
| `--learning-rate` | 2e-4 | LR for LoRA |
| `--warmup-steps` | 100 | LR warmup |

### Effective Batch Size

```
effective_batch = batch_size × gradient_accumulation × num_gpus
```

Target: 16-32 for stable training.

## Monitoring Training

### Weights & Biases

```bash
# Login (one-time)
wandb login

# Training logs automatically
python training/finetune.py \
  --wandb-project ethics-engine \
  --wandb-entity your-username
```

### Local Logging

```bash
# Disable W&B
python training/finetune.py --offline

# View logs
tail -f models/ethics-base-v1/training.log
```

## Resume Training

```bash
# From checkpoint
python training/finetune.py \
  --resume models/ethics-base-v1/checkpoint-500 \
  --output models/ethics-base-v1-resumed
```

## Contributing Your Model

Trained a good model? Share it!

```bash
# 1. Test your model
python -c "
from peft import PeftModel
from transformers import AutoModelForCausalLM
base = AutoModelForCausalLM.from_pretrained('mistralai/Mistral-7B-Instruct-v0.1')
model = PeftModel.from_pretrained(base, 'models/your-model')
print('Model loads successfully!')
"

# 2. Upload to Hugging Face
pip install huggingface-hub
huggingface-cli upload your-username/ethics-engine-v1 models/your-model/final

# 3. Open PR to update default model
# Or share model card in GitHub issues
```

## Troubleshooting

### Out of Memory

```bash
# Reduce batch size, increase accumulation
python training/finetune.py \
  --batch-size 1 \
  --gradient-accumulation 16

# Or use 8-bit
python training/finetune.py --gpu colab
```

### Slow Training

```bash
# Use bf16 on Ampere GPUs (A100, RTX 30xx+)
python training/finetune.py --gpu lambda

# Enable gradient checkpointing (saves VRAM, slower)
# Edit training/finetune.py:
# model.gradient_checkpointing_enable()
```

### Dataset Issues

```bash
# Validate dataset first
python scripts/validate_jsonl.py data/processed/training_dataset.jsonl

# Check format
head -1 data/processed/training_dataset.jsonl | python -m json.tool
```

## Cost Estimates

| Provider | GPU | Hours | Cost |
|----------|-----|-------|------|
| Colab Pro | T4/V100 | 3 | $10/month |
| Lambda | A10 | 3 | $1.50 |
| RunPod | A100 | 3 | $3.60 |
| SageMaker | ml.g5.2xlarge | 3 | $4.50 |

3 epochs on ~1000 examples ≈ 2-3 hours.

## Community Compute Pool

Want to contribute GPU time?

1. Train on your hardware
2. Upload model to Hugging Face
3. Open PR with model card
4. We ensemble community models

**Rewards**: GitHub contribution credit, model attribution.

## Questions?

- GitHub Issues: https://github.com/RedCiprianPater/ethics-engine/issues
- Discussions: https://github.com/RedCiprianPater/ethics-engine/discussions

## Next Steps

1. Generate training data: `python scripts/contribute.py --aggregate`
2. Train model: `python training/finetune.py`
3. Evaluate: Compare against baseline
4. Share: Upload to Hugging Face
