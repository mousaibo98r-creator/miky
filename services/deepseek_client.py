import json
import os
import re

import requests
from bs4 import BeautifulSoup
from openai import AsyncOpenAI


class DeepSeekClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the internet for company contact details.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g. 'Chalishkan Company Iraq contact email')"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_page",
                    "description": "Fetch the content of a webpage to extract contact details like email, phone, address. Use this AFTER finding a website URL from search.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to fetch (e.g. 'https://company.com/contact')"
                            }
                        },
                        "required": ["url"]
                    }
                }
            }
        ]

    async def extract_company_data(self, system_prompt, buyer_name, country, model="deepseek-chat", callback=None):
        """
        Orchestrates the chat completion.
        MUST return a DICT or LIST. Never returns raw string.
        """
        user_content = f"Find contact info for Buyer: '{buyer_name}' located in '{country}'."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        if callback:
            callback(f"Initiating request with model: {model}...")

        max_turns = 15
        current_turn = 0

        while current_turn < max_turns:
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
                
                message = response.choices[0].message
                
                # Check for Tool Calls
                if message.tool_calls:
                    messages.append(message) # Add assistant's tool-call message
                    
                    for tool_call in message.tool_calls:
                        args = json.loads(tool_call.function.arguments)
                        
                        if tool_call.function.name == "web_search":
                            query = args.get('query')
                            if callback:
                                callback(f"Turn {current_turn+1}: Searching for '{query}'...")
                            result = self._perform_search(query)
                            
                        elif tool_call.function.name == "fetch_page":
                            url = args.get('url')
                            if callback:
                                callback(f"Turn {current_turn+1}: Fetching page '{url}'...")
                            result = self._fetch_page(url)
                        else:
                            result = {"error": "Unknown tool"}
                        
                        # Add Tool Output
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result, ensure_ascii=False)
                        })
                    
                    current_turn += 1
                else:
                    # No tool calls -> Final Answer
                    content = message.content
                    if not content:
                        return {"status": "error", "message": "Empty response"}, current_turn
                    
                    return self._parse_to_dict(content), current_turn

            except Exception as e:
                # Capture API errors gracefully
                if callback:
                    callback(f"API Error: {str(e)}")
                return {"status": "error", "message": str(e)}, current_turn
        
        # Force a FINAL answer if loop limit reached
        if callback:
            callback("Max turns reached. Forcing final JSON output...")
        
        messages.append({
            "role": "user",
            "content": "STOP SEARCHING. Return the JSON object immediately. Do NOT output any text other than JSON."
        })

        try:
            final_response = await self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            content = final_response.choices[0].message.content
            return self._parse_to_dict(content), current_turn
        except Exception as e:
             return {"status": "error", "message": f"Finalization failed: {str(e)}"}, current_turn

    def _parse_to_dict(self, content):
        """Helper to ensure we return a dict, even if model outputs markdown or text."""
        cleaned = self._clean_json(content)
        if not cleaned:
             return {"status": "error", "message": "No content to parse"}
             
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # If it's not JSON, it might be conversational text.
            # Return it wrapped in a dict so the app doesn't crash.
            return {
                "status": "warning",
                "message": "Model returned text instead of JSON",
                "raw_content": cleaned
            }

    def _perform_search(self, query):
        """Uses DuckDuckGo Search and extracts contact info."""
        try:
            from duckduckgo_search import DDGS
            
            # Use DuckDuckGo Search
            # We use a list comprehension to ensure it's a list
            results = list(DDGS().text(query, max_results=8))
            
            if not results:
                return [{"error": "No search results found."}]
                
            simplified_results = []
            for r in results:
                simplified_results.append({
                    "title": r.get('title'),
                    "url": r.get('href'),
                    "snippet": r.get('body')
                })
                
            simplified_results.insert(0, {
                "system_note": "Here are search results. Use 'fetch_page' on promising URLs."
            })
            
            return simplified_results
            
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]

    def _fetch_page(self, url):
        """Fetches a webpage and extracts contact info using BeautifulSoup."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            html = response.text
            
            soup = BeautifulSoup(html, 'html.parser')
            for element in soup(['script', 'style', 'noscript']):
                element.decompose()
            
            text = soup.get_text(separator=' ')
            text = re.sub(r'\s+', ' ', text)
            
            emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)))
            
            cf_emails = re.findall(r'data-cfemail="([^"]+)"', html)
            for cf in cf_emails:
                try:
                    r = int(cf[:2], 16)
                    decoded_email = ''.join([chr(int(cf[i:i+2], 16) ^ r) for i in range(2, len(cf), 2)])
                    if '@' in decoded_email:
                        emails.append(decoded_email)
                except Exception:
                    pass
            
            # Simple keyword filters
            emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'test', 'sample', 'wix', 'sentry'])]
            
             # Extract phone numbers with FIXED patterns
            phone_patterns = [
                r'\d{10,15}\+',  # 9647514504009+  (Iraqi format with + at end)
                r'\+\d{10,15}',  # +9647514554426  (+ at start)
                r'\+\d{1,3}[\s\-]?\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',  # +964 751 455 4426
                r'(?:tel|phone|call)[:\s]+([+\d\s\-()]+)',  # tel: or phone: prefixed
                r'0\d{9,12}',  # 07514504009 (local format)
            ]
            
            phones = []
            for pattern in phone_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for m in matches:
                    if isinstance(m, str):
                        phones.append(m)
            
            flat_phones = []
            for p in phones:
                if isinstance(p, list): flat_phones.extend(p)
                else: flat_phones.append(p)
            
            cleaned_phones = []
            for p in flat_phones:
                cleaned = re.sub(r'[^\d+]', '', str(p))
                if len(cleaned) >= 10 and cleaned not in cleaned_phones:
                    cleaned_phones.append(cleaned)
            
            tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
            for link in tel_links:
                tel = link.get('href', '').replace('tel:', '').strip()
                cleaned = re.sub(r'[^\d+]', '', tel)
                if len(cleaned) >= 10 and cleaned not in cleaned_phones:
                    cleaned_phones.append(cleaned)
            
            address_candidates = []
            address_markers = ['address', 'location', 'hq', 'office', 'box ', 'street', 'road', 'avenue', 'suite', 'floor']
            text_lower = text.lower()
            
            for marker in address_markers:
                idx = text_lower.find(marker)
                if idx != -1:
                    start = max(0, idx - 50)
                    end = min(len(text), idx + 150)
                    candidate = text[start:end].strip()
                    if len(candidate) > 10:
                        address_candidates.append(candidate)
                        
            footer = soup.find('footer')
            if footer:
                footer_text = footer.get_text(separator=' ').strip()
                footer_text = re.sub(r'\s+', ' ', footer_text)
                if len(footer_text) < 500:
                    address_candidates.append(f"Footer: {footer_text}")
            
            address_text = " | ".join(address_candidates[:3])
            final_text = text[:2500]
            if address_text:
                final_text += f"\n\nPossible Address Info: {address_text}"

            return {
                "url": url,
                "emails_found": emails[:10],
                "phones_found": cleaned_phones[:10],
                "page_text_preview": final_text
            }
        except Exception as e:
            return [{"error": f"Failed to fetch page: {str(e)}"}]

    def _clean_json(self, text):
        """Extracts JSON from markdown code blocks if necessary."""
        if not text:
            return None
        text = text.strip()
        
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.rfind("```")
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.rfind("```")
            return text[start:end].strip()
            
        return text
