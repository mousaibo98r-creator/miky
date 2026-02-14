import datetime

import streamlit as st

st.title("\U0001f4c2 File Manager")
st.caption("Upload and manage files. No directory scanning at startup.")

# --- NO file scanning on load ---

# Session state for uploaded files
if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []

MAX_FILE_SIZE_MB = 5

uploaded_file = st.file_uploader(
    "Upload New File",
    type=["csv", "xlsx", "pdf", "json"],
    help=f"Maximum file size: {MAX_FILE_SIZE_MB}MB",
)

# --- File processing ONLY after user uploads ---
if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"File too large ({file_size_mb:.1f}MB). Maximum is {MAX_FILE_SIZE_MB}MB.")
    else:
        file_details = {
            "name": uploaded_file.name,
            "type": uploaded_file.type or "unknown",
            "size": f"{uploaded_file.size / 1024:.2f} KB",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        # Prevent duplicate entries on rerun
        existing = [f["name"] for f in st.session_state["uploaded_files"]]
        if uploaded_file.name not in existing:
            st.session_state["uploaded_files"].append(file_details)
            st.success(f"Uploaded {uploaded_file.name} ({file_details['size']})")

st.divider()

# --- File list (from session state only, no disk scan) ---
if st.session_state["uploaded_files"]:
    st.subheader("My Files")
    import pandas as pd

    f_df = pd.DataFrame(st.session_state["uploaded_files"])
    st.dataframe(f_df, use_container_width=True)

    col_act1, col_act2 = st.columns([1, 4])
    with col_act1:
        file_to_action = st.selectbox(
            "Select File", options=[f["name"] for f in st.session_state["uploaded_files"]]
        )

    if file_to_action:
        c1, c2 = st.columns(2)
        with c1:
            st.button("\u2b07\ufe0f Download Selected")
        with c2:
            if st.button("\U0001f5d1\ufe0f Delete Selected"):
                st.session_state["uploaded_files"] = [
                    f for f in st.session_state["uploaded_files"] if f["name"] != file_to_action
                ]
                st.rerun()
else:
    st.info("No files uploaded yet. Upload a file above to get started.")
