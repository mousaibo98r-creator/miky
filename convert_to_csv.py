import json
import pandas as pd
import os

# Source and Target
SOURCE_FILE = r"c:\Users\salah\OneDrive\Desktop\ez\combined_buyers.json"
TARGET_FILE = r"c:\Users\salah\OneDrive\Desktop\ez\combined_buyers.csv"

def to_string(val):
    """Helper to flatten lists/dicts for CSV."""
    if isinstance(val, list):
        # Join list items with semicolon
        return "; ".join([str(v) for v in val if v])
    if isinstance(val, dict):
        # Dump dict as JSON string
        return json.dumps(val, ensure_ascii=False)
    return val

print(f"Reading {SOURCE_FILE}...")
try:
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records. converting...")

    df = pd.DataFrame(data)

    # Flatten specific columns
    list_cols = ["email", "phone", "website", "address", "exporters"]
    for col in list_cols:
        if col in df.columns:
            df[col] = df[col].apply(to_string)

    # Save to CSV
    df.to_csv(TARGET_FILE, index=False, encoding="utf-8-sig")
    print(f"Success! Saved to {TARGET_FILE}")

except Exception as e:
    print(f"Error: {e}")
