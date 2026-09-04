import sys, types
import warnings

# Hide future version warnings to keep terminal logs clean
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 1. The VertexAI Bypass (Must be at the very top)
dummy_chat = types.ModuleType("langchain_community.chat_models.vertexai")
dummy_chat.ChatVertexAI = type("ChatVertexAI", (object,), {})
sys.modules["langchain_community.chat_models.vertexai"] = dummy_chat

import os
import pandas as pd
from datasets import Dataset
from ragas import evaluate

# 2. UPDATED: Import the Metric Classes
from ragas.metrics.collections import Faithfulness, ContextPrecision

# Ragas Wrappers for LlamaIndex
from ragas.llms import LlamaIndexLLMWrapper
from ragas.embeddings import LlamaIndexEmbeddingsWrapper
from llama_index.core import Settings

# Your Application Imports
from src.engine.config import setup_globals
from src.engine.retriever import get_query_engine

def run_evaluation():
    print("Setting up globals and loading Query Engine...")
    setup_globals()
    query_engine = get_query_engine()

    # Wrap your global Groq and MiniLM models for Ragas to use as the "Judge"
    evaluator_llm = LlamaIndexLLMWrapper(Settings.llm)
    evaluator_embeddings = LlamaIndexEmbeddingsWrapper(Settings.embed_model)

    questions = [
        "How does useState handle initial state functions?",
        "Can you call useState inside a loop or condition?"
    ]
    
    ground_truths = [
        "If you pass a function to useState, it is treated as an initializer function. It must be pure, take no arguments, and return a value.",
        "No, useState is a Hook, so you can only call it at the top level of your component or your own Hooks. You cannot call it inside loops or conditions."
    ]

    answers = []
    contexts = []

    print("Running test questions through the RAG pipeline...")
    for q in questions:
        response = query_engine.query(q)
        answers.append(str(response))
        contexts.append([node.get_content() for node in response.source_nodes])

    print("Formatting data for Ragas...")
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    dataset = Dataset.from_dict(data)

    print("Scoring Faithfulness and Context Precision...")
    
    # 3. UPDATED: Instantiate the metric classes with ()
    results = evaluate(
        dataset=dataset,
        metrics=[
            Faithfulness(),
            ContextPrecision()
        ],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings
    )

    df = results.to_pandas()
    print("\n=== Evaluation Results ===")
    print(df)
    
    df.to_csv("rag_evaluation_results.csv", index=False)
    print("\nSaved detailed results to rag_evaluation_results.csv")

if __name__ == "__main__":
    run_evaluation()