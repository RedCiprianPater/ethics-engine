#!/usr/bin/env python3
"""
Training script for Ethics Engine using LoRA.
Designed to run on consumer GPUs (Colab, Lambda, etc.)
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict

try:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        DataCollatorForLanguageModeling
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from datasets import Dataset
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    print("Warning: Training dependencies not installed.")
    print("Install with: pip install transformers peft datasets torch")

def load_config(config_path: Path) -> Dict:
    """Load training configuration"""
    with open(config_path) as f:
        return yaml.safe_load(f)

def format_training_example(qa: Dict, template: str) -> str:
    """Format a Q&A pair for training"""
    return template.format(
        scenario=qa['scenario'],
        framework=qa['framework'],
        reasoning=qa['reasoning'],
        conclusion=qa['conclusion']
    )

def load_dataset(dataset_path: Path, template: str, val_split: float = 0.1):
    """Load and split training data"""
    with open(dataset_path) as f:
        qa_pairs = [json.loads(line) for line in f if line.strip()]
    
    # Format for training
    formatted = [format_training_example(qa, template) for qa in qa_pairs]
    
    # Split train/val
    split_idx = int(len(formatted) * (1 - val_split))
    train_texts = formatted[:split_idx]
    val_texts = formatted[split_idx:]
    
    return train_texts, val_texts

def main():
    if not HAS_DEPS:
        print("Cannot train without dependencies.")
        return
    
    # Load config
    config = load_config(Path("train/lora_config.yaml"))
    
    # Check for training data
    dataset_path = Path(config['data']['train_file'])
    if not dataset_path.exists():
        print(f"Error: Training data not found at {dataset_path}")
        print("Run: python scripts/contribute.py --aggregate")
        return
    
    print(f"Loading model: {config['model_name']}")
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        config['model_name'],
        torch_dtype=torch.float16,
        device_map="auto",
        load_in_8bit=True  # Quantize for memory efficiency
    )
    
    # Prepare for LoRA
    model = prepare_model_for_kbit_training(model)
    
    lora_config = LoraConfig(
        r=config['lora']['r'],
        lora_alpha=config['lora']['alpha'],
        target_modules=config['lora']['target_modules'],
        lora_dropout=config['lora']['dropout'],
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    print(f"Trainable parameters: {model.print_trainable_parameters()}")
    
    # Load dataset
    print("Loading dataset...")
    train_texts, val_texts = load_dataset(
        dataset_path,
        config['template'],
        config['data']['validation_split']
    )
    
    print(f"Training examples: {len(train_texts)}")
    print(f"Validation examples: {len(val_texts)}")
    
    # Tokenize
    def tokenize(texts):
        return tokenizer(
            texts,
            truncation=True,
            max_length=config['training']['max_seq_length'],
            padding="max_length"
        )
    
    train_dataset = Dataset.from_dict({"text": train_texts})
    val_dataset = Dataset.from_dict({"text": val_texts})
    
    # Training arguments
    output_dir = Path(config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=config['training']['num_epochs'],
        per_device_train_batch_size=config['training']['batch_size'],
        gradient_accumulation_steps=config['training']['gradient_accumulation_steps'],
        warmup_steps=config['training']['warmup_steps'],
        learning_rate=config['training']['learning_rate'],
        logging_steps=config['training']['logging_steps'],
        save_steps=config['training']['save_steps'],
        evaluation_strategy="steps",
        eval_steps=config['training']['save_steps'],
        save_total_limit=3,
        load_best_model_at_end=True,
        fp16=True,
        report_to="none"  # Disable wandb for simplicity
    )
    
    # Trainer
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    from transformers import Trainer
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator
    )
    
    # Train
    print("\nStarting training...")
    trainer.train()
    
    # Save
    final_output = output_dir / "final"
    trainer.save_model(final_output)
    tokenizer.save_pretrained(final_output)
    
    print(f"\n✅ Training complete!")
    print(f"Model saved to: {final_output}")
    print(f"\nTo use the model:")
    print(f"  from peft import PeftModel")
    print(f"  model = PeftModel.from_pretrained(base_model, '{final_output}')")

if __name__ == "__main__":
    main()
