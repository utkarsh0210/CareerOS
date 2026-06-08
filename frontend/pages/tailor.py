import streamlit as st
from frontend.utils import api_post


def render():
    st.header("✨ Resume Tailoring Engine")
    st.caption("Optimize your resume sections for a specific role while preserving your authentic voice.")

    with st.form("tailor_form"):
        target_role = st.text_input(
            "Target Role & Company",
            placeholder="e.g. Senior Backend Engineer at Stripe",
        )

        resume = st.text_area(
            "Your Current Resume",
            height=250,
            placeholder="Paste your full resume here...",
        )

        st.markdown("**Sections to optimize:**")
        c1, c2, c3, c4 = st.columns(4)
        opt_summary = c1.checkbox("Summary", value=True)
        opt_skills = c2.checkbox("Skills", value=True)
        opt_exp = c3.checkbox("Experience", value=True)
        opt_projects = c4.checkbox("Projects", value=False)

        submitted = st.form_submit_button("🚀 Optimize Resume", type="primary", use_container_width=True)

    if submitted:
        if not target_role.strip() or not resume.strip():
            st.warning("Please fill in both the target role and your resume.")
            return

        with st.spinner("Gemini is tailoring your resume..."):
            result = api_post(
                "/tailor/",
                {
                    "target_role": target_role,
                    "resume": resume,
                    "optimize_summary": opt_summary,
                    "optimize_skills": opt_skills,
                    "optimize_experience": opt_exp,
                    "optimize_projects": opt_projects,
                },
            )

        if not result:
            return

        st.divider()
        st.success(f"✅ Resume optimized for: **{target_role}**")

        tabs = []
        tab_names = []
        if opt_summary and result.get("optimized_summary"):
            tab_names.append("📝 Summary")
        if opt_skills and result.get("optimized_skills"):
            tab_names.append("🛠 Skills")
        if opt_exp and result.get("optimized_experience"):
            tab_names.append("💼 Experience")
        if opt_projects and result.get("optimized_projects"):
            tab_names.append("🔬 Projects")

        if tab_names:
            tabs = st.tabs(tab_names)
            idx = 0
            if opt_summary and result.get("optimized_summary"):
                with tabs[idx]:
                    st.markdown(result["optimized_summary"])
                    st.code(result["optimized_summary"], language=None)
                idx += 1
            if opt_skills and result.get("optimized_skills"):
                with tabs[idx]:
                    st.markdown(result["optimized_skills"])
                    st.code(result["optimized_skills"], language=None)
                idx += 1
            if opt_exp and result.get("optimized_experience"):
                with tabs[idx]:
                    st.markdown(result["optimized_experience"])
                    st.code(result["optimized_experience"], language=None)
                idx += 1
            if opt_projects and result.get("optimized_projects"):
                with tabs[idx]:
                    st.markdown(result["optimized_projects"])
                    st.code(result["optimized_projects"], language=None)

        if result.get("tips"):
            st.subheader("💡 Quick Win Tips")
            for tip in result["tips"]:
                st.info(tip)
