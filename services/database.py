import os
import logging
from supabase import create_client, Client

# Configure logger
logger = logging.getLogger(__name__)

def get_supabase() -> Client:
    """Initialize Supabase client from environment variables."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        return None
        
    try:
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")
        return None

def upsert_company_data(data: dict):
    """
    Upserts company data into the 'leads' table.
    
    Expected data dictionary format:
    {
        "buyer_name": "Company Name",
        "country": "Country Name",
        "emails": ["a@b.com", ...],
        "phones": ["+123...", ...],
        "website": "http://...",
        "address": "123 St..."
    }
    """
    supabase = get_supabase()
    if not supabase:
        logger.warning("Supabase credentials missing. Flipping to dry-run (no-op).")
        return {"status": "skipped", "reason": "no_credentials"}

    try:
        # Prepare payload for 'leads' table
        # We assume the table has columns: company_name (PK/Unique), country, website, email, phone, address, raw_data (json)
        # We need to ensure we don't crash on schema mismatches, so we'll wrap in try/except
        
        payload = {
            "company_name": data.get("buyer_name"),
            "country": data.get("country"),
            "website": data.get("website"),
            # Store primary contacts in columns, full list in raw_data
            "email": data.get("emails")[0] if data.get("emails") else None,
            "phone": data.get("phones")[0] if data.get("phones") else None,
            "address": data.get("address"),
            "raw_data": data # Backup full scavenged data
        }
        
        # Use company_name as the conflict target if possible, or let Supabase handle PK
        # Assuming 'company_name' is unique or we rely on ID. 
        # For upsert to work effectively without ID, we need a unique constraint on company_name.
        
        response = supabase.table("leads").upsert(payload, on_conflict="company_name").execute()
        
        return {"status": "success", "data": response.data}
        
    except Exception as e:
        logger.error(f"Supabase upsert failed: {e}")
        return {"status": "error", "message": str(e)}
