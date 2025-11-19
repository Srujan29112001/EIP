"""
Streamlit Frontend for EIP
Main dashboard and chat interface
"""
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import uuid

# Page configuration
st.set_page_config(
    page_title="EIP - Entrepreneurship Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Initialize session state
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


def login(email: str, password: str):
    """Login user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            return True
        else:
            st.error("Invalid credentials")
            return False
    except Exception as e:
        st.error(f"Login failed: {e}")
        return False


def register(email: str, name: str, password: str, tier: str):
    """Register new user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "email": email,
                "name": name,
                "password": password,
                "tier": tier
            }
        )
        if response.status_code == 201:
            st.success("Registration successful! Please login.")
            return True
        else:
            st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Registration failed: {e}")
        return False


def get_user_info():
    """Get current user information"""
    if not st.session_state.access_token:
        return None

    try:
        response = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def send_chat_message(query: str):
    """Send chat message to backend"""
    if not st.session_state.access_token:
        st.error("Please login first")
        return None

    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/",
            json={
                "query": query,
                "session_id": st.session_state.session_id
            },
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Query failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Query failed: {e}")
        return None


def auth_page():
    """Authentication page"""
    st.title("🚀 Welcome to EIP")
    st.markdown("### Entrepreneurship Intelligence Platform")
    st.markdown("AI-Powered Decision-Making System for Entrepreneurs")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login to Your Account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True):
            if login(email, password):
                st.rerun()

    with tab2:
        st.subheader("Create New Account")
        name = st.text_input("Full Name", key="register_name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        tier = st.selectbox("User Tier", ["aspiring", "mid", "top"])

        if st.button("Register", use_container_width=True):
            if register(email, name, password, tier):
                st.balloons()


def dashboard_page():
    """Main dashboard page"""
    # Sidebar
    with st.sidebar:
        st.title("🚀 EIP Dashboard")

        # User info
        user_info = get_user_info()
        if user_info:
            st.session_state.user_info = user_info
            st.markdown(f"**Welcome, {user_info['name']}!**")
            st.markdown(f"Tier: `{user_info['tier'].upper()}`")
            st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigation",
            ["💬 AI Chat", "📊 Dashboard", "📈 Analytics", "⚙️ Settings"]
        )

        st.markdown("---")

        if st.button("Logout", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.session_state.chat_history = []
            st.rerun()

    # Main content based on navigation
    if page == "💬 AI Chat":
        chat_interface()
    elif page == "📊 Dashboard":
        overview_dashboard()
    elif page == "📈 Analytics":
        analytics_page()
    else:
        settings_page()


def chat_interface():
    """AI Chat interface"""
    st.title("💬 AI Business Advisor")
    st.markdown("Ask me anything about your business - market insights, policy updates, tax optimization, and more!")

    # Chat container
    chat_container = st.container()

    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask your business question..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Get AI response
        with st.spinner("Analyzing..."):
            response = send_chat_message(prompt)

        if response:
            # Add assistant message to history
            assistant_message = response["answer"]
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_message})

            # Display assistant message
            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(assistant_message)

                    # Show metadata
                    with st.expander("📌 Additional Info"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Agent Used", response["agent_used"])
                        with col2:
                            st.metric("Response Time", f"{response['latency_ms']:.0f}ms")
                        with col3:
                            st.metric("Sources", len(response.get("sources", [])))

                        # Show sources
                        if response.get("sources"):
                            st.markdown("**Sources:**")
                            for source in response["sources"]:
                                st.markdown(f"- [{source['title']}]({source.get('url', '#')})")

            st.rerun()


def overview_dashboard():
    """Overview dashboard with key metrics"""
    st.title("📊 Business Overview")

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Revenue (Monthly)",
            value="$167K",
            delta="12%"
        )

    with col2:
        st.metric(
            label="Profit Margin",
            value="40%",
            delta="5%"
        )

    with col3:
        st.metric(
            label="Cash Flow",
            value="$85K",
            delta="-3%",
            delta_color="inverse"
        )

    with col4:
        st.metric(
            label="Market Score",
            value="7.8/10",
            delta="0.5"
        )

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            y=[150, 155, 160, 165, 167, 170],
            mode='lines+markers',
            name='Revenue'
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Expense Breakdown")
        fig = go.Figure(data=[go.Pie(
            labels=["Salaries", "Marketing", "Operations", "R&D"],
            values=[600, 300, 200, 100]
        )])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Recent insights
    st.subheader("🔍 Recent Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("**New Policy Alert**\n\nStartup tax exemption extended till 2025. Apply now!")

    with col2:
        st.success("**Market Opportunity**\n\nSustainable fashion market growing at 18% CAGR")

    with col3:
        st.warning("**Tax Deadline**\n\nAdvance tax payment due on June 15")


def analytics_page():
    """Analytics and reports page"""
    st.title("📈 Advanced Analytics")
    st.markdown("Coming soon - Detailed analytics and custom reports")


def settings_page():
    """Settings page"""
    st.title("⚙️ Settings")
    st.markdown("Coming soon - User preferences and configuration")


# Main app logic
def main():
    if st.session_state.access_token is None:
        auth_page()
    else:
        dashboard_page()


if __name__ == "__main__":
    main()
