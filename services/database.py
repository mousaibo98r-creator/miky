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
        logger.error("SUPABASE_URL or SUPABASE_KEY not found in environment")
        return None
        
    try:
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")
        return None

def save_scavenged_data(company_name, new_data):
    """
    Upserts scavenged data into the 'mousa' table with enhanced logging.
    
    Args:
        company_name: The buyer_name (primary key)
        new_data: Dict with keys: emails, phones, website, address
        
    Returns:
        Dict with status: success/error and optional message
    """
    supabase = get_supabase()
    if not supabase:
        logger.warning("Supabase credentials missing. Skipping save.")
        return {"status": "error", "message": "Supabase not configured"}

    try:
        # Clean company name
        clean_name = company_name.strip()
        logger.info(f"Saving scavenged data for: {clean_name}")
        
        # Process Emails
        emails = new_data.get("emails", [])
        if isinstance(emails, list) and emails:
            # Filter out invalid emails
            valid_emails = [e for e in emails if e and '@' in e]
            email_str = ", ".join(valid_emails)
        else:
            email_str = None
        
        # Process Phones
        phones = new_data.get("phones", [])
        if isinstance(phones, list) and phones:
            # Clean phone numbers
            valid_phones = [p for p in phones if p and len(p) >= 10]
            phone_str = ", ".join(valid_phones)
        else:
            phone_str = None
        
        # Process Website
        website = new_data.get("website")
        if isinstance(website, list) and website:
            website = website[0]  # Take first if list
        if not website or website == "null":
            website = None
             
        # Process Address
        address = new_data.get("address")
        if isinstance(address, list) and address:
            address = ", ".join([a for a in address if a])
        if not address or address == "null":
            address = None

        # Construct Payload
        payload = {
            "buyer_name": clean_name,  # Primary Key
            "email": email_str,
            "phone": phone_str,
            "website": website,
            "address": address,
            "last_scavenged_at": datetime.utcnow().isoformat()
        }
        
        # Log what we're saving
        logger.info(f"Payload: emails={bool(email_str)}, phones={bool(phone_str)}, website={bool(website)}, address={bool(address)}")
        
        # Upsert to Supabase
        response = supabase.table("mousa").upsert(payload, on_conflict="buyer_name").execute()
        
        if response.data:
            logger.info(f"✅ Successfully saved data for {clean_name}")
            return {
                "status": "success",
                "data": response.data,
                "message": f"Saved {len(valid_emails) if email_str else 0} emails, {len(valid_phones) if phone_str else 0} phones"
            }
        else:
            logger.warning(f"Upsert returned no data for {clean_name}")
            return {"status": "warning", "message": "Upsert completed but no data returned"}
        
    except Exception as e:
        logger.error(f"Supabase upsert failed for {company_name}: {e}")
        return {"status": "error", "message": str(e)}

def upsert_company_data(data: dict):
    """Alias for backward compatibility."""
    company = data.get("buyer_name") or data.get("company_name")
    return save_scavenged_data(company, data)

def fetch_all_buyers():
    """
    Fetches ALL records from the 'mousa' table.
    
    Returns:
        List of dicts or empty list on error
    """
    supabase = get_supabase()
    if not supabase:
        logger.error("Cannot fetch buyers: Supabase not configured")
        return []
    
    try:
        # Fetch all rows (Supabase default limit is 1000)
        # For larger datasets, implement pagination
        response = supabase.table("mousa").select("*").execute()
        
        if response.data:
            logger.info(f"Fetched {len(response.data)} buyer records")
            return response.data
        else:
            logger.warning("No buyer data found in database")
            return []
            
    except Exception as e:
        logger.error(f"Failed to fetch buyers: {e}")
        return []

def bulk_upsert_buyers(records: list):
    """
    Bulk upsert a list of buyer records to 'mousa'.
    
    Args:
        records: List of dicts with buyer data
        
    Returns:
        Dict with status and message
    """
    supabase = get_supabase()
    if not supabase:
        return {"status": "error", "message": "Supabase not configured"}
        
    if not records:
        return {"status": "skipped", "message": "No records to save"}

    try:
        logger.info(f"Bulk upserting {len(records)} records")
        
        # Supabase bulk upsert
        response = supabase.table("mousa").upsert(records, on_conflict="buyer_name").execute()
        
        if response.data:
            logger.info(f"✅ Successfully upserted {len(response.data)} records")
            return {"status": "success", "data": response.data}
        else:
            return {"status": "warning", "message": "Bulk upsert completed but no data returned"}
            
    except Exception as e:
        logger.error(f"Bulk upsert failed: {e}")
        return {"status": "error", "message": str(e)}

def update_contact_timestamp(company_name: str):
    """
    Update last_contacted_at timestamp for email tracking.
    
    Args:
        company_name: The buyer_name to update
        
    Returns:
        Dict with status
    """
    supabase = get_supabase()
    if not supabase:
        return {"status": "error", "message": "Supabase not configured"}
    
    try:
        payload = {
            "buyer_name": company_name.strip(),
            "last_contacted_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("mousa").upsert(payload, on_conflict="buyer_name").execute()
        
        if response.data:
            logger.info(f"Updated contact timestamp for {company_name}")
            return {"status": "success"}
        else:
            return {"status": "warning", "message": "Update completed but no data returned"}
            
    except Exception as e:
        logger.error(f"Failed to update contact timestamp: {e}")
        return {"status": "error", "message": str(e)}
