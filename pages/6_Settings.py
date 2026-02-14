import os

import streamlit as st

st.title("\u2699\ufe0f Settings")
st.caption("API keys are loaded from environment variables. Never hardcoded.")

# --- NO secrets loaded at startup. Show current status lazily. ---

st.subheader("Environment Variable Status")

env_vars = {
    "SUPABASE_URL": os.environ.get("SUPABASE_URL", ""),
    "SUPABASE_KEY": os.environ.get("SUPABASE_KEY", ""),
    "DEEPSEEK_API_KEY": os.environ.get("DEEPSEEK_API_KEY", ""),
}

for var_name, var_value in env_vars.items():
    if var_value:
        st.success(f"\u2705 `{var_name}` is configured ({len(var_value)} chars)")
    else:
        st.warning(f"\u26a0\ufe0f `{var_name}` is NOT set")

st.divider()
st.subheader("Configure via Session (temporary)")
st.info("For production, set environment variables in the Antigravity dashboard or a `.env` file.")

with st.form("settings_form"):
    db_url = st.text_input(
        "Supabase URL",
        value=st.session_state.get("supabase_url", ""),
        help="Your Supabase project URL",
    )
    db_key = st.text_input(
        "Supabase Key",
        type="password",
        value=st.session_state.get("supabase_key", ""),
        help="Your Supabase anon/service key",
    )
    st.divider()
    deepseek_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        value=st.session_state.get("deepseek_key", ""),
        help="API key from platform.deepseek.com",
    )

    saved = st.form_submit_button("Save Configuration")

    if saved:
        # Validate inputs
        errors = []
        if db_url and not db_url.startswith("http"):
            errors.append("Supabase URL must start with http:// or https://")

        if errors:
            for err in errors:
                st.error(err)
        else:
            st.session_state["supabase_url"] = db_url
            st.session_state["supabase_key"] = db_key
            st.session_state["deepseek_key"] = deepseek_key

            # Also set as env vars for the current session
            if db_url:
                os.environ["SUPABASE_URL"] = db_url
            if db_key:
                os.environ["SUPABASE_KEY"] = db_key
            if deepseek_key:
                os.environ["DEEPSEEK_API_KEY"] = deepseek_key

            st.success("Settings saved for this session!")
            st.rerun()
