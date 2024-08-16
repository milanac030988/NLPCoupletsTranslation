import datasets
import pandas as pd
import re
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import torch
import argparse
from transformers import MarianTokenizer, MarianMTModel, Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq
from datasets import load_dataset, Dataset, DatasetDict
from sklearn.model_selection import train_test_split
from utils import *


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_NAME_TO_FINE_TUNE = "Helsinki-NLP/opus-mt-zh-vi"
DEFAULT_OUPUT_MODEL_DIR = os.path.abspath(SCRIPT_DIR + "\\..\\output\\model\\transformer")
DEFAULT_DATASET_PATH = os.path.abspath(SCRIPT_DIR + "\\..\\output\\data\\dataset\\primary_couplets_dataset.csv")

# Preprocess function to normalize text
def preprocess_text(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r',', '', text)  # Remove commas
    text = re.sub(r'_', ' ', text)  # Replace underscores with spaces
    text = re.sub(r'"', '', text)  # Remove double quotes
    text = re.sub(r'\(\d+\)', '', text)  # Remove patterns like '(1)', '(2)', etc.
    text = re.sub(r'•', '', text)  # Remove bullet points
    text = re.sub(r'[()]', '', text)  # Remove parentheses
    text = text.lower()  # Lowercase
    return text

def main(dataset_path, source_col, target_col, outdir, splits, train_args):
    # Load the dataset
    df = pd.read_csv(dataset_path, encoding='utf-8-sig')

    # Split couplets into separate lines
    sources = []
    targets = []
    cn_original = []
    vi_original = []
    for _, row in df.iterrows():
        cn_lines = row[source_col].split('\n')
        vi_lines = row[target_col].split('\n')
        if len(cn_lines) == len(vi_lines):
            for cn_sentence,vi_sentence in zip(cn_lines, vi_lines):
                cn_sentence = ''.join([char if Utils.is_chinese_char(char) else '' for char in cn_sentence]).strip()
                sources.append(cn_sentence)
            # for vi_sentence in vi_lines:
                vi_sentence = Utils.normalize_text(vi_sentence)
                targets.append(vi_sentence)
            cn_original.extend([row[source_col], ";Filled row;"])
            vi_original.extend([row[target_col], ";Filled row;"])

    # Create a new DataFrame with separated lines
    separated_df = pd.DataFrame({'cn': cn_original, 'vi': vi_original,'source': sources, 'target': targets})

    # Preprocess the data
    separated_df['source'] = separated_df['source'].apply(preprocess_text)
    separated_df['target'] = separated_df['target'].apply(preprocess_text)

    # Split the dataset into train and validation sets
    train_df, test_df = train_test_split(separated_df, test_size=splits)
    train_df_no_filled = train_df[train_df['cn'] != ";Filled row;"]
    test_df_no_filled = test_df[test_df['vi'] != ";Filled row;"]

    # Save the training and test sets to CSV files without ";Filled row;"
    train_df_no_filled[['cn', 'vi']].to_csv(f'{outdir}/train.csv', index=False, encoding='utf-8-sig')
    test_df_no_filled[['cn', 'vi']].to_csv(f'{outdir}/test.csv', index=False, encoding='utf-8-sig')

    # Convert the dataframes to Hugging Face datasets
    train_dataset = Dataset.from_pandas(train_df[['source', 'target']])
    test_dataset = Dataset.from_pandas(test_df[['source', 'target']])
    dataset = DatasetDict({"train": train_dataset, "test": test_dataset})

    # Load the tokenizer and model
    model_name = MODEL_NAME_TO_FINE_TUNE
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    # Check if CUDA is available and move the model to GPU if possible
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    # Preprocess the data for the model
    def preprocess_function(examples):
        model_inputs = tokenizer(examples['source'], max_length=36, truncation=True, padding="max_length")
        labels = tokenizer(examples['target'], max_length=36, truncation=True, padding="max_length")
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized_datasets = dataset.map(preprocess_function, batched=True)

    # Define training arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=train_args['output_dir'],
        evaluation_strategy=train_args['evaluation_strategy'],
        learning_rate=train_args['learning_rate'],
        per_device_train_batch_size=train_args['per_device_train_batch_size'],
        per_device_eval_batch_size=train_args['per_device_eval_batch_size'],
        weight_decay=train_args['weight_decay'],
        save_total_limit=train_args['save_total_limit'],
        num_train_epochs=train_args['num_train_epochs'],
        predict_with_generate=train_args['predict_with_generate'],
        fp16=train_args['fp16'],
        warmup_steps=train_args['warmup_steps'],
        gradient_accumulation_steps=train_args['gradient_accumulation_steps']
    )

    # Define data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # Initialize the Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        data_collator=data_collator,
        tokenizer=tokenizer
    )

    # Fine-tune the model
    trainer.train()

    # Save the model and tokenizer
    model.save_pretrained(f"{outdir}/fine_tuned_model")
    tokenizer.save_pretrained(f"{outdir}/fine_tuned_model")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fine-tune a MarianMT model on a custom dataset.')
    parser.add_argument('--dataset', default=DEFAULT_DATASET_PATH, help='Path to CSV dataset file')
    parser.add_argument('--source', default='cn', help='Source column name')
    parser.add_argument('--target', default='vi', help='Target column name')
    parser.add_argument('--outdir', default=DEFAULT_OUPUT_MODEL_DIR, help='Directory to store model, test and train dataset')
    parser.add_argument('--splits', type=float, default=0.1, help='Percent to split source dataset to test and train')

    # Training arguments
    parser.add_argument('--output_dir', default=DEFAULT_OUPUT_MODEL_DIR + '/results', help='Output directory for results')
    parser.add_argument('--evaluation_strategy', default='epoch', help='Evaluation strategy')
    parser.add_argument('--learning_rate', type=float, default=1e-5, help='Learning rate')
    parser.add_argument('--per_device_train_batch_size', type=int, default=16, help='Batch size for training')
    parser.add_argument('--per_device_eval_batch_size', type=int, default=16, help='Batch size for evaluation')
    parser.add_argument('--weight_decay', type=float, default=0.01, help='Weight decay')
    parser.add_argument('--save_total_limit', type=int, default=3, help='Total limit for saved models')
    parser.add_argument('--num_train_epochs', type=int, default=20, help='Number of training epochs')
    parser.add_argument('--predict_with_generate', type=bool, default=True, help='Predict with generate')
    parser.add_argument('--fp16', type=bool, default=torch.cuda.is_available(), help='Enable mixed precision training if using CUDA')
    parser.add_argument('--warmup_steps', type=int, default=500, help='Warm-up steps')
    parser.add_argument('--gradient_accumulation_steps', type=int, default=2, help='Gradient accumulation steps')

    args = parser.parse_args()

    train_args = {
        'output_dir': args.output_dir,
        'evaluation_strategy': args.evaluation_strategy,
        'learning_rate': args.learning_rate,
        'per_device_train_batch_size': args.per_device_train_batch_size,
        'per_device_eval_batch_size': args.per_device_eval_batch_size,
        'weight_decay': args.weight_decay,
        'save_total_limit': args.save_total_limit,
        'num_train_epochs': args.num_train_epochs,
        'predict_with_generate': args.predict_with_generate,
        'fp16': args.fp16,
        'warmup_steps': args.warmup_steps,
        'gradient_accumulation_steps': args.gradient_accumulation_steps
    }

    main(args.dataset, args.source, args.target, args.outdir, args.splits, train_args)