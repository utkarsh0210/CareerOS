import streamlit as st
from frontend.utils import api_get, status_emoji, score_color


def render():
    st.header("🚀 CareerOS Dashboard")
    st.caption("Your AI-powered job search command center.")

    # ── Fetch applications ──
    apps = api_get("/tracker/") or []

    total = len(apps)
    statuses = ["Applied", "OA", "Interview", "Offer", "Rejected"]
    counts = {s: sum(1 for a in apps if a["status"] == s) for s in statuses}

    # ── Top metrics ──
    st.subheader("📊 Pipeline Overview")

    if not apps:
        st.info("No applications yet. Head to **📋 Application Tracker** to add your first one!")
        st.divider()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📨 Applied", counts["Applied"])
    c2.metric("💻 OA", counts["OA"])
    c3.metric("🎯 Interviews", counts["Interview"])
    c4.metric("🎉 Offers", counts["Offer"])
    c5.metric("❌ Rejected", counts["Rejected"])

    # ── Conversion rates ──
    st.subheader("📈 Funnel Conversion")
    col1, col2 = st.columns(2)
    with col1:
        if total > 0:
            resp_rate = round((counts["OA"] + counts["Interview"] + counts["Offer"]) / total * 100, 1)
            st.metric("Response Rate", f"{resp_rate}%", help="(OA + Interview + Offer) / Total Applied")
            st.progress(resp_rate / 100)

            interview_rate = round((counts["Interview"] + counts["Offer"]) / max(total, 1) * 100, 1)
            st.metric("Interview Rate", f"{interview_rate}%")
            st.progress(interview_rate / 100)

            offer_rate = round(counts["Offer"] / max(total, 1) * 100, 1)
            st.metric("Offer Rate", f"{offer_rate}%")
            st.progress(offer_rate / 100)
        else:
            st.info("Add applications to see conversion metrics.")

    with col2:
        st.subheader("🗂 Recent Applications")
        recent = sorted(apps, key=lambda a: a.get("applied_date", ""), reverse=True)[:5]
        if recent:
            for app in recent:
                score = app.get("match_score")
                sc = f" · {score_color(score)} {score}%" if score else ""
                st.markdown(
                    f"**{app['company']}** — {app['role']}  \n"
                    f"{status_emoji(app['status'])} {app['status']}{sc} · _{app.get('applied_date', '')}_"
                )
                st.divider()
        else:
            st.info("No applications yet.")

    # ── Quick navigation ──
    st.divider()
    st.subheader("⚡ Quick Actions")
    c1, c2, c3, c4 = st.columns(4)
    c1.page_link("app.py", label="🔍 Analyze JD", help="Go to JD Analyzer")
    c2.page_link("app.py", label="✨ Tailor Resume", help="Go to Resume Tailor")
    c3.page_link("app.py", label="🤝 Networking", help="Go to Networking")
    c4.page_link("app.py", label="🎤 Mock Interview", help="Go to Interview Coach")

    # ── Tips ──
    st.divider()
    st.subheader("💡 Career Intelligence Tips")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Resume Tailoring** lifts response rates by ~18%. Always tailor before applying.")
        st.info("**Networking outreach** is 3x more effective than cold applications.")
    with col2:
        st.warning("**Interview rate** below 10%? Focus on match score — target roles above 70%.")
        st.success("**Practice 2-3 mock interviews/week** to consistently score 8+/10.")
