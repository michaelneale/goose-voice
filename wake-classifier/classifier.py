#!/usr/bin/env python3
"""
classifier.py - Wake word classifier for detecting if text is addressed to Goose
"""

# Set environment variables before importing libraries
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import argparse
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

# Default model path
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model/final")

class GooseWakeClassifier:
    """Classifier to determine if text is addressed to Goose"""
    
    _instance = None  # Singleton instance
    
    @classmethod
    def get_instance(cls, model_path=MODEL_PATH):
        """Get or create a singleton instance of the classifier"""
        if cls._instance is None:
            cls._instance = cls(model_path)
        return cls._instance
    
    def __init__(self, model_path=MODEL_PATH):
        """Initialize the classifier with the given model path"""
        self.model_path = model_path
        self._load_model()
    
    def _load_model(self):
        """Load the model and tokenizer"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.classifier = pipeline(
                "text-classification", 
                model=self.model, 
                tokenizer=self.tokenizer,
                return_all_scores=True
            )
            print(f"Model loaded from {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("ERROR: Failed to load classifier model. System will not function correctly.")
            self.model = None
            self.tokenizer = None
            self.classifier = None
    
    def classify(self, text):
        """
        Classify if the input text is addressed to Goose
        
        Args:
            text (str): The text to classify
            
        Returns:
            bool: True if addressed to Goose, False otherwise
        """
        if not self.classifier:
            print("Error: No classifier model available")
            return False
            
        # Use the fine-tuned model
        try:
            result = self.classifier(text)
            scores = result[0]
            
            # Get the probability for "addressed to Goose" (label 1)
            addressed_score = next(score["score"] for score in scores if score["label"] == "LABEL_1")
            not_addressed_score = next(score["score"] for score in scores if score["label"] == "LABEL_0")
            
            # Determine classification
            is_addressed = addressed_score > not_addressed_score
            
            return is_addressed
        except Exception as e:
            print(f"Error during classification: {e}")
            return False
    
    def classify_with_details(self, text):
        """
        Classify with detailed information if the input text is addressed to Goose
        
        Args:
            text (str): The text to classify
            
        Returns:
            dict: Classification result with label and confidence
        """
        if not self.classifier:
            print("Error: No classifier model available")
            return {
                "text": text,
                "classification": "ERROR",
                "addressed_to_goose": False,
                "confidence": 0.0,
                "error": "No classifier model available"
            }
            
        # Use the fine-tuned model
        try:
            result = self.classifier(text)
            scores = result[0]
            
            # Get the probability for "addressed to Goose" (label 1)
            addressed_score = next(score["score"] for score in scores if score["label"] == "LABEL_1")
            not_addressed_score = next(score["score"] for score in scores if score["label"] == "LABEL_0")
            
            # Determine classification
            is_addressed = addressed_score > not_addressed_score
            
            return {
                "text": text,
                "classification": "ADDRESSED_TO_GOOSE" if is_addressed else "NOT_ADDRESSED_TO_GOOSE",
                "addressed_to_goose": is_addressed,
                "confidence": float(addressed_score if is_addressed else not_addressed_score)
            }
        except Exception as e:
            print(f"Error during classification: {e}")
            return {
                "text": text,
                "classification": "ERROR",
                "addressed_to_goose": False,
                "confidence": 0.0,
                "error": str(e)
            }

def main():
    """Parse command line arguments and run the classifier"""
    parser = argparse.ArgumentParser(description="Classify if text is addressed to Goose")
    parser.add_argument("text", help="The text to classify")
    parser.add_argument("--model", help="Path to the model directory", default=MODEL_PATH)
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()
    
    classifier = GooseWakeClassifier.get_instance(model_path=args.model)
    
    # Get both the boolean result and detailed result
    is_addressed = classifier.classify(args.text)
    details = classifier.classify_with_details(args.text)
    
    if args.json:
        print(json.dumps(details, indent=2))
    else:
        print(f"Text: {args.text}")
        print(f"Is addressed to Goose: {'Yes' if is_addressed else 'No'}")
        if is_addressed:
            print(f"Classification: {details['classification']}")
            print(f"Confidence: {details['confidence']:.4f}")
        if "note" in details:
            print(f"Note: {details['note']}")

if __name__ == "__main__":
    main()