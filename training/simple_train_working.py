import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
import json

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
tokenizer.pad_token = tokenizer.eos_token

bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1", quantization_config=bnb_config, device_map="auto")
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"], lora_dropout=0.05, bias="none", task_type="CAUSAL_LM")
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

with open("data/processed/training_dataset.jsonl", "r") as f:
 data = [json.loads(line) for line in f]

texts = []
for d in data:
 scenario = d["scenario"]
 conclusion = d["conclusion"]
 texts.append(f"[INST] {scenario} [/INST] {conclusion}")

dataset = Dataset.from_dict({"text": texts})

def tokenize_function(examples):
 result = tokenizer(examples["text"], truncation=True, max_length=256, padding="max_length")
 result["labels"] = result["input_ids"].copy()
 return result

tokenized = dataset.map(tokenize_function, batched=True)

training_args = TrainingArguments(output_dir="models/ethics-v1", num_train_epochs=3, per_device_train_batch_size=1, gradient_accumulation_steps=8, learning_rate=2e-4, logging_steps=1, fp16=True, report_to=[])
trainer = Trainer(model=model, args=training_args, train_dataset=tokenized)
trainer.train()
model.save_pretrained("models/ethics-v1/final")
