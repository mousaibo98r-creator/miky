import streamlit as st

st.title("🤖 AI Search (DeepSeek)")
st.caption("Enrich buyer contact data using DeepSeek AI with web search capabilities.")

import os

from services.data_loader import get_buyer_names, get_countries, load_buyers

# --- Data loads AFTER title ---
data = load_buyers()

# Check API key availability
api_key = os.environ.get("DEEPSEEK_API_KEY", "")
if not api_key:
    st.warning("DeepSeek API key not configured. Set DEEPSEEK_API_KEY in Settings or .env file.")

# --- Buyer selection ---
st.markdown("### Select Buyer to Enrich")
col1, col2 = st.columns(2)

selected_buyer = None
selected_country = None

with col1:
    buyer_names = get_buyer_names(data)
    if buyer_names:
        selected_buyer = st.selectbox("Buyer Name", options=buyer_names)
    else:
        selected_buyer = st.text_input("Buyer Name", placeholder="Enter buyer name...")

with col2:
    country_list = get_countries(data)
    if country_list:
        selected_country = st.selectbox("Country", options=country_list)
    else:
        selected_country = st.text_input("Country", placeholder="Enter country...")

# Show current data for selected buyer
if data and selected_buyer:
    record = None
    for item in data:
        if item.get("buyer_name") == selected_buyer:
            record = item
            break
    if record:
        with st.expander("Current Data", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Emails:** {', '.join(record.get('email', [])) or 'None'}")
                st.markdown(f"**Phones:** {', '.join(record.get('phone', [])) or 'None'}")
            with c2:
                st.markdown(f"**Website:** {', '.join(record.get('website', [])) or 'None'}")
                st.markdown(f"**Address:** {', '.join(record.get('address', [])) or 'None'}")

st.divider()

# --- AI Enrichment (ONLY on button click) ---
if st.button("🚀 Enrich with AI", type="primary", disabled=not api_key):
    if not selected_buyer or not selected_country:
        st.error("Please select both a buyer and a country.")
    else:
        from services.search_agent import SearchAgent
        import asyncio

        status_container = st.status("AI Enrichment in progress...", expanded=True)
        
        async def run_search():
            agent = SearchAgent()
            def update_status(msg):
                status_container.write(msg)
            
            return await agent.find_company_leads(selected_buyer, selected_country, callback=update_status)

        try:
            result = asyncio.run(run_search())
            
            if result:
                status_container.update(label="Enrichment complete!", state="complete")
                
                st.markdown("### Enriched Results")
                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown("**📧 Emails Found:**")
                    for e in result.get("emails", []):
                        st.markdown(f"- {e}")

                    st.markdown("**📞 Phones Found:**")
                    for p in result.get("phones", []):
                        st.markdown(f"- {p}")

                with col_b:
                    st.markdown("**🌐 Websites Found:**")
                    if result.get("website"):
                        st.markdown(f"- [{result['website']}]({result['website']})")

                    st.markdown("**📍 Addresses Found:**")
                    if result.get("address"):
                        st.markdown(f"- {result['address']}")

                if result.get("notes"):
                    st.info(f"Notes: {result['notes']}")
            else:
                status_container.update(label="No results found", state="error")
                st.warning(
                    "AI search returned no results. The buyer may not have public contact information."
                )

        except Exception as e:
            status_container.update(label="Error", state="error")
            st.error(f"AI Search failed: {e}")
