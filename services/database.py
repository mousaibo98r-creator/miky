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
    Upserts scavenged data into the 'leads' table.
    Fields: company_name, email, phone, website, address, last_scavenged_at.
    """
    supabase = get_supabase()
    if not supabase:
        logger.warning("Supabase credentials missing. Skipping save.")
        return {"status": "skipped", "reason": "no_credentials"}

    try:
        # Prepare payload
        # new_data is expected to have lists for emails/phones
        
        emails = new_data.get("emails", [])
        phones = new_data.get("phones", [])
        
        # Flatten for single columns (take first item), but store full list in raw if needed
        email_str = emails[0] if emails else None
        phone_str = phones[0] if phones else None
        
        # Helper to join if multiple
        if len(emails) > 1: email_str = "; ".join(emails)
        if len(phones) > 1: phone_str = "; ".join(phones)

        payload = {
            "company_name": company_name,
            "email": email_str,
            "phone": phone_str,
            "website": new_data.get("website"),
            "address": new_data.get("address"),
            "country": new_data.get("country"), # good to have
            "last_scavenged_at": datetime.utcnow().isoformat(),
            "raw_data": new_data # Optional: store full JSON
        }
        
        # Upsert based on company_name
        response = supabase.table("leads").upsert(payload, on_conflict="company_name").execute()
        
        return {"status": "success", "data": response.data}
        
    except Exception as e:
        logger.error(f"Supabase upsert failed: {e}")
        return {"status": "error", "message": str(e)}

def upsert_company_data(data: dict):
    # Wrapper or alias if needed for backward compatibility
    # But user specifically asked for 'save_scavenged_data'
    company = data.get("buyer_name") or data.get("company_name")
    return save_scavenged_data(company, data)
