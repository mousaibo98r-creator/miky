import streamlit as st
import os
import json
import asyncio


@st.cache_resource
def get_deepseek_client():
    """Create DeepSeek AI client once. Returns None if unavailable."""
    api_key = os.environ.get('DEEPSEEK_API_KEY', '')
    if not api_key:
        try:
            if hasattr(st, 'secrets') and 'DEEPSEEK_API_KEY' in st.secrets:
                api_key = str(st.secrets['DEEPSEEK_API_KEY'])
        except Exception:
            pass
    if not api_key:
        return None
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        return client
    except ImportError:
        return None
    except Exception:
        return None


TOOLS = [
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
                        "description": "Search query (e.g. 'Company Name Country contact email')"
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
            "description": "Fetch a webpage to extract contact details like email, phone, address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch"
                    }
                },
                "required": ["url"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are an expert business intelligence agent. Your task is to find contact information for a company.

You have access to two tools:
1. web_search - Search the internet for company info
2. fetch_page - Fetch a webpage for detailed contact info

Return a JSON object with these fields:
{
    "email": ["list of emails found"],
    "phone": ["list of phone numbers found"],
    "website": ["list of websites found"],
    "address": ["list of addresses found"],
    "notes": "any additional context about the company"
}

If a field has no data, use an empty list []. Always return valid JSON."""


def _perform_search(query):
    """Web search using available search engine."""
    try:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return {"results": [], "error": "No search library available"}

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "href": r.get("href", "")
                })
        return {"results": results}
    except Exception as e:
        return {"results": [], "error": str(e)}


def _fetch_page(url):
    """Fetch a page and extract text content."""
    try:
        import requests
        from bs4 import BeautifulSoup

        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (compatible; DataBot/1.0)"
        })
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Remove script/style
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Limit to 3000 chars to avoid token overload
        return {"content": text[:3000], "url": url}
    except Exception as e:
        return {"content": "", "error": str(e), "url": url}


def _clean_json(text):
    """Extract JSON from markdown code blocks."""
    import re
    if "```" in text:
        match = re.search(r'```(?:json)?\s*(.*?)```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


async def enrich_buyer(buyer_name, country, status_callback=None):
    """Run DeepSeek AI enrichment for a buyer. Returns (result_dict, turns)."""
    client = get_deepseek_client()
    if client is None:
        return None, 0

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Find contact info for Buyer: '{buyer_name}' located in '{country}'."}
    ]

    if status_callback:
        status_callback("Initiating AI search...")

    max_turns = 10
    for turn in range(max_turns):
        try:
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )

            message = response.choices[0].message

            if message.tool_calls:
                messages.append(message)
                for tool_call in message.tool_calls:
                    args = json.loads(tool_call.function.arguments)

                    if tool_call.function.name == "web_search":
                        query = args.get('query', '')
                        if status_callback:
                            status_callback(f"Turn {turn+1}: Searching '{query}'...")
                        result = _perform_search(query)

                    elif tool_call.function.name == "fetch_page":
                        url = args.get('url', '')
                        if status_callback:
                            status_callback(f"Turn {turn+1}: Fetching '{url[:50]}'...")
                        result = _fetch_page(url)
                    else:
                        result = {"error": "Unknown tool"}

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })
            else:
                content = message.content
                if not content:
                    return None, turn
                return _clean_json(content), turn

        except Exception as e:
            if status_callback:
                status_callback(f"Error: {str(e)}")
            return None, turn

    # Force final answer
    if status_callback:
        status_callback("Max turns reached. Forcing final output...")

    messages.append({
        "role": "user",
        "content": "STOP SEARCHING. Return the JSON object immediately with whatever data you found."
    })

    try:
        final = await client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        content = final.choices[0].message.content
        return _clean_json(content), max_turns
    except Exception:
        return None, max_turns
