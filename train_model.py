"""
train_model.py
----------------
Generates a training dataset from knowledge_base.py (each disease's
typical symptoms, with realistic random noise/variation added so the
model isn't just memorizing exact patterns), trains a RandomForest
classifier, and saves:

    model.pkl        - the trained sklearn model
    symptoms.pkl      - ordered list of symptom feature names
    label_encoder.pkl - maps model output <-> disease name

Run this ONCE before first using the app:
    python train_model.py
"""

import random
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from knowledge_base import SYMPTOMS, DISEASES

random.seed(42)
np.random.seed(42)

SAMPLES_PER_DISEASE = 120  # synthetic patient records generated per disease


def generate_dataset():
    rows = []
    labels = []

    for disease, (specialization, core_symptoms) in DISEASES.items():
        for _ in range(SAMPLES_PER_DISEASE):
            row = {s: 0 for s in SYMPTOMS}

            # Each core symptom appears most of the time (85%) but not
            # always -> makes the model robust to partial symptom entry.
            for s in core_symptoms:
                row[s] = 1 if random.random() < 0.85 else 0

            # Small chance of an unrelated symptom too (real patients
            # are messy) - keeps the model from overfitting to exact sets.
            for s in SYMPTOMS:
                if s not in core_symptoms and random.random() < 0.04:
                    row[s] = 1

            rows.append(row)
            labels.append(disease)

    df = pd.DataFrame(rows)
    df["disease"] = labels
    return df


def main():
    print("Generating training dataset from knowledge_base.py ...")
    df = generate_dataset()
    print(f"  {len(df)} rows, {len(SYMPTOMS)} symptom features, {df['disease'].nunique()} diseases")

    X = df[SYMPTOMS]
    y_raw = df["disease"]

    encoder = LabelEncoder()
    y = encoder.fit_transform(y_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training RandomForestClassifier ...")
    model = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"  Test accuracy: {acc * 100:.2f}%")

    joblib.dump(model, "model.pkl")
    joblib.dump(SYMPTOMS, "symptoms.pkl")
    joblib.dump(encoder, "label_encoder.pkl")
    print("Saved model.pkl, symptoms.pkl, label_encoder.pkl")


if __name__ == "__main__":
    main()
