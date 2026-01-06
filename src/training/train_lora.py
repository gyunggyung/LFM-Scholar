import os
import argparse
import yaml
from typing import Dict, Optional

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset

def load_config(config_path: str) -> Dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="LFM-CiteAgent LoRA Training")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    parser.add_argument("--data_file", type=str, default="./data/processed/train.jsonl", help="Path to training data")
    parser.add_argument("--output_dir", type=str, default="./models/lfm2-adapter", help="Output directory for adapter")
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    # Model and Tokenizer settings
    model_name = config['model']['base']
    
    # Quantization config
    bnb_config = None
    if config['model'].get('quantization') == '4bit':
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
    
    print(f"Loading model: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    # Prepare model for LoRA
    if config['model'].get('quantization') == '4bit':
        model = prepare_model_for_kbit_training(model)
        
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"] # Common targets, adjust for LFM if needed
    )
    
    # Load dataset
    dataset = load_dataset('json', data_files=args.data_file, split='train')
    
    # Formatting function
    def format_prompts(example):
        text = f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['output']}"
        return [text]
    
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        logging_steps=10,
        save_strategy="epoch",
        fp16=True,
        optim="paged_adamw_32bit",
    )
    
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        max_seq_length=config['model'].get('max_length', 2048),
        tokenizer=tokenizer,
        args=training_args,
        formatting_func=format_prompts,
        dataset_text_field="text", # SFTTrainer requires a text field if formatting_func returns list
    )
    
    # Hack for SFTTrainer with formatting_func returning list of strings (depends on TRL version)
    # Ideally formatting_func returns list of strings, and dataset doesn't need 'text' column if packed=False.
    # But usually it's cleaner to map dataset first.
    # Let's simple use map manually to be safe.
    
    def apply_format(example):
        return {"text": f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['output']}"}
    
    dataset = dataset.map(apply_format)
    
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        max_seq_length=config['model'].get('max_length', 2048),
        tokenizer=tokenizer,
        args=training_args,
        dataset_text_field="text",
    )
    
    print("Starting training...")
    trainer.train()
    
    print("Saving model...")
    trainer.save_model(args.output_dir)

if __name__ == "__main__":
    main()
