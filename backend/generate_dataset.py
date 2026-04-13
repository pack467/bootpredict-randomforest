"""
Dataset Generator
=================
Generates a realistic dummy dataset for football boots classification.
The dataset includes controlled noise to make classification non-trivial.
"""

import csv
import random
import os

def generate_dataset(output_path, num_samples=250):
    """
    Generate a CSV dataset with realistic football boot preferences.
    
    Labeling logic:
    - speed peminatan + striker/midfielder -> mostly speed_boot
    - control peminatan + any position -> mostly control_boot  
    - power peminatan + defender/goalkeeper -> mostly power_boot
    - Brand and position add realistic noise/variation
    
    Args:
        output_path: Path to save the CSV file
        num_samples: Number of samples to generate
    """
    random.seed(42)
    
    peminatan_options = ["speed", "control", "power"]
    brand_options = ["nike", "adidas", "puma", "mizuno", "umbro"]
    posisi_options = ["striker", "midfielder", "defender", "goalkeeper"]
    
    # Define probability distributions for labels based on peminatan + posisi
    label_rules = {
        # (peminatan, posisi): {label: probability}
        ("speed", "striker"):     {"speed_boot": 0.85, "control_boot": 0.10, "power_boot": 0.05},
        ("speed", "midfielder"):  {"speed_boot": 0.70, "control_boot": 0.25, "power_boot": 0.05},
        ("speed", "defender"):    {"speed_boot": 0.55, "control_boot": 0.20, "power_boot": 0.25},
        ("speed", "goalkeeper"):  {"speed_boot": 0.45, "control_boot": 0.25, "power_boot": 0.30},
        
        ("control", "striker"):   {"speed_boot": 0.15, "control_boot": 0.75, "power_boot": 0.10},
        ("control", "midfielder"):{"speed_boot": 0.10, "control_boot": 0.80, "power_boot": 0.10},
        ("control", "defender"):  {"speed_boot": 0.05, "control_boot": 0.75, "power_boot": 0.20},
        ("control", "goalkeeper"):{"speed_boot": 0.05, "control_boot": 0.70, "power_boot": 0.25},
        
        ("power", "striker"):     {"speed_boot": 0.15, "control_boot": 0.15, "power_boot": 0.70},
        ("power", "midfielder"):  {"speed_boot": 0.10, "control_boot": 0.25, "power_boot": 0.65},
        ("power", "defender"):    {"speed_boot": 0.05, "control_boot": 0.10, "power_boot": 0.85},
        ("power", "goalkeeper"):  {"speed_boot": 0.05, "control_boot": 0.10, "power_boot": 0.85},
    }
    
    rows = []
    
    for _ in range(num_samples):
        peminatan = random.choice(peminatan_options)
        brand = random.choice(brand_options)
        posisi = random.choice(posisi_options)
        
        # Get label probabilities
        probs = label_rules[(peminatan, posisi)]
        labels = list(probs.keys())
        weights = list(probs.values())
        
        # Select label based on probabilities
        label = random.choices(labels, weights=weights, k=1)[0]
        
        rows.append({
            "peminatan": peminatan,
            "brand": brand,
            "posisi": posisi,
            "label_sepatu": label
        })
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["peminatan", "brand", "posisi", "label_sepatu"])
        writer.writeheader()
        writer.writerows(rows)
    
    # Print distribution summary
    from collections import Counter
    label_counts = Counter(row["label_sepatu"] for row in rows)
    print(f"Dataset generated: {len(rows)} samples")
    print(f"Label distribution: {dict(label_counts)}")
    print(f"Saved to: {output_path}")
    
    return rows


if __name__ == "__main__":
    # Generate dataset when run directly
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.config import DATASET_CSV_PATH
    generate_dataset(DATASET_CSV_PATH, num_samples=250)
