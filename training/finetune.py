#!/usr/bin/env python3
"""
Fine-tuning script for Ethics Engine.
Supports local GPU, cloud providers (Lambda, RunPod, SageMaker), and Colab.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

import yaml

try:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from datasets import Dataset, load_dataset
    import wandb
    HAS_DEPS = True
except ImportError as e:
    HAS_DEPS = False
    print(f"Missing dependencies: {e}")
    print("Install: pip install transformers peft datasets torch wandb")
    sys.exit(1)

# Cloud provider configurations
CLOUD_CONFIGS = {
    "local": {
        "device": "auto",
        "fp16": True,
        "bf16": False,
        "load_in_8bit": True,
    },
    "lambda": {
        "device": "cuda",
        "fp16": True,
        "bf16": True,  # A10/A100 support bf16
        "load_in_8bit": False,  # Full precision on cloud
    },
    "runpod": {
        "device": "cuda",
        "fp16": True,
        "bf16": True,
        "load_in_8bit": False,
    },
    "sagemaker": {
        "device": "cuda",
        "fp16": True,
        "bf16": True,
        "load_in_8bit": False,
    },
    "colab": {
        "device": "cuda",
        "fp16": True,
        "bf16": False,  # T4 doesn't support bf16
        "load_in_8bit": True,  # Save memory on Colab
    }
}

def parse_args():
    parser = argparse.ArgumentParser(
        description="Fine-tune Ethics Engine model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local training with defaults
  python training/finetune.py --dataset data/training_dataset.jsonl

  # Cloud training (Lambda Labs)
  python training/finetune.py --gpu lambda --model mistralai/Mistral-7B-Instruct-v0.1

  # Colab training (8-bit to save memory)
  python training/finetune.py --gpu colab --epochs 1 --batch-size 1

  # Custom output directory
  python training/finetune.py --output models/my-ethics-model --wandb-project ethics-engine
        """
    )
    
    # Model & data
    parser.add_argument("--model", default="mistralai/Mistral-7B-Instruct-v0.1",
                       help="Base model to fine-tune (default: Mistral-7B)")
    parser.add_argument("--dataset", default="data/processed/training_dataset.jsonl",
                       help="Path to training dataset (JSONL format)")
    parser.add_argument("--output", default="models/ethics-base-v1",
                       help="Output directory for trained model")
    
    # GPU/Compute
    parser.add_argument("--gpu", default="auto",
                       choices=["auto", "local", "lambda", "runpod", "sagemaker", "colab"],
                       help="GPU environment configuration")
    
    # Training hyperparameters
    parser.add_argument("--epochs", type=int, default=3,
                       help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=4,
                       help="Per-device batch size")
    parser.add_argument("--gradient-accumulation", type=int, default=4,
                       help="Gradient accumulation steps")
    parser.add_argument("--learning-rate", type=float, default=2e-4,
                       help="Learning rate")
    parser.add_argument("--warmup-steps", type=int, default=100,
                       help="Warmup steps")
    parser.add_argument("--max-seq-length", type=int, default=1024,
                       help="Maximum sequence length")
    
    # LoRA parameters
    parser.add_argument("--lora-r", type=int, default=16,
                       help="LoRA rank")
    parser.add_argument("--lora-alpha", type=int, default=32,
                       help="LoRA alpha (scaling)")
    parser.add_argument("--lora-dropout", type=float, default=0.05,
                       help="LoRA dropout")
    
    # Logging
    parser.add_argument("--wandb-project", default="ethics-engine",
                       help="Weights & Biases project name")
    parser.add_argument("--wandb-entity", default=None,
                       help="Weights & Biases entity/team")
    parser.add_argument("--offline", action="store_true",
                       help="Disable W&B logging (offline mode)")
    
    # Resume
    parser.add_argument("--resume", type=str, default=None,
                       help="Resume from checkpoint directory")
    
    return parser.parse_args()

def setup_wandb(args):
    """Initialize Weights & Biases logging"""
    if args.offline:
        os.environ["WANDB_MODE"] = "offline"
        return None
    
    try:
        wandb.init(
            project=args.wandb_project,
            entity=args.wandb_entity,
            config=vars(args),
            name=f"{Path(args.output).name}-{args.gpu}"
        )
        return wandb
    except Exception as e:
        print(f"W&B init failed: {e}")
        return None

def load_and_format_dataset(dataset_path: str, tokenizer, max_length: int = 1024):
    """Load and format dataset for training"""
    
    def format_example(example):
        """Format a single Q&A pair"""
        text = f"""### Instruction:
Analyze the following ethical scenario using {example.get('framework', 'ethical')} reasoning.

Scenario: {example['scenario']}

### Response:
Reasoning: {example['reasoning']}

Conclusion: {example['conclusion']}

###"""
        return {"text": text}
    
    # Load JSONL
    dataset = load_dataset("json", data_files=dataset_path, split="train")
    
    # Format
    dataset = dataset.map(format_example)
    
    # Tokenize
    def tokenize(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length"
        )
    
    dataset = dataset.map(tokenize, batched=True)
    dataset = dataset.remove_columns([col for col in dataset.column_names if col not in ["input_ids", "attention_mask"]])
    
    return dataset

def get_gpu_config(gpu_type: str):
    """Get GPU configuration for environment"""
    if gpu_type == "auto":
        # Detect environment
        if "LAMBDA_GPU" in os.environ:
            return CLOUD_CONFIGS["lambda"]
        elif "RUNPOD_POD_ID" in os.environ:
            return CLOUD_CONFIGS["runpod"]
        elif "SM_MODEL_DIR" in os.environ:
            return CLOUD_CONFIGS["sagemaker"]
        elif "COLAB_GPU" in os.environ or not torch.cuda.is_available():
            return CLOUD_CONFIGS["colab"]
        else:
            return CLOUD_CONFIGS["local"]
    
    return CLOUD_CONFIGS.get(gpu_type, CLOUD_CONFIGS["local"])

def main():
    args = parse_args()
    
    print("=" * 60)
    print("NWO Ethics Engine - Fine-tuning")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Dataset: {args.dataset}")
    print(f"Output: {args.output}")
    print(f"GPU config: {args.gpu}")
    print("-" * 60)
    
    # Check dataset exists
    if not Path(args.dataset).exists():
        print(f"Error: Dataset not found: {args.dataset}")
        print("Generate training data first:")
        print("  python scripts/contribute.py --aggregate")
        sys.exit(1)
    
    # Setup W&B
    wandb_run = setup_wandb(args)
    
    # Get GPU config
    gpu_config = get_gpu_config(args.gpu)
    print(f"Using GPU config: {gpu_config}")
    
    # Load tokenizer
    print("\nLoading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model
    print("Loading model...")
    load_kwargs = {
        "torch_dtype": torch.float16 if gpu_config["fp16"] else torch.float32,
        "device_map": gpu_config["device"],
    }
    
    if gpu_config["load_in_8bit"]:
        load_kwargs["load_in_8bit"] = True
    
    model = AutoModelForCausalLM.from_pretrained(args.model, **load_kwargs)
    
    # Prepare for LoRA
    if gpu_config["load_in_8bit"]:
        model = prepare_model_for_kbit_training(model)
    
    # Setup LoRA
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Load dataset
    print("\nLoading dataset...")
    dataset = load_and_format_dataset(args.dataset, tokenizer, args.max_seq_length)
    
    # Split train/val
    dataset = dataset.train_test_split(test_size=0.1)
    print(f"Train examples: {len(dataset['train'])}")
    print(f"Validation examples: {len(dataset['test'])}")
    
    # Training arguments
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation,
        warmup_steps=args.warmup_steps,
        learning_rate=args.learning_rate,
        fp16=gpu_config["fp16"],
        bf16=gpu_config["bf16"],
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=100,
        save_strategy="steps",
        save_steps=500,
        save_total_limit=3,
        load_best_model_at_end=True,
        report_to="wandb" if wandb_run else None,
        run_name=f"{output_dir.name}-{args.gpu}" if wandb_run else None,
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        data_collator=data_collator,
    )
    
    # Train
    print("\nStarting training...")
    if args.resume:
        trainer.train(resume_from_checkpoint=args.resume)
    else:
        trainer.train()
    
    # Save final model
    print("\nSaving model...")
    final_dir = output_dir / "final"
    trainer.save_model(final_dir)
    tokenizer.save_pretrained(final_dir)
    
    # Save training config
    config_path = final_dir / "training_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(vars(args), f)
    
    print(f"\n{'='*60}")
    print(f"✅ Training complete!")
    print(f"Model saved to: {final_dir}")
    print(f"\nTo use the model:")
    print(f"  from peft import PeftModel")
    print(f"  model = PeftModel.from_pretrained(base_model, '{final_dir}')")
    print(f"{'='*60}")
    
    if wandb_run:
        wandb.finish()

if __name__ == "__main__":
    main()
