"""
Training script for sentiment analysis model
Uses MLflow for experiment tracking
"""
import os
import sys
import argparse
import mlflow
import mlflow.pytorch
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
import pandas as pd
import numpy as np
from tqdm import tqdm
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


class SentimentDataset(Dataset):
    """Dataset for sentiment analysis training"""

    def __init__(self, texts: list, labels: list, tokenizer, max_length: int = 256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }


def load_data(data_path: str) -> tuple:
    """
    Load training data

    Args:
        data_path: Path to CSV file with columns: text, sentiment

    Returns:
        Tuple of (texts, labels)
    """
    df = pd.read_csv(data_path)

    # Map sentiments to labels
    label_map = {'negative': 0, 'neutral': 1, 'positive': 2}
    df['label'] = df['sentiment'].map(label_map)

    return df['text'].tolist(), df['label'].tolist()


def train_epoch(model, dataloader, optimizer, device, scheduler=None):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    predictions = []
    true_labels = []

    progress_bar = tqdm(dataloader, desc="Training")

    for batch in progress_bar:
        optimizer.zero_grad()

        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['label'].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss

        loss.backward()
        optimizer.step()

        if scheduler:
            scheduler.step()

        total_loss += loss.item()

        # Get predictions
        preds = torch.argmax(outputs.logits, dim=1)
        predictions.extend(preds.cpu().numpy())
        true_labels.extend(labels.cpu().numpy())

        # Update progress bar
        progress_bar.set_postfix({'loss': loss.item()})

    avg_loss = total_loss / len(dataloader)
    accuracy = accuracy_score(true_labels, predictions)
    f1 = f1_score(true_labels, predictions, average='weighted')

    return avg_loss, accuracy, f1


def evaluate(model, dataloader, device):
    """Evaluate model"""
    model.eval()
    total_loss = 0
    predictions = []
    true_labels = []

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss

            total_loss += loss.item()

            preds = torch.argmax(outputs.logits, dim=1)
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())

    avg_loss = total_loss / len(dataloader)
    accuracy = accuracy_score(true_labels, predictions)
    f1 = f1_score(true_labels, predictions, average='weighted')

    return avg_loss, accuracy, f1, predictions, true_labels


def train_model(config: Dict[str, Any]):
    """
    Main training function

    Args:
        config: Training configuration
    """
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Start MLflow run
    with mlflow.start_run():
        # Log parameters
        mlflow.log_params(config)

        # Load data
        print("Loading data...")
        texts, labels = load_data(config['data_path'])

        # Split data
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels,
            test_size=config['val_split'],
            random_state=config['seed'],
            stratify=labels
        )

        print(f"Training samples: {len(train_texts)}")
        print(f"Validation samples: {len(val_texts)}")

        # Initialize tokenizer and model
        print("Initializing model...")
        tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
        model = AutoModelForSequenceClassification.from_pretrained(
            config['model_name'],
            num_labels=config['num_labels']
        )
        model.to(device)

        # Create datasets
        train_dataset = SentimentDataset(train_texts, train_labels, tokenizer, config['max_length'])
        val_dataset = SentimentDataset(val_texts, val_labels, tokenizer, config['max_length'])

        # Create dataloaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=config['batch_size'],
            shuffle=True,
            num_workers=config['num_workers']
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=config['batch_size'],
            shuffle=False,
            num_workers=config['num_workers']
        )

        # Initialize optimizer
        optimizer = AdamW(model.parameters(), lr=config['learning_rate'])

        # Training loop
        best_f1 = 0
        patience_counter = 0

        for epoch in range(config['epochs']):
            print(f"\nEpoch {epoch + 1}/{config['epochs']}")

            # Train
            train_loss, train_acc, train_f1 = train_epoch(model, train_loader, optimizer, device)

            # Evaluate
            val_loss, val_acc, val_f1, _, _ = evaluate(model, val_loader, device)

            # Log metrics
            mlflow.log_metrics({
                'train_loss': train_loss,
                'train_accuracy': train_acc,
                'train_f1': train_f1,
                'val_loss': val_loss,
                'val_accuracy': val_acc,
                'val_f1': val_f1
            }, step=epoch)

            print(f"Train Loss: {train_loss:.4f}, Acc: {train_acc:.4f}, F1: {train_f1:.4f}")
            print(f"Val Loss: {val_loss:.4f}, Acc: {val_acc:.4f}, F1: {val_f1:.4f}")

            # Save best model
            if val_f1 > best_f1:
                best_f1 = val_f1
                patience_counter = 0

                # Save model
                model_path = os.path.join(config['output_dir'], 'best_model')
                model.save_pretrained(model_path)
                tokenizer.save_pretrained(model_path)

                # Log model to MLflow
                mlflow.pytorch.log_model(model, "model")

                print(f"✓ Saved best model (F1: {best_f1:.4f})")
            else:
                patience_counter += 1
                if patience_counter >= config['patience']:
                    print(f"Early stopping triggered after {epoch + 1} epochs")
                    break

        # Final evaluation
        print("\nFinal evaluation on validation set:")
        val_loss, val_acc, val_f1, predictions, true_labels = evaluate(model, val_loader, device)

        # Classification report
        print("\nClassification Report:")
        print(classification_report(true_labels, predictions, target_names=['negative', 'neutral', 'positive']))

        # Log final metrics
        mlflow.log_metrics({
            'final_val_accuracy': val_acc,
            'final_val_f1': val_f1,
            'best_f1': best_f1
        })

        print(f"\n✓ Training complete! Best F1: {best_f1:.4f}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Train sentiment analysis model")
    parser.add_argument('--data_path', type=str, required=True, help='Path to training data CSV')
    parser.add_argument('--model_name', type=str, default='distilbert-base-uncased', help='Pretrained model name')
    parser.add_argument('--output_dir', type=str, default='./models/sentiment', help='Output directory')
    parser.add_argument('--epochs', type=int, default=5, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=16, help='Batch size')
    parser.add_argument('--learning_rate', type=float, default=2e-5, help='Learning rate')
    parser.add_argument('--max_length', type=int, default=256, help='Max sequence length')
    parser.add_argument('--val_split', type=float, default=0.2, help='Validation split')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--patience', type=int, default=3, help='Early stopping patience')
    parser.add_argument('--num_workers', type=int, default=4, help='Number of dataloader workers')

    args = parser.parse_args()

    # Configuration
    config = {
        'data_path': args.data_path,
        'model_name': args.model_name,
        'output_dir': args.output_dir,
        'epochs': args.epochs,
        'batch_size': args.batch_size,
        'learning_rate': args.learning_rate,
        'max_length': args.max_length,
        'val_split': args.val_split,
        'seed': args.seed,
        'patience': args.patience,
        'num_workers': args.num_workers,
        'num_labels': 3  # negative, neutral, positive
    }

    # Create output directory
    os.makedirs(config['output_dir'], exist_ok=True)

    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")  # Update with your MLflow server
    mlflow.set_experiment("sentiment-analysis-training")

    # Train model
    train_model(config)


if __name__ == "__main__":
    main()
