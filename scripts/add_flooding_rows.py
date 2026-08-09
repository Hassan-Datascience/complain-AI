"""
Adds 18 new Water/Drainage flooding/burst-pipe rows to training_data.csv,
then retrains the priority model using the project's existing train_classifier.
Run from project root: python scripts/add_flooding_rows.py
"""
import os
import sys
import pandas as pd

DATA_PATH = "data/training_data.csv"

NEW_ROWS = [
    ("Burst water pipe on residential street is gushing water and flooding front gardens of several homes.", "Water/Drainage", "High"),
    ("Street is completely flooded from a burst main water pipe near the intersection of Oak and Maple.", "Water/Drainage", "Critical"),
    ("Water gushing out of cracked pipe on the pavement causing flooding across the entire road surface.", "Water/Drainage", "Critical"),
    ("Flooding in our street caused by burst underground water pipe has been going on since this morning.", "Water/Drainage", "High"),
    ("Burst pipe sending high-pressure water onto the road and flooding three residential properties.", "Water/Drainage", "High"),
    ("Water pressure has dropped to almost nothing in surrounding streets due to burst pipe nearby.", "Water/Drainage", "Medium"),
    ("Significant flooding on Maple Avenue after water main failure causing loss of pressure in area.", "Water/Drainage", "High"),
    ("Pavement is flooded and water is still gushing from a cracked supply pipe outside house 12.", "Water/Drainage", "High"),
    ("Low water pressure reported across multiple streets after burst pipe incident early this morning.", "Water/Drainage", "Medium"),
    ("Water flooding the road from a burst pipe near house number 12 on Maple Avenue since this morning.", "Water/Drainage", "High"),
    ("Gushing water from broken supply line flooding pavements and driveways along the entire street.", "Water/Drainage", "Critical"),
    ("Water pipe cracked open flooding roadway and front gardens since early morning, pressure dropped.", "Water/Drainage", "High"),
    ("Burst supply pipe is flooding the street and multiple gardens with no sign of repair team yet.", "Water/Drainage", "High"),
    ("Water main break causing water to flood the road, gardens flooded, pressure lost in nearby homes.", "Water/Drainage", "Critical"),
    ("Visible pipe fracture spraying water and flooding the pavement near residential houses all morning.", "Water/Drainage", "High"),
    ("Water pressure completely lost in our building since a pipe burst on the main road this morning.", "Water/Drainage", "Medium"),
    ("Flooded street and waterlogged gardens from burst municipal supply pipe, repair needed urgently.", "Water/Drainage", "High"),
    ("Multiple homes affected by flooding after underground supply pipe failed on residential avenue.", "Water/Drainage", "High"),
]

def main():
    # --- Step 1: Expand the dataset ---
    df = pd.read_csv(DATA_PATH)
    print(f"[1] Loaded {len(df)} rows from {DATA_PATH}")

    new_df = pd.DataFrame(NEW_ROWS, columns=["description", "category", "priority"])
    combined = pd.concat([df, new_df], ignore_index=True)
    combined.to_csv(DATA_PATH, index=False)
    print(f"[2] Dataset expanded to {len(combined)} rows (+{len(NEW_ROWS)} flooding rows)")

    # --- Step 2: Retrain via the existing project module ---
    print("[3] Retraining models via app.ml.train_classifier ...")
    from app.ml.train_classifier import train_and_save_models
    train_and_save_models(data_path=DATA_PATH, output_dir="app/ml")
    print("[4] Done.")

if __name__ == "__main__":
    main()
