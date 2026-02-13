"""
Fine-tuning script for BFSI SLM using LoRA (Parameter-Efficient Fine-Tuning).

NOTE: This script requires a GPU with CUDA support and additional packages:
    pip install torch transformers peft datasets accelerate

This is OPTIONAL — the template-based SLMEngine works without fine-tuning.
"""

import os

def train():
    # Lazy imports — these packages are only needed when training
    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, get_peft_model, TaskType
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install training dependencies: pip install torch transformers peft datasets accelerate")
        return

    if not torch.cuda.is_available():
        print("WARNING: CUDA not available. Training on CPU will be extremely slow.")
        print("Consider using Google Colab or a cloud GPU instance.")

    # Resolve dataset path relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(project_root, "bfsi_alpaca_1_to_160_final_clean.json")

    if not os.path.exists(dataset_path):
        print(f"Dataset not found at: {dataset_path}")
        print("Run 'python src/create_dataset.py' first.")
        return

    # Load dataset
    data_files = {"train": dataset_path}
    dataset = load_dataset("json", data_files=data_files, split="train")

    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    def tokenize_function(examples):
        text = f"{examples['instruction']} {examples['input']} Answer: {examples['output']}"
        return tokenizer(text, truncation=True, padding="max_length", max_length=256)

    tokenized_datasets = dataset.map(tokenize_function)

    # Load Model
    print(f"Loading model: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto" if torch.cuda.is_available() else "cpu",
    )

    # LoRA Config (Parameter-Efficient Fine-Tuning)
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=8,
        lora_alpha=32,
        lora_dropout=0.1,
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    output_dir = os.path.join(project_root, "results")
    log_dir = os.path.join(project_root, "logs")

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=4,
        num_train_epochs=3,
        logging_dir=log_dir,
        save_strategy="epoch",
        logging_steps=10,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets,
    )

    trainer.train()

    save_path = os.path.join(project_root, "fine_tuned_slm")
    model.save_pretrained(save_path)
    print(f"Training Complete. Model saved to {save_path}")


if __name__ == "__main__":
    train()
