import json
import os
import re
import logging
import asyncio

import requests
from bs4 import BeautifulSoup
from openai import AsyncOpenAI

# Configure logger
logger = logging.getLogger(__name__)

class SearchAgent:
    """
    The 'Brain' for scavenging company data.
    Uses DuckDuckGo for discovery and DeepSeek via OpenAI for extraction/cleaning.
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not found. Agent will fail if called.")
            
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

    async def find_company_leads(self, company_name, country, callback=None):
        """
        Main entry point. Finds leads for a company.
        Returns a dict: {emails: [], phones: [], website: str, address: str}
        """
        query = f"{company_name} {country} official website contact email phone"
        
        if callback: callback(f"Searching for '{company_name}'...")
        
        # 1. Search DB/Web
        search_results = self._perform_search(query)
        
        if not search_results or "error" in search_results[0]:
             error_msg = search_results[0].get("error", "No results")
             if callback: callback(f"Search failed: {error_msg}")
             return {"status": "error", "message": error_msg}

        # 2. Pick best URL and fetch
        # We look for the first non-directory URL
        target_url = None
        for r in search_results:
             if r.get("url"):
                 target_url = r["url"]
                 break
        
        raw_page_content = ""
        if target_url:
            if callback: callback(f"Fetching {target_url}...")
            page_data = self._fetch_page(target_url)
            # Combine snippets and page content for the AI
            raw_page_content = page_data.get("page_text_preview", "")
            # Also grab regex-found contacts as backup
            regex_contacts = {
                "emails": page_data.get("emails_found", []),
                "phones": page_data.get("phones_found", [])
            }
        else:
            regex_contacts = {}

        # 3. Clean with DeepSeek
        if callback: callback("Analyzing data with AI...")
        
        # Construct context for AI
        context = f"""
        COMPANY: {company_name}
        COUNTRY: {country}
        
        SEARCH RESULTS:
        {json.dumps(search_results[:3])}
        
        WEBPAGE CONTENT ({target_url}):
        {raw_page_content[:4000]}
        """
        
        system_prompt = (
            "You are a data extraction engine. "
            "Extract the Website, Phone, Email, and Address into a strict JSON format. "
            "Keys: emails (list), phones (list), website (string), address (string). "
            "Do not say anything else. Return ONLY the JSON."
        )

        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ]
            )
            content = response.choices[0].message.content
            cleaned_data = self._parse_json(content)
            
            # Merge regex findings if AI missed them (optional, but good for robustness)
            if isinstance(cleaned_data, dict):
                if not cleaned_data.get("emails") and regex_contacts.get("emails"):
                    cleaned_data["emails"] = regex_contacts["emails"]
                if not cleaned_data.get("phones") and regex_contacts.get("phones"):
                    cleaned_data["phones"] = regex_contacts["phones"]
                if not cleaned_data.get("website") and target_url:
                    cleaned_data["website"] = target_url
            
            return cleaned_data

        except Exception as e:
            logger.error(f"AI Extraction failed: {e}")
            return {"status": "error", "message": str(e)}

    def _perform_search(self, query):
        try:
            from duckduckgo_search import DDGS
            results = list(DDGS().text(query, max_results=5))
            clean_results = []
            for r in results:
                clean_results.append({
                    "title": r.get("title"),
                    "url": r.get("href"),
                    "snippet": r.get("body")
                })
            return clean_results
        except Exception as e:
            return [{"error": str(e)}]

    def _fetch_page(self, url):
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            resp.raise_for_status()
            text = BeautifulSoup(resp.text, 'html.parser').get_text(separator=' ')
            
            # Basic Regex for backup
            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
            phones = re.findall(r'\+?\d{10,15}', text)
            
            return {
                "page_text_preview": text,
                "emails_found": list(set(emails)),
                "phones_found": list(set(phones))
            }
        except Exception:
            return {}

    def _parse_json(self, text):
        if not text: return {}
        try:
            # Strip markdown
            text = text.strip()
            if "```" in text:
                text = re.search(r'```(?:json)?(.*?)```', text, re.DOTALL).group(1)
            return json.loads(text.strip())
        except Exception:
            # Fallback: simple dict error
            return {"status": "error", "message": "Failed to parse AI JSON", "raw": text}
