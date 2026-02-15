
import json
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load env
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("[ERROR] Missing Supabase credentials")
    exit()

supabase = create_client(url, key)

JSON_PATH = os.path.join("data", "combined_buyers.json")

def process_field(value):
    """Convert list to comma-separated string if needed, or handle None."""
    if value is None:
        return None
    if isinstance(value, list):
        # Filter out empty strings/None
        valid_items = [str(x) for x in value if x]
        return ", ".join(valid_items) if valid_items else None
    return str(value)

def import_data():
    if not os.path.exists(JSON_PATH):
        print(f"[ERROR] File not found: {JSON_PATH}")
        return

    print(f"[INFO] Reading {JSON_PATH}...")
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read JSON: {e}")
        return

    print(f"[INFO] Found {len(data)} records. Preparing for import...")

    batch_size = 100
    records = []
    
    for i, item in enumerate(data):
        # Map JSON fields to DB schema
        record = {
            "buyer_name": item.get("buyer_name", "Unknown"),
            "destination_country": item.get("country_english", item.get("destination_country")),
            "total_usd": item.get("total_usd", 0),
            "email": process_field(item.get("email")),
            "phone": process_field(item.get("phone")),
            "website": process_field(item.get("website")),
            "address": process_field(item.get("address"))
        }
        records.append(record)
        
        # Batch insert
        if len(records) >= batch_size:
            try:
                # Use insert instead of upsert since table is empty and constraint is missing
                supabase.table("mousa").insert(records).execute()
                print(f"[SUCCESS] Imported batch {i+1-batch_size} to {i+1}")
            except Exception as e:
                print(f"[ERROR] Error inserting batch: {e}")
            records = []

    # Final batch
    if records:
        try:
            supabase.table("mousa").insert(records).execute()
            print(f"[SUCCESS] Imported final batch of {len(records)}")
        except Exception as e:
            print(f"[ERROR] Error inserting final batch: {e}")

    print("\n[DONE] Import Complete!")

if __name__ == "__main__":
    import_data()
