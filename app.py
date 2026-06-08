import streamlit as st

st.set_page_config(
    page_title="CareerOS — AI Career Copilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

from frontend.pages import dashboard, analyzer, tailor, network, interview, tracker

# ── Sidebar navigation ──
with st.sidebar:
    st.markdown("## 🚀 CareerOS")
    st.caption("AI-Powered Job Copilot")
    st.divider()

    st.markdown("**Workspace**")
    pages = {
        "🏠 Dashboard": "dashboard",
        "🔍 JD Analyzer": "analyzer",
        "✨ Resume Tailor": "tailor",
        "🤝 Networking": "network",
        "🎤 Interview Coach": "interview",
        "📋 Application Tracker": "tracker",
    }

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    for label, key in pages.items():
        if st.button(label, use_container_width=True, key=f"nav_{key}"):
            st.session_state.page = key

    st.divider()
    st.caption("Powered by **Gemini 1.5 Flash** (free tier)")
    st.caption("Backend: FastAPI · Frontend: Streamlit")

# ── Route to page ──
page = st.session_state.get("page", "dashboard")

if page == "dashboard":
    dashboard.render()
elif page == "analyzer":
    analyzer.render()
elif page == "tailor":
    tailor.render()
elif page == "network":
    network.render()
elif page == "interview":
    interview.render()
elif page == "tracker":
    tracker.render()
