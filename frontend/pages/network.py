import streamlit as st
from frontend.utils import api_post


MSG_TYPES = {
    "LinkedIn Connect": "linkedin",
    "Recruiter Outreach (Email)": "recruiter",
    "Referral Request": "referral",
    "Follow-up (After Apply)": "followup",
}


def render():
    st.header("🤝 Networking Assistant")
    st.caption("Generate personalized outreach messages that actually get replies.")

    with st.form("network_form"):
        msg_type_label = st.selectbox("Message Type", list(MSG_TYPES.keys()))

        c1, c2 = st.columns(2)
        recipient_name = c1.text_input("Recipient Name", placeholder="e.g. Sarah Chen")
        recipient_title = c2.text_input("Recipient Title", placeholder="e.g. Engineering Manager")

        c3, c4 = st.columns(2)
        company = c3.text_input("Company", placeholder="e.g. Stripe")
        target_role = c4.text_input("Role You're Targeting", placeholder="e.g. Senior Backend Engineer")

        background = st.text_area(
            "Your Background (2–3 lines)",
            height=100,
            placeholder="e.g. CS grad with 2 years in fintech startups, built payment infra at Acme, looking for larger-scale systems challenges...",
        )

        submitted = st.form_submit_button("✉️ Generate Message", type="primary", use_container_width=True)

    if submitted:
        if not recipient_name.strip() or not company.strip() or not target_role.strip():
            st.warning("Please fill in recipient name, company, and target role.")
            return

        with st.spinner("Crafting a personalized message with Gemini..."):
            result = api_post(
                "/network/",
                {
                    "message_type": MSG_TYPES[msg_type_label],
                    "recipient_name": recipient_name,
                    "recipient_title": recipient_title,
                    "company": company,
                    "target_role": target_role,
                    "your_background": background,
                },
            )

        if not result:
            return

        st.divider()

        if result.get("subject"):
            st.markdown(f"**Subject:** `{result['subject']}`")

        st.subheader("📨 Generated Message")
        st.text_area(
            label="Copy and send this:",
            value=result["message"],
            height=200,
            key="msg_output",
        )

        col1, col2 = st.columns(2)
        col1.metric("Word Count", result["word_count"])
        col2.metric("Recommended Max", "300" if MSG_TYPES[msg_type_label] == "linkedin" else "150")

        if result.get("tips"):
            st.subheader("🎯 Response-Rate Tips")
            for tip in result["tips"]:
                st.info(tip)
