import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# CSV path
csv_path = r"app\vector_database\MTS-Dialog-Augmented-TrainingSet-1-En-FR-EN-2402-Pairs.csv"
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file not found: {csv_path}")

df = pd.read_csv(csv_path, encoding="utf-8")

# Extract patient lines
patient_texts = []

for dialogue in df['dialogue'].dropna():
    lines = dialogue.split("\n")
    for line in lines:
        line = line.strip()
        if line.lower().startswith("patient:"):
            patient_texts.append(line[len("Patient:"):].strip())

if len(patient_texts) == 0:
    raise ValueError("No patient lines found in CSV.")

print(f"Extracted patient lines: {len(patient_texts)}")
print(patient_texts[:5])  # Show first 5 patient lines

# Generate embeddings
embeddings = model.encode(patient_texts, convert_to_numpy=True).astype("float32")

# Build FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save vector DB
kb_path = "patient_kb.pkl"
with open(kb_path, "wb") as f:
    pickle.dump({
        "index": index,
        "texts": patient_texts,
        "model_name": "all-MiniLM-L6-v2"
    }, f)

print(f"Knowledge base created successfully → {kb_path}")
