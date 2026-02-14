import os
import logging
from datetime import datetime
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

def save_scavenged_data(company_name, new_data):
    """
    Upserts scavenged data into the 'mousa' table.
    Identity Column: buyer_name
    Fields Updated: email, phone, website, address
    """
    supabase = get_supabase()
    if not supabase:
        logger.warning("Supabase credentials missing. Skipping save.")
        return {"status": "skipped", "reason": "no_credentials"}

    try:
        # Robustness: Strip whitespace
        clean_name = company_name.strip()
        print(f"DEBUG: Saving to '{clean_name}'...")
        
        # 1. Prepare Data
        # Ensure we handled lists correctly (join with comma as requested)
        emails = new_data.get("emails", [])
        phones = new_data.get("phones", [])
        
        email_str = ", ".join(emails) if isinstance(emails, list) and emails else None
        phone_str = ", ".join(phones) if isinstance(phones, list) and phones else None
        
        website = new_data.get("website")
        if isinstance(website, list):
             website = ", ".join(website)
             
        address = new_data.get("address")
        if isinstance(address, list):
             address = ", ".join(address)

        # 2. Construct Payload
        payload = {
            "buyer_name": clean_name,  # Primary Key
            "email": email_str,
            "phone": phone_str,
            "website": website,
            "address": address,
            "last_scavenged_at": datetime.utcnow().isoformat()
        }
        
        # 3. Upsert
        response = supabase.table("mousa").upsert(payload, on_conflict="buyer_name").execute()
        
        return {"status": "success", "data": response.data}
        
    except Exception as e:
        logger.error(f"Supabase upsert failed: {e}")
        return {"status": "error", "message": str(e)}

def upsert_company_data(data: dict):
    # Alias for backward compatibility if needed, but app.py uses save_scavenged_data
    company = data.get("buyer_name") or data.get("company_name")
    return save_scavenged_data(company, data)
