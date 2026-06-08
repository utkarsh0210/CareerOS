import streamlit as st
from frontend.utils import api_post, score_color


def render():
    st.header("🔍 JD & Resume Analyzer")
    st.caption("Paste a job description and your resume to get a match score, skill gaps, and improvement tips.")

    col1, col2 = st.columns(2)

    with col1:
        jd = st.text_area(
            "Job Description",
            height=300,
            placeholder="Paste the full job description here...\n\nE.g.: We are looking for a Senior Backend Engineer to design scalable APIs using Python and Go...",
            key="jd_input",
        )

    with col2:
        resume = st.text_area(
            "Your Resume",
            height=300,
            placeholder="Paste your resume content here...\n\nE.g.: 2 years at Acme Corp as SWE. Built REST APIs in Node.js. Deployed on AWS. BS CS from MIT 2022...",
            key="resume_input",
        )

    if st.button("⚡ Analyze with AI", type="primary", use_container_width=True):
        if not jd.strip() or not resume.strip():
            st.warning("Please fill in both fields before analyzing.")
            return

        with st.spinner("Gemini is analyzing your resume against the JD..."):
            result = api_post("/analyze/", {"job_description": jd, "resume": resume})

        if not result:
            return

        st.divider()

        # --- Score row ---
        c1, c2, c3 = st.columns(3)
        score = result["match_score"]
        c1.metric("Match Score", f"{score_color(score)} {score}/100")
        c2.metric("Shortlist Likelihood", result["shortlist_likelihood"])
        c3.metric(
            "Status",
            "Strong Candidate" if score >= 75 else ("Borderline" if score >= 55 else "Needs Work"),
        )

        st.progress(score / 100)

        st.info(f"💡 **Key Observation:** {result['key_observation']}")

        # --- Skills ---
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("✅ Matching Skills")
            for skill in result["matching_skills"]:
                st.success(f"  {skill}")

        with col_b:
            st.subheader("❌ Skill Gaps")
            for skill in result["missing_skills"]:
                st.error(f"  {skill}")

        # --- Suggestions ---
        st.subheader("📋 Improvement Suggestions")
        for i, tip in enumerate(result["suggestions"], 1):
            st.markdown(f"**{i}.** {tip}")
