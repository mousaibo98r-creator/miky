import streamlit as st
import datetime
import random

st.title("\U0001f4e7 Email Center")
st.caption("Mock email client - all sending requires button click.")

# --- NO network calls on load ---

ec1, ec2 = st.columns([1, 1])

with ec1:
    st.subheader("Inbox")

    # Mock emails (no external fetch)
    senders = ["support@logistics.com", "buyer@client.com", "admin@platform.com"]
    subjects = ["Invoice Request", "Shipment Update", "New Order Inquiry", "Account Verification"]
    mock_emails = []
    for i in range(5):
        mock_emails.append({
            "id": i,
            "sender": random.choice(senders),
            "subject": random.choice(subjects),
            "time": (datetime.datetime.now() - datetime.timedelta(hours=i*2)).strftime("%H:%M"),
            "body": "This is a sample email body mock content regarding the subject line."
        })

    for email in mock_emails:
        with st.expander(f"{email['sender']} - {email['subject']}"):
            st.caption(f"Time: {email['time']}")
            st.write(email['body'])
            if st.button("Reply", key=f"reply_{email['id']}"):
                st.info("Reply feature coming soon.")

with ec2:
    st.subheader("Compose Email")

    with st.expander("\u2699\ufe0f SMTP Configuration"):
        c1, c2 = st.columns(2)
        c1.text_input("SMTP Host", value="smtp.gmail.com")
        c1.text_input("Port", value="587")
        c2.text_input("Username")
        c2.text_input("Password", type="password")

    with st.form("email_form"):
        to_addr = st.text_input("To (Recipient)")
        subject = st.text_input("Subject")
        body = st.text_area("Body", height=200)
        submitted = st.form_submit_button("Send Email")

        # --- Sending ONLY on button click ---
        if submitted:
            if not to_addr:
                st.error("Please enter a recipient address.")
            else:
                progress = st.progress(0)
                progress.progress(30)
                # No actual sending - mock only
                progress.progress(70)
                progress.progress(100)
                st.success("Email sent successfully!")
