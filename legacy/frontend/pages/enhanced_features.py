"""
Enhanced Features Dashboard
Centralized access to all Phase 2 enhanced agents
"""
import streamlit as st
import requests
import json
from typing import Dict, Any

# Backend API URL
API_BASE_URL = "http://localhost:8000/api/v1"


def render_enhanced_features_page():
    """Render the enhanced features dashboard"""

    st.title("🚀 Enhanced AI Features")
    st.markdown("Access powerful new AI agents for comprehensive business intelligence")

    # Feature selector
    feature = st.selectbox(
        "Select Feature",
        [
            "🎯 Business Model Analysis",
            "💡 Business Model Recommender",
            "📈 Stock Analysis",
            "🏆 Competitor Intelligence",
            "💰 Government Subsidies"
        ]
    )

    st.markdown("---")

    # Route to appropriate feature
    if feature == "🎯 Business Model Analysis":
        render_business_model_analyzer()
    elif feature == "💡 Business Model Recommender":
        render_business_model_recommender()
    elif feature == "📈 Stock Analysis":
        render_stock_analyzer()
    elif feature == "🏆 Competitor Intelligence":
        render_competitor_tracker()
    elif feature == "💰 Government Subsidies":
        render_subsidies_explorer()


def render_business_model_analyzer():
    """Business Model Canvas Analysis"""
    st.header("🎯 Business Model Analysis")
    st.markdown("Analyze your business model using the Business Model Canvas framework")

    with st.form("business_model_form"):
        description = st.text_area(
            "Describe your business",
            placeholder="E.g., We're building a B2B SaaS platform for HR analytics with freemium pricing...",
            height=150
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            industry = st.selectbox("Industry", ["Technology", "E-commerce", "Services", "Healthcare", "Other"])
        with col2:
            stage = st.selectbox("Stage", ["idea", "seed", "growth", "expansion"])
        with col3:
            has_metrics = st.checkbox("I have metrics to share")

        metrics = {}
        if has_metrics:
            st.subheader("Current Metrics")
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                metrics["users"] = st.number_input("Users", min_value=0, value=0)
                metrics["revenue"] = st.number_input("Monthly Revenue ($)", min_value=0, value=0)
            with mcol2:
                metrics["growth_rate"] = st.number_input("Growth Rate (%)", min_value=0.0, value=0.0)
                metrics["burn_rate"] = st.number_input("Monthly Burn ($)", min_value=0, value=0)

        submitted = st.form_submit_button("Analyze Business Model")

        if submitted and description:
            with st.spinner("Analyzing your business model..."):
                try:
                    # Call backend API
                    response = requests.post(
                        f"{API_BASE_URL}/enhanced/business-model/analyze",
                        json={
                            "description": description,
                            "industry": industry,
                            "stage": stage,
                            "metrics": metrics if has_metrics else None
                        }
                    )

                    if response.status_code == 200:
                        result = response.json()
                        data = result.get("data", {})

                        # Display Results
                        st.success("Analysis Complete!")

                        # Scores
                        st.subheader("📊 Business Model Scores")
                        scores = data.get("scores", {})

                        score_cols = st.columns(4)
                        with score_cols[0]:
                            st.metric("Overall Score", f"{scores.get('overall', 0):.1f}/10")
                        with score_cols[1]:
                            st.metric("Customer Fit", f"{scores.get('customer_fit', 0):.1f}/10")
                        with score_cols[2]:
                            st.metric("Revenue Potential", f"{scores.get('revenue_potential', 0):.1f}/10")
                        with score_cols[3]:
                            st.metric("Viability", f"{scores.get('financial_viability', 0):.1f}/10")

                        # Canvas Analysis
                        st.subheader("🎨 Business Model Canvas")
                        canvas = data.get("canvas", {})

                        if canvas:
                            tabs = st.tabs(["Value Proposition", "Customer Segments", "Revenue Streams", "Full Canvas"])

                            with tabs[0]:
                                vp = canvas.get("value_propositions", {})
                                st.markdown(f"**Analysis:** {vp.get('analysis', 'N/A')}")
                                st.markdown(f"**Score:** {vp.get('score', 0)}/10")

                            with tabs[1]:
                                cs = canvas.get("customer_segments", {})
                                st.markdown(f"**Analysis:** {cs.get('analysis', 'N/A')}")
                                st.markdown(f"**Score:** {cs.get('score', 0)}/10")

                            with tabs[2]:
                                rs = canvas.get("revenue_streams", {})
                                st.markdown(f"**Analysis:** {rs.get('analysis', 'N/A')}")
                                st.markdown(f"**Score:** {rs.get('score', 0)}/10")

                            with tabs[3]:
                                st.json(canvas)

                        # Recommendations
                        st.subheader("💡 Recommendations")
                        recommendations = data.get("recommendations", [])
                        for i, rec in enumerate(recommendations, 1):
                            with st.expander(f"{i}. {rec.get('title', 'Recommendation')}"):
                                st.markdown(rec.get('description', ''))
                                st.markdown(f"**Priority:** {rec.get('priority', 'medium').upper()}")
                                st.markdown(f"**Impact:** {rec.get('impact', 'N/A')}")

                    else:
                        st.error(f"API Error: {response.status_code}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")


def render_business_model_recommender():
    """Business Model Recommendation"""
    st.header("💡 Business Model Recommender")
    st.markdown("Get AI-powered recommendations for the best business model for your idea")

    with st.form("bm_recommender_form"):
        idea = st.text_area(
            "Describe your startup idea",
            placeholder="E.g., AI-powered HR analytics platform for mid-sized companies...",
            height=120
        )

        col1, col2 = st.columns(2)
        with col1:
            industry = st.selectbox("Industry", ["Technology", "E-commerce", "Services", "Healthcare"])
            target_market = st.selectbox("Target Market", ["B2B", "B2C", "B2B2C"])
        with col2:
            resources = st.selectbox("Available Resources", ["Low", "Medium", "Medium-High", "High"])
            timeline = st.selectbox("Timeline to Profitability", ["6-12 months", "12-18 months", "18-24 months", "24-36 months"])

        submitted = st.form_submit_button("Get Recommendations")

        if submitted and idea:
            with st.spinner("Generating recommendations..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/enhanced/business-model/recommend",
                        json={
                            "idea": idea,
                            "industry": industry,
                            "target_market": target_market,
                            "resources": resources,
                            "timeline": timeline
                        }
                    )

                    if response.status_code == 200:
                        result = response.json()
                        data = result.get("data", {})

                        st.success("Recommendations Ready!")

                        # Display recommendations
                        recommendations = data.get("recommendations", [])
                        for rec in recommendations:
                            with st.expander(f"#{rec['rank']}: {rec['model_type']} - {rec['recommendation_strength']} Match ({rec['match_score']:.0%})"):
                                st.markdown(f"**Revenue Model:** {rec['revenue_model']}")
                                st.markdown(f"**Success Rate:** {rec['success_rate']:.0%}")
                                st.markdown(f"**Time to Profit:** {rec['time_to_profitability']}")
                                st.markdown(f"**Examples:** {', '.join(rec['examples'][:2])}")

                                st.markdown("**Pros:**")
                                for pro in rec['pros'][:3]:
                                    st.markdown(f"- ✅ {pro}")

                                st.markdown("**Cons:**")
                                for con in rec['cons'][:3]:
                                    st.markdown(f"- ⚠️ {con}")

                        # Roadmap
                        roadmap = data.get("roadmap", {})
                        if roadmap:
                            st.subheader("🗺️ Implementation Roadmap")
                            st.markdown(f"**Recommended Model:** {roadmap.get('recommended_model')}")

                            for phase in roadmap.get('phases', [])[:2]:
                                st.markdown(f"**{phase['phase']}**")
                                for activity in phase['activities'][:3]:
                                    st.markdown(f"- {activity}")

                    else:
                        st.error(f"API Error: {response.status_code}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")


def render_stock_analyzer():
    """Stock Analysis Tool"""
    st.header("📈 Stock Analysis")
    st.markdown("Get AI-powered stock analysis with technical and fundamental insights")

    with st.form("stock_analysis_form"):
        query = st.text_input(
            "Enter stock query",
            placeholder="E.g., Should I invest in Apple and Microsoft?"
        )

        col1, col2 = st.columns(2)
        with col1:
            risk_tolerance = st.selectbox("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"])
        with col2:
            horizon = st.selectbox("Investment Horizon", ["Short-term", "Medium-term", "Long-term"])

        submitted = st.form_submit_button("Analyze Stocks")

        if submitted and query:
            with st.spinner("Analyzing stocks..."):
                st.info("📊 Stock analysis feature ready! Connect to backend API at /api/v1/enhanced/stocks/analyze")
                st.markdown("""
                **Expected Output:**
                - Technical Analysis (RSI, MACD, Moving Averages)
                - Fundamental Analysis (P/E, Dividend Yield, Valuation)
                - Buy/Sell/Hold Recommendations
                - Target Prices
                """)


def render_competitor_tracker():
    """Competitor Intelligence Tool"""
    st.header("🏆 Competitor Intelligence")
    st.markdown("Track and analyze your competitors in real-time")

    with st.form("competitor_form"):
        query = st.text_input(
            "Enter competitor query",
            placeholder="E.g., Who are my competitors in the SaaS CRM space?"
        )

        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Your Company Name (optional)")
            industry = st.selectbox("Industry", ["SaaS", "E-commerce", "FinTech", "HealthTech", "Other"])
        with col2:
            product = st.text_input("Product/Service (optional)")

        submitted = st.form_submit_button("Find Competitors")

        if submitted and query:
            with st.spinner("Analyzing competitors..."):
                st.info("🎯 Competitor intelligence ready! Connect to backend API at /api/v1/enhanced/competitors/track")
                st.markdown("""
                **Expected Output:**
                - Top 5 Competitors with profiles
                - Competitive landscape analysis
                - Recent competitor moves (funding, product launches)
                - Strategic recommendations
                """)


def render_subsidies_explorer():
    """Government Subsidies Explorer"""
    st.header("💰 Government Subsidies & Grants")
    st.markdown("Discover government funding opportunities for your business")

    with st.form("subsidies_form"):
        query = st.text_input(
            "Describe your business",
            placeholder="E.g., Tech startup in India looking for seed funding..."
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            industry = st.selectbox("Industry", ["Technology", "Manufacturing", "Services", "Agriculture", "Healthcare"])
        with col2:
            country = st.selectbox("Country", ["India", "USA", "UK", "Singapore"])
        with col3:
            stage = st.selectbox("Business Stage", ["idea", "seed", "growth", "expansion"])

        submitted = st.form_submit_button("Search Subsidies")

        if submitted:
            with st.spinner("Searching for eligible subsidies..."):
                st.info("💰 Subsidies search ready! Connect to backend API at /api/v1/enhanced/subsidies/search")
                st.markdown("""
                **Expected Output:**
                - List of eligible subsidies (₹20L+ potential)
                - Eligibility matching scores
                - Application strategy and timeline
                - Required documents checklist
                """)


# Main execution
if __name__ == "__main__":
    render_enhanced_features_page()
