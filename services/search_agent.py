import os
import time
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional

from duckduckgo_search import DDGS
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load env variables (API Keys)
load_dotenv()

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchAgent:
    def __init__(self):
        """
        Initialize the SearchAgent with DeepSeek client (OpenAI compatible).
        """
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            logger.warning("DEEPSEEK_API_KEY not found in environment variables.")
        
        # Initialize DeepSeek Client
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )

    async def _search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform a DuckDuckGo search and return results.
        Handles rate limits gracefully.
        """
        results = []
        try:
            # Synchronous DDGS call inside async method (could be wrapped in run_in_executor if needed)
            # DDGS() context manager limits scope
            with DDGS() as ddgs:
                search_gen = ddgs.text(query, max_results=max_results)
                for r in search_gen:
                    results.append({
                        "title": r.get("title", ""),
                        "href": r.get("href", ""),
                        "body": r.get("body", "")
                    })
            logger.info(f"Found {len(results)} results for query: '{query}'")
        except Exception as e:
            logger.error(f"DuckDuckGo search error for query '{query}': {e}")
        
        return results

    async def find_company_leads(self, company_name: str, country: str = "", callback=None) -> Dict[str, Any]:
        """
        Advanced 'Pro Scraper' Logic:
        1. Multi-Query Strategy (3 distinct searches).
        2. Aggregation of search snippets.
        3. DeepSeek Analysis for structured JSON extraction.
        4. Fallback for Website URL.
        """
        if not company_name:
            return {"error": "Company name is required."}

        start_time = time.time()
        if callback: callback(f"Starting advanced search for: {company_name}")

        # --- 1. Multi-Query Strategy ---
        queries = [
            f"{company_name} {country} official website contact",
            f"{company_name} {country} email address phone number",
            f"{company_name} {country} export contact"
        ]

        all_results = []
        seen_urls = set()
        
        # Execute searches (sequentially to avoid rate limits, or carefully async)
        for q in queries:
            if callback: callback(f"Searching: {q}...")
            results = await self._search_duckduckgo(q, max_results=4)
            
            # Deduplicate and Collect
            for r in results:
                if r['href'] not in seen_urls:
                    all_results.append(r)
                    seen_urls.add(r['href'])
            
            # Brief pause to be polite to DDG
            await asyncio.sleep(1)

        if not all_results:
            if callback: callback("No search results found.")
            return {"status": "error", "message": "No search results found."}

        # --- 2. Aggregate Text Context ---
        # Limit to reasonable size for LLM context window
        context_parts = []
        for i, r in enumerate(all_results[:15]): # Top 15 unique results
            context_parts.append(f"Result {i+1}:")
            context_parts.append(f"Title: {r['title']}")
            context_parts.append(f"URL: {r['href']}")
            context_parts.append(f"Snippet: {r['body']}")
            context_parts.append("---")
        
        combined_context = "\n".join(context_parts)
        
        # --- 3. DeepSeek Intelligence ---
        if callback: callback("Analyzing aggregated data with DeepSeek...")
        
        system_prompt = (
            "You are a Data Extraction Expert. "
            "Analyze the following search results and extract the Website, Email, Phone, and Address. "
            "If multiple exist, list them all separated by commas. "
            "Return strictly JSON with keys: email (list), phone (list), website (string), address (string). "
            "If a field is not found, return null or empty list."
        )

        user_prompt = f"""
        Target Company: {company_name}
        Country Context: {country}
        
        Search Results Aggregation:
        {combined_context}
        """

        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1, # Low temp for factual extraction
                response_format={ "type": "json_object" } # Force JSON if supported, else rely on prompt
            )
            
            content = response.choices[0].message.content
            
            # Robust JSON Parsing
            try:
                # Remove code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[0].strip()
                
                extracted_data = json.loads(content)
            except json.JSONDecodeError:
                logger.error("Failed to parse DeepSeek JSON response.")
                extracted_data = {}

        except Exception as e:
            logger.error(f"DeepSeek API Error: {e}")
            extracted_data = {}
            if callback: callback("AI Analysis failed. Attempting fallback...")

        # --- 4. Fallback Mechanism & Normalization ---
        
        # Normalize keys to match database expectations (emails list, phones list)
        final_data = {
            "emails": [],
            "phones": [],
            "website": None,
            "address": None,
            "country": country
        }
        
        # Process Emails
        raw_email = extracted_data.get("email") or extracted_data.get("emails")
        if isinstance(raw_email, list):
            final_data["emails"] = [e for e in raw_email if isinstance(e, str)]
        elif isinstance(raw_email, str) and raw_email:
            # split by comma if AI returned string
            final_data["emails"] = [e.strip() for e in raw_email.split(",")]
            
        # Process Phones
        raw_phone = extracted_data.get("phone") or extracted_data.get("phones")
        if isinstance(raw_phone, list):
            final_data["phones"] = [p for p in raw_phone if isinstance(p, str)]
        elif isinstance(raw_phone, str) and raw_phone:
            final_data["phones"] = [p.strip() for p in raw_phone.split(",")]

        # Process Address
        final_data["address"] = extracted_data.get("address")
        if isinstance(final_data["address"], list):
             final_data["address"] = ", ".join(final_data["address"])

        # Process Website (Fallback Logic)
        ai_website = extracted_data.get("website")
        if ai_website and isinstance(ai_website, str) and "http" in ai_website:
             final_data["website"] = ai_website
        elif ai_website and isinstance(ai_website, list) and len(ai_website) > 0:
             final_data["website"] = ai_website[0]
        else:
            # Fallback: Use the first search result URL that looks like a main page
            # Simple heuristic: shortest URL in top 3 results that isn't a directory (like yellowpages)
            potential_urls = [r['href'] for r in all_results[:5]]
            if potential_urls:
                # Just take the first one for now as a best guess fallback
                final_data["website"] = potential_urls[0]
                if callback: callback(f"AI missed website. Using fallback: {final_data['website']}")

        # Final Cleanup
        # Ensure we don't return empty lists if database expects None? 
        # Actually our database logic handles lists, so it's fine.
        
        return final_data

# Test block (run directly to verify)
if __name__ == "__main__":
    agent = SearchAgent()
    logging.info("Running test search...")
    res = asyncio.run(agent.find_company_leads("Erd Metal Inc", "USA"))
    print(json.dumps(res, indent=2))
