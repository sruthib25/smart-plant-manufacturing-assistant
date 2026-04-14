import streamlit as st

st.set_page_config(
    page_title="Smart Plant Manager",
    layout="wide",
)

st.title("🏭 Smart Manufacturing Hub")

st.markdown("""
### Welcome to the Smart Manufacturing Plant Monitoring System

**Modules:**
- **[Dashboard](/dashboard)**: Real-time sensor monitoring.
- **[AI Assistant](/chat)**: RAG-powered expert chatbot.

**Status:**
- Backend: `Online` (Assumed)
- Vector DB: `Loaded`
- Model: `TinyLlama` (Local)
""")

st.info("Navigate using the sidebar to access different modules.")
