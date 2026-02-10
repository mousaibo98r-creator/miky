import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import datetime
import random
import time
import json
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Export Analytics Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
<style>
    /* Dark Mode Enhancements */
    .stApp {
        background-color: #0e1117;
    }
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #41424b;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00d2ff;
    }
    .metric-label {
        font-size: 1rem;
        color: #fafafa;
    }
    .profile-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #00d2ff;
        margin-bottom: 20px;
        border-bottom: 2px solid #00d2ff;
        padding-bottom: 10px;
    }
    div[data-testid="stExpander"] details summary p {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# --- SUPABASE CONNECTION & DATA LOADING ---
def init_connection():
    url = st.session_state.get('supabase_url', '')
    key = st.session_state.get('supabase_key', '')
    
    if not url or not key:
        return None
        
    try:
        client = create_client(url, key)
        return client
    except Exception as e:
        return None

@st.cache_data
def load_data():
    """Matches the structure of combined_buyers.json"""
    file_path = "combined_buyers.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            st.error(f"Error loading JSON data: {e}")
            return None
    return None

# --- MOCK DATA GENERATORS (Fallback) ---
def get_mock_dashboard_data():
    dates = pd.date_range(start="2023-01-01", periods=12, freq='M')
    volume = [random.randint(50000, 500000) for _ in range(12)]
    count = [random.randint(10, 100) for _ in range(12)]
    
    df_chart_a = pd.DataFrame({'Date': dates, 'USD Volume': volume, 'Count': count})
    
    countries = ['USA', 'China', 'Germany', 'UK', 'France', 'India']
    values = [random.randint(100, 1000) for _ in range(len(countries))]
    df_chart_b = pd.DataFrame({'Country': countries, 'Value': values})
    
    return df_chart_a, df_chart_b

def get_mock_intelligence_data():
    names = ["TechGlobal Inc", "Oceanic Trade", "FastLogistics", "Alpha Foods", "Zenith Parts"]
    countries = ["USA", "Germany", "China", "UK", "UAE", "Turkey"]
    data = []
    for i in range(50):
        data.append({
            "buyer_name": random.choice(names),
            "country_english": random.choice(countries),
            "total_usd": random.randint(1000, 100000),
            "email": [f"contact{i}@example.com"],
            "exporters": {"Mock Exporter": 1},
            "phone": [f"+1-555-01{i:02d}"],
            "address": [f"{random.randint(100,999)} Business Rd"],
            "website": ["http://example.com"]
        })
    return pd.DataFrame(data)

def get_mock_emails():
    emails = []
    senders = ["support@logistics.com", "buyer@client.com", "admin@platform.com"]
    subjects = ["Invoice Request", "Shipment Update", "New Order Inquiry", "Account Verification"]
    
    for i in range(5):
        emails.append({
            "id": i,
            "sender": random.choice(senders),
            "subject": random.choice(subjects),
            "time": (datetime.datetime.now() - datetime.timedelta(hours=i*2)).strftime("%H:%M"),
            "body": "This is a sample email body mock content regarding the subject line."
        })
    return emails

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", 
    ["Dashboard", "Intelligence", "Email Center", "File Manager", "Settings"],
    index=0
)

# Initialize Session State
if 'supabase_url' not in st.session_state:
    st.session_state['supabase_url'] = ''
if 'supabase_key' not in st.session_state:
    st.session_state['supabase_key'] = ''
if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = []

supabase = init_connection()

# Load Real Data or Fallback
real_df = load_data()
if real_df is not None:
    # Normalize column names for consistent usage
    # JSON keys: buyer_name, country_english, total_usd, email, phone, website, address, exporters
    df_intel = real_df.copy()
else:
    df_intel = get_mock_intelligence_data()


# --- PAGE 1: DASHBOARD ---
if page == "Dashboard":
    st.title("📊 Executive Dashboard")
    
    # Hero Section
    st.markdown("### Search Exporters")
    search_query = st.text_input("Enter Exporter Name, ID, or Region", placeholder="Search...")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    if real_df is not None:
        total_rev_val = real_df['total_usd'].sum()
        total_rev = f"${total_rev_val/1000000:.1f}M"
        active_exporters = f"{len(real_df)}" # Counting buyers here as proxy
        growth = "+12.5%" # Static for now
        
        # Prepare charts from real data
        # Chart B: Top Countries
        country_counts = real_df['country_english'].value_counts().head(10).reset_index()
        country_counts.columns = ['Country', 'Value']
        df_b = country_counts
        
        # Chart A: Dummy temporal data since JSON doesn't seem to have dates
        df_a, _ = get_mock_dashboard_data()
        
    else:
        total_rev = "$12.5M"
        active_exporters = "1,240"
        growth = "+15.4%"
        df_a, df_b = get_mock_dashboard_data()
    
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Volume (USD)</div><div class="metric-value">{total_rev}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Active Buyers</div><div class="metric-value">{active_exporters}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">YoY Growth</div><div class="metric-value">{growth}</div></div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Analytics Charts
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("USD Volume vs Transaction Count")
        fig_a = go.Figure()
        fig_a.add_trace(go.Bar(x=df_a['Date'], y=df_a['USD Volume'], name='USD Volume', marker_color='#00d2ff'))
        fig_a.add_trace(go.Scatter(x=df_a['Date'], y=df_a['Count'], name='Count', yaxis='y2', line=dict(color='#ff0055', width=3)))
        
        fig_a.update_layout(
            template="plotly_dark",
            yaxis=dict(title="USD Volume"),
            yaxis2=dict(title="Count", overlaying='y', side='right'),
            legend=dict(x=0, y=1.1, orientation='h'),
            height=400,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_a, use_container_width=True)
        
    with c2:
        st.subheader("Top Countries")
        fig_b = px.pie(df_b, values='Value', names='Country', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        fig_b.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_b, use_container_width=True)

# --- PAGE 2: INTELLIGENCE (MATRIX) ---
elif page == "Intelligence":
    st.title("🕸️ The Matrix (Intelligence)")
    
    # 3-Column Layout: Filters | Table | Profile
    col_filters, col_table, col_profile = st.columns([1, 3, 2])
    
    with col_filters:
        st.markdown("### Filters")
        
        # Check if we have data
        if not df_intel.empty:
            countries = sorted(list(df_intel['country_english'].dropna().unique()))
            sel_country = st.multiselect("Country", options=countries)
            
            # Simple Text Filter for Exporter/Buyer since Exporter is a dict
            txt_search = st.text_input("Search Buyer/Exporter")
            
            # Apply filters
            dff = df_intel.copy()
            if sel_country: 
                dff = dff[dff['country_english'].isin(sel_country)]
            
            if txt_search:
                # Basic string contains search on buyer name
                dff = dff[dff['buyer_name'].str.contains(txt_search, case=False, na=False)]
            
            st.info(f"Showing {len(dff)} records")
        else:
            dff = pd.DataFrame()
            st.warning("No data available.")

    with col_table:
        st.markdown("### Data Matrix")
        
        if not dff.empty:
            # Display primary columns
            display_cols = ['buyer_name', 'country_english', 'total_usd']
            # Add email count or first email for display?
            # Let's show just the list of string representation or count
            dff['emails_display'] = dff['email'].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
            
            event = st.dataframe(
                dff[display_cols + ['emails_display']],
                column_config={
                    "buyer_name": "Buyer Name",
                    "country_english": "Country",
                    "total_usd": st.column_config.NumberColumn("Total USD", format="$%.2f"),
                    "emails_display": "Emails"
                },
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
        else:
            event = None
    
    with col_profile:
        st.markdown("### Entity Profile")
        
        if event and event.selection.rows:
            idx = event.selection.rows[0]
            # Get data from filtered dataframe
            record = dff.iloc[idx]
            
            st.markdown(f"<div class='profile-header'>{record['buyer_name']}</div>", unsafe_allow_html=True)
            
            st.image("https://via.placeholder.com/150", width=100, caption="Company Logo")
            
            # Details
            st.markdown(f"**📍 Country:** {record.get('country_english', 'N/A')}")
            
            emails = record.get('email', [])
            email_str = ", ".join(emails) if isinstance(emails, list) else str(emails)
            st.markdown(f"**📧 Email:** {email_str}")
            
            phones = record.get('phone', [])
            phone_str = ", ".join(phones) if isinstance(phones, list) else str(phones)
            st.markdown(f"**📞 Phone:** {phone_str}")
            
            websites = record.get('website', [])
            web_str = ", ".join(websites) if isinstance(websites, list) else str(websites)
            st.markdown(f"**🌐 Website:** {web_str}")

            st.divider()
            
            val = record.get('total_usd', 0)
            st.markdown(f"**💰 Total Volume:** ${val:,.2f}")
            
            st.markdown("**🚢 Exporters:**")
            exporters = record.get('exporters', {})
            if isinstance(exporters, dict):
                for k, v in exporters.items():
                    st.markdown(f"- {k} ({v} invoices)")
            
            st.divider()
            
            b1, b2 = st.columns(2)
            with b1:
                st.link_button("🌐 Google Search", f"https://www.google.com/search?q={record['buyer_name']}")
            with b2:
                if st.button("🦅 Scavenge Data"):
                    img = st.empty()
                    img.info("Scavenging web for more data...")
                    time.sleep(1.5)
                    img.success("Data scavenged! (See logs)")
                    
        else:
            st.info("Select a row in the table to view the full profile.")

# --- PAGE 3: EMAIL CENTER ---
elif page == "Email Center":
    st.title("📧 Email Center")
    
    ec1, ec2 = st.columns([1, 1])
    
    with ec1:
        st.subheader("Inbox")
        emails = get_mock_emails()
        
        for email in emails:
            with st.expander(f"{email['sender']} - {email['subject']}"):
                st.caption(f"Time: {email['time']}")
                st.write(email['body'])
                st.button("Reply", key=f"reply_{email['id']}")
    
    with ec2:
        st.subheader("Compose Email")
        
        with st.expander("⚙️ SMTP Configuration"):
            c1, c2 = st.columns(2)
            c1.text_input("SMTP Host", value="smtp.gmail.com")
            c1.text_input("Port", value="587")
            c2.text_input("Username")
            c2.text_input("Password", type="password")
        
        with st.form("email_form"):
            st.text_input("To (Recipient)")
            st.text_input("Subject")
            st.text_area("Body", height=200)
            submitted = st.form_submit_button("Send Email")
            if submitted:
                st.success("Email sent successfully!")

# --- PAGE 4: FILE MANAGER ---
elif page == "File Manager":
    st.title("📂 File Manager")
    
    # Upload
    uploaded_file = st.file_uploader("Upload New File", type=['csv', 'xlsx', 'pdf', 'json'])
    
    if uploaded_file:
        file_details = {
            "name": uploaded_file.name,
            "type": uploaded_file.type,
            "size": f"{uploaded_file.size / 1024:.2f} KB",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state['uploaded_files'].append(file_details)
        st.success(f"Uploaded {uploaded_file.name}")
    
    st.divider()
    
    # File Grid
    if st.session_state['uploaded_files']:
        st.subheader("My Files")
        f_df = pd.DataFrame(st.session_state['uploaded_files'])
        st.dataframe(f_df, use_container_width=True)
        
        col_act1, col_act2 = st.columns([1, 4])
        with col_act1:
            file_to_action = st.selectbox("Select File", options=[f['name'] for f in st.session_state['uploaded_files']])
        
        if file_to_action:
            c1, c2 = st.columns(2)
            with c1:
                st.button("⬇️ Download Selected")
            with c2:
                if st.button("🗑️ Delete Selected"):
                    st.session_state['uploaded_files'] = [f for f in st.session_state['uploaded_files'] if f['name'] != file_to_action]
                    st.rerun()
    else:
        st.info("No files uploaded yet.")

# --- PAGE 5: SETTINGS ---
elif page == "Settings":
    st.title("⚙️ Settings")
    st.subheader("API Configuration")
    
    with st.form("settings_form"):
        db_url = st.text_input("Supabase URL", value=st.session_state['supabase_url'])
        db_key = st.text_input("Supabase Key", type="password", value=st.session_state['supabase_key'])
        st.divider()
        deepseek_key = st.text_input("DeepSeek API Key", type="password")
        maps_key = st.text_input("Google Maps API Key", type="password")
        saved = st.form_submit_button("Save Configuration")
        
        if saved:
            st.session_state['supabase_url'] = db_url
            st.session_state['supabase_key'] = db_key
            st.success("Settings saved! Reloading...")
            time.sleep(1)
            st.rerun()
