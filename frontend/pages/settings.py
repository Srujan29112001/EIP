"""
Settings Page
User preferences and configuration
"""
import streamlit as st
import requests


API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000/api/v1")


def render_settings_page():
    """Render settings page"""
    st.title("⚙️ Settings")

    # Check authentication
    if "access_token" not in st.session_state or not st.session_state.access_token:
        st.warning("Please login first")
        return

    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

    # Settings sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Profile",
        "🤖 AI Preferences",
        "🔔 Notifications",
        "🔐 Security"
    ])

    # Profile Settings
    with tab1:
        st.subheader("Profile Settings")

        # Get current user info
        user_info = get_user_info(headers)

        if user_info:
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Name", value=user_info.get("name", ""))
                email = st.text_input("Email", value=user_info.get("email", ""), disabled=True)

            with col2:
                tier = st.selectbox(
                    "Account Tier",
                    ["aspiring", "mid", "top"],
                    index=["aspiring", "mid", "top"].index(user_info.get("tier", "mid")),
                    disabled=True
                )
                st.info("Contact support to change your tier")

            business_info = st.text_area(
                "Business Information",
                value=user_info.get("business_info", ""),
                placeholder="Tell us about your business (sector, revenue range, goals)"
            )

            if st.button("💾 Save Profile", type="primary"):
                # TODO: Update profile via API
                st.success("Profile updated successfully!")

    # AI Preferences
    with tab2:
        st.subheader("AI Preferences")

        st.markdown("#### Default LLM Provider")
        llm_provider = st.selectbox(
            "Choose your preferred AI model",
            ["OpenAI (GPT-4o)", "Anthropic (Claude Sonnet 4.5)", "DeepSeek-R1"],
            index=0
        )

        st.markdown("#### Response Style")
        response_style = st.radio(
            "How would you like AI responses?",
            ["Concise", "Detailed", "Very Detailed"],
            help="Choose the level of detail in AI responses"
        )

        temperature = st.slider(
            "Creativity Level",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Lower values = more focused, Higher values = more creative"
        )

        st.markdown("#### Knowledge Sources")
        use_rag = st.checkbox("Use document knowledge base (RAG)", value=True)
        use_graphrag = st.checkbox("Use knowledge graph (GraphRAG)", value=True)
        use_web_search = st.checkbox("Enable web search (coming soon)", value=False, disabled=True)

        if st.button("💾 Save AI Preferences", type="primary"):
            # TODO: Save preferences to backend
            st.success("AI preferences saved!")

    # Notifications
    with tab3:
        st.subheader("Notification Preferences")

        st.markdown("#### Email Notifications")
        email_daily = st.checkbox("Daily digest", value=True)
        email_policy = st.checkbox("Policy updates", value=True)
        email_market = st.checkbox("Market alerts", value=False)

        st.markdown("#### In-App Notifications")
        inapp_messages = st.checkbox("AI conversation updates", value=True)
        inapp_docs = st.checkbox("Document processing complete", value=True)
        inapp_reports = st.checkbox("Weekly reports ready", value=True)

        st.markdown("#### Notification Frequency")
        frequency = st.select_slider(
            "How often should we notify you?",
            options=["Real-time", "Hourly", "Daily", "Weekly"],
            value="Daily"
        )

        if st.button("💾 Save Notification Preferences", type="primary"):
            st.success("Notification preferences saved!")

    # Security
    with tab4:
        st.subheader("Security Settings")

        st.markdown("#### Change Password")
        col1, col2 = st.columns(2)

        with col1:
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")

        with col2:
            confirm_password = st.text_input("Confirm New Password", type="password")

        if st.button("🔐 Change Password"):
            if new_password != confirm_password:
                st.error("Passwords don't match")
            elif len(new_password) < 8:
                st.error("Password must be at least 8 characters")
            else:
                # TODO: Change password via API
                st.success("Password changed successfully!")

        st.divider()

        st.markdown("#### Active Sessions")
        st.info("You are currently logged in on 1 device")

        if st.button("🚪 Logout All Devices"):
            st.warning("This will log you out from all devices")
            # TODO: Implement logout all

        st.divider()

        st.markdown("#### API Keys")
        st.info("Manage your API keys for programmatic access")

        if st.button("🔑 Generate New API Key"):
            st.code("eip_sk_1234567890abcdef", language="text")
            st.warning("Save this key securely. It won't be shown again.")

        st.divider()

        st.markdown("#### Danger Zone")
        with st.expander("⚠️ Delete Account", expanded=False):
            st.error("This action cannot be undone. All your data will be permanently deleted.")
            confirm_delete = st.text_input(
                "Type 'DELETE' to confirm",
                key="delete_confirm"
            )
            if st.button("🗑️ Delete My Account", type="secondary"):
                if confirm_delete == "DELETE":
                    st.error("Account deletion requested. Contact support to complete.")
                else:
                    st.warning("Please type 'DELETE' to confirm")


def get_user_info(headers):
    """Get current user information"""
    try:
        response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


if __name__ == "__main__":
    render_settings_page()
