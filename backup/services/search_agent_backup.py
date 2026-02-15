import os
import time
import json
import logging
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

# Import the advanced DeepSeekClient
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from deepseek_client import DeepSeekClient

# Load env variables (API Keys)
load_dotenv()

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchAgent:
    def __init__(self):
        """
        Initialize the SearchAgent with advanced DeepSeekClient.
        """
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            logger.warning("DEEPSEEK_API_KEY not found in environment variables.")
        
        # Initialize Advanced DeepSeek Client with Tool Calling
        self.client = DeepSeekClient(api_key=api_key)

    async def find_company_leads(self, company_name: str, country: str = "", callback=None) -> Dict[str, Any]:
        """
        Advanced 'Pro Scraper' Logic using DeepSeekClient with tool calling.
        
        Returns:
            Dict with keys: emails (list), phones (list), website (str), address (str)
        """
        if not company_name:
            return {"error": "Company name is required."}

        start_time = time.time()
        if callback: 
            callback(f"🔍 Starting intelligent search for: {company_name}")

        # System prompt for the AI agent
        system_prompt = f"""You are an expert Contact Information Researcher.

Your task: Find the contact details for the company "{company_name}" located in "{country}".

SEARCH STRATEGY:
1. First, search for the company's official website
2. Then fetch the website to find contact information
3. If needed, search for additional contact details

EXTRACTION RULES:
- Extract ALL emails found (multiple if available)
- Extract ALL phone numbers (international format preferred)
- Extract the main website URL
- Extract the physical address if available

IMPORTANT:
- Use web_search tool to find information
- Use fetch_page tool to extract data from websites
- Return results as a clean JSON object with these EXACT keys:
  {{
    "emails": ["email1@example.com", "email2@example.com"],
    "phones": ["+1234567890", "+0987654321"],
    "website": "https://company.com",
    "address": "123 Main St, City, Country"
  }}
- If a field is not found, use an empty list [] for emails/phones or null for website/address
- DO NOT include any markdown, explanations, or extra text in your final response
"""

        try:
            # Call the advanced extraction method
            if callback:
                callback("🤖 AI Agent is searching the web...")
            
            result_json, turns = await self.client.extract_company_data(
                system_prompt=system_prompt,
                buyer_name=company_name,
                country=country,
                model="deepseek-chat",
                callback=callback
            )
            
            if callback:
                callback(f"✅ Completed in {turns} search turns")

            # Parse the JSON response
            if result_json:
                try:
                    # Clean and parse JSON
                    extracted_data = json.loads(result_json)
                    
                    if callback:
                        callback(f"📊 Extracted data successfully")
                    
                    # Normalize the data structure
                    final_data = self._normalize_data(extracted_data, company_name, country)
                    
                    # Log success
                    elapsed = time.time() - start_time
                    logger.info(f"Search completed in {elapsed:.2f}s for {company_name}")
                    
                    return final_data
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON Parse Error: {e}")
                    logger.error(f"Raw response: {result_json}")
                    
                    if callback:
                        callback(f"⚠️ Warning: Model returned text instead of JSON")
                    
                    # Try to extract any contact info from the text response
                    return self._extract_from_text(result_json, company_name, country, callback)
            else:
                if callback:
                    callback("❌ No data returned from AI")
                return {
                    "status": "error",
                    "message": "AI search returned no results"
                }

        except Exception as e:
            logger.error(f"Search Agent Error: {e}")
            if callback:
                callback(f"❌ Error: {str(e)}")
            
            return {
                "status": "error",
                "message": f"Search failed: {str(e)}"
            }

    def _normalize_data(self, extracted_data: dict, company_name: str, country: str) -> dict:
        """
        Normalize extracted data to match expected format.
        """
        final_data = {
            "emails": [],
            "phones": [],
            "website": None,
            "address": None,
            "country": country,
            "status": "success"
        }
        
        # Process Emails
        raw_email = extracted_data.get("email") or extracted_data.get("emails")
        if isinstance(raw_email, list):
            final_data["emails"] = [e.strip() for e in raw_email if isinstance(e, str) and e.strip()]
        elif isinstance(raw_email, str) and raw_email.strip():
            # Split by comma if AI returned string
            final_data["emails"] = [e.strip() for e in raw_email.split(",") if e.strip()]
            
        # Process Phones
        raw_phone = extracted_data.get("phone") or extracted_data.get("phones")
        if isinstance(raw_phone, list):
            final_data["phones"] = [p.strip() for p in raw_phone if isinstance(p, str) and p.strip()]
        elif isinstance(raw_phone, str) and raw_phone.strip():
            final_data["phones"] = [p.strip() for p in raw_phone.split(",") if p.strip()]

        # Process Website
        raw_website = extracted_data.get("website")
        if isinstance(raw_website, str) and raw_website.strip():
            final_data["website"] = raw_website.strip()
        elif isinstance(raw_website, list) and len(raw_website) > 0:
            final_data["website"] = raw_website[0].strip()

        # Process Address
        raw_address = extracted_data.get("address")
        if isinstance(raw_address, str) and raw_address.strip():
            final_data["address"] = raw_address.strip()
        elif isinstance(raw_address, list) and len(raw_address) > 0:
            final_data["address"] = ", ".join([a.strip() for a in raw_address if a.strip()])

        return final_data

    def _extract_from_text(self, text: str, company_name: str, country: str, callback=None) -> dict:
        """
        Fallback: Try to extract contact info from plain text response.
        """
        import re
        
        if callback:
            callback("🔧 Attempting to parse text response...")
        
        # Extract emails using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Extract phone numbers
        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
        phones = re.findall(phone_pattern, text)
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        website = urls[0] if urls else None
        
        return {
            "emails": list(set(emails)),
            "phones": list(set(phones)),
            "website": website,
            "address": None,
            "country": country,
            "status": "partial",
            "message": "Extracted from text response (may be incomplete)"
        }


# Test block (run directly to verify)
if __name__ == "__main__":
    agent = SearchAgent()
    logging.info("Running test search...")
    
    def test_callback(msg):
        print(f"[CALLBACK] {msg}")
    
    res = asyncio.run(agent.find_company_leads("FERO METAL INC", "United States", callback=test_callback))
    print("\n=== FINAL RESULT ===")
    print(json.dumps(res, indent=2))
