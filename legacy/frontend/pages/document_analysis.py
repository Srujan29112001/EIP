"""
Document Analysis Page
Upload and analyze documents with OCR + VLM
"""
import streamlit as st
import requests
from typing import Dict, Any
import plotly.graph_objects as go


# API Configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000/api/v1")


def render_document_analysis_page():
    """Render document analysis page"""
    st.title("📄 Document Intelligence")
    st.markdown("Upload documents for AI-powered analysis using OCR and Vision Models")

    # Check authentication
    if "access_token" not in st.session_state or not st.session_state.access_token:
        st.warning("Please login first")
        return

    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

    # Upload section
    st.subheader("Upload Document")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=["pdf", "png", "jpg", "jpeg"],
            help="Supported formats: PDF, PNG, JPG"
        )

    with col2:
        use_vlm = st.checkbox(
            "Use Vision AI",
            value=True,
            help="Enable advanced visual analysis (uses GPT-4V)"
        )

        analysis_type = st.selectbox(
            "Analysis Type",
            ["Auto-detect", "Financial Document", "Chart/Graph", "General Document", "Custom"]
        )

    # Custom prompt for analysis
    custom_prompt = None
    if analysis_type == "Custom":
        custom_prompt = st.text_area(
            "Custom Analysis Prompt",
            placeholder="E.g., Extract all financial metrics and compare year-over-year growth"
        )

    # Analyze button
    if uploaded_file is not None:
        if st.button("🔍 Analyze Document", type="primary"):
            with st.spinner("Analyzing document... This may take a minute."):
                try:
                    # Prepare file data
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

                    # Choose endpoint based on analysis type
                    if analysis_type == "Financial Document":
                        endpoint = f"{API_BASE_URL}/analyze/financial-document"
                        response = requests.post(endpoint, headers=headers, files=files)
                    elif analysis_type == "Chart/Graph":
                        endpoint = f"{API_BASE_URL}/analyze/chart"
                        response = requests.post(endpoint, headers=headers, files=files)
                    elif analysis_type == "Custom" and custom_prompt:
                        endpoint = f"{API_BASE_URL}/analyze/image"
                        data = {"prompt": custom_prompt}
                        response = requests.post(endpoint, headers=headers, files=files, data=data)
                    else:
                        # Auto-detect / General
                        endpoint = f"{API_BASE_URL}/analyze/document"
                        data = {"use_vlm": use_vlm}
                        response = requests.post(endpoint, headers=headers, files=files, data=data)

                    if response.status_code == 200:
                        result = response.json()
                        display_analysis_results(result, analysis_type)
                    else:
                        st.error(f"Analysis failed: {response.json().get('detail', 'Unknown error')}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Analysis history
    st.divider()
    st.subheader("Recent Analyses")

    # TODO: Fetch from backend
    if st.button("Show Analysis History"):
        st.info("Feature coming soon: View your analysis history")


def display_analysis_results(result: Dict[str, Any], analysis_type: str):
    """Display analysis results"""
    st.success("✅ Analysis Complete!")

    # Create tabs for different result sections
    if analysis_type == "Financial Document":
        display_financial_results(result)
    elif analysis_type == "Chart/Graph":
        display_chart_results(result)
    else:
        display_general_results(result)

    # Download results
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download as JSON"):
            st.download_button(
                label="Download JSON",
                data=str(result),
                file_name="analysis_results.json",
                mime="application/json"
            )

    with col2:
        if st.button("📄 Generate Report"):
            st.info("Generating comprehensive report...")
            # TODO: Generate PDF report


def display_financial_results(result: Dict[str, Any]):
    """Display financial document analysis results"""
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📝 Extracted Data", "🤖 AI Insights"])

    with tab1:
        st.markdown("### Financial Document Overview")

        # Key metrics
        if "text_extraction" in result:
            entities = result["text_extraction"].get("entities", {})

            col1, col2, col3 = st.columns(3)

            with col1:
                amounts = entities.get("amounts", [])
                if amounts:
                    st.metric("Key Amounts Found", len(amounts))

            with col2:
                dates = entities.get("dates", [])
                if dates:
                    st.metric("Date References", len(dates))

            with col3:
                st.metric("Confidence", f"{result.get('confidence', 0)*100:.1f}%")

    with tab2:
        st.markdown("### Extracted Text & Data")

        if "text_extraction" in result:
            # Raw text
            with st.expander("View Extracted Text"):
                st.text(result["text_extraction"].get("text", ""))

            # Entities
            st.markdown("#### Extracted Entities")
            entities = result["text_extraction"].get("entities", {})

            for entity_type, values in entities.items():
                if values:
                    st.markdown(f"**{entity_type.title()}:**")
                    for value in values[:5]:  # Show top 5
                        st.write(f"- {value}")

    with tab3:
        st.markdown("### AI-Powered Insights")

        if "visual_analysis" in result:
            st.markdown(result["visual_analysis"])
        elif "vlm_analysis" in result:
            st.markdown(result["vlm_analysis"])
        else:
            st.info("No AI insights available")


def display_chart_results(result: Dict[str, Any]):
    """Display chart analysis results"""
    st.markdown("### Chart Analysis")

    if "analysis" in result:
        st.markdown(result["analysis"])

    # TODO: Parse and visualize chart data if available


def display_general_results(result: Dict[str, Any]):
    """Display general document analysis results"""
    tab1, tab2 = st.tabs(["📝 Extracted Text", "🤖 AI Analysis"])

    with tab1:
        st.markdown("### Extracted Text")
        st.text(result.get("text", ""))

        # Document metadata
        with st.expander("Document Metadata"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Document Type", result.get("document_type", "Unknown"))
                st.metric("Confidence", f"{result.get('confidence', 0)*100:.1f}%")
            with col2:
                st.metric("Page Count", result.get("page_count", 1))

        # Entities
        if "entities" in result and result["entities"]:
            st.markdown("#### Extracted Entities")
            entities = result["entities"]

            for entity_type, values in entities.items():
                if values:
                    with st.expander(f"{entity_type.title()} ({len(values)})"):
                        for value in values:
                            st.write(f"- {value}")

    with tab2:
        st.markdown("### AI-Powered Analysis")

        if result.get("vlm_analysis"):
            st.markdown(result["vlm_analysis"])
        else:
            st.info("Vision AI analysis not available. Enable 'Use Vision AI' for enhanced insights.")


# Main entry point
if __name__ == "__main__":
    render_document_analysis_page()
