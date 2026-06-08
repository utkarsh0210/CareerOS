import streamlit as st
from frontend.utils import api_post

INTERVIEW_TYPES = {
    "Technical (DSA / System Design)": "technical",
    "Behavioral (STAR Method)": "behavioral",
    "Mixed (Technical + Behavioral)": "mixed",
    "Product Sense": "product",
}


def render():
    st.header("🎤 AI Interview Coach")
    st.caption("Generate role-specific questions, answer them, and get AI feedback instantly.")

    # ── Session state init ──
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "current_q" not in st.session_state:
        st.session_state.current_q = 0
    if "scores" not in st.session_state:
        st.session_state.scores = []
    if "interview_active" not in st.session_state:
        st.session_state.interview_active = False
    if "interview_role" not in st.session_state:
        st.session_state.interview_role = ""
    if "interview_type" not in st.session_state:
        st.session_state.interview_type = "mixed"

    # ── Setup panel (shown before interview starts) ──
    if not st.session_state.interview_active:
        with st.form("interview_setup"):
            st.subheader("Setup Your Mock Interview")
            role = st.text_input("Role you're interviewing for", placeholder="e.g. Software Engineer II at Google")

            c1, c2 = st.columns(2)
            itype_label = c1.selectbox("Interview Type", list(INTERVIEW_TYPES.keys()), index=2)
            num_q = c2.number_input("Number of questions", min_value=3, max_value=10, value=5)

            jd = st.text_area(
                "Paste relevant JD snippet (optional)",
                height=100,
                placeholder="Key requirements from the JD...",
            )

            gen = st.form_submit_button("📋 Generate Question Bank", type="primary", use_container_width=True)

        if gen:
            if not role.strip():
                st.warning("Please enter the role you're interviewing for.")
                return
            with st.spinner("Gemini is generating your question bank..."):
                result = api_post(
                    "/interview/questions",
                    {
                        "role": role,
                        "interview_type": INTERVIEW_TYPES[itype_label],
                        "jd_snippet": jd,
                        "num_questions": num_q,
                    },
                )
            if not result or not result.get("questions"):
                st.error("Failed to generate questions.")
                return

            st.session_state.questions = result["questions"]
            st.session_state.interview_role = role
            st.session_state.interview_type = INTERVIEW_TYPES[itype_label]
            st.session_state.current_q = 0
            st.session_state.scores = []

            st.success(f"✅ Generated {len(result['questions'])} questions!")
            st.subheader("Your Question Bank")
            for i, q in enumerate(result["questions"], 1):
                st.markdown(f"**Q{i}.** {q}")

            if st.button("▶️ Start Mock Interview", type="primary", use_container_width=True):
                st.session_state.interview_active = True
                st.rerun()

        return

    # ── Active interview ──
    questions = st.session_state.questions
    cq = st.session_state.current_q

    # Sidebar-style stats
    st.markdown(
        f"**Progress:** Question {min(cq + 1, len(questions))} of {len(questions)} &nbsp;|&nbsp; "
        f"**Avg Score:** {round(sum(st.session_state.scores)/len(st.session_state.scores), 1) if st.session_state.scores else '—'}/10"
    )
    st.progress((cq) / len(questions))

    if cq >= len(questions):
        # ── Session complete ──
        st.balloons()
        st.success("🎉 Mock interview complete!")
        avg = round(sum(st.session_state.scores) / len(st.session_state.scores), 1) if st.session_state.scores else 0
        st.metric("Final Average Score", f"{avg}/10")

        for i, (q, s) in enumerate(zip(questions, st.session_state.scores), 1):
            color = "🟢" if s >= 7 else ("🟡" if s >= 5 else "🔴")
            st.markdown(f"{color} **Q{i}** ({s}/10): {q}")

        if st.button("🔄 Start New Interview", use_container_width=True):
            st.session_state.interview_active = False
            st.session_state.questions = []
            st.session_state.current_q = 0
            st.session_state.scores = []
            st.rerun()
        return

    # ── Current question ──
    st.divider()
    st.subheader(f"Question {cq + 1}")
    st.info(questions[cq])

    answer = st.text_area(
        "Your Answer",
        height=180,
        placeholder="Be detailed. Use the STAR method for behavioral questions (Situation → Task → Action → Result).",
        key=f"answer_{cq}",
    )

    if st.button("📤 Submit Answer & Get Feedback", type="primary", use_container_width=True):
        if not answer.strip():
            st.warning("Please write your answer before submitting.")
            return

        with st.spinner("Gemini is evaluating your answer..."):
            eval_result = api_post(
                "/interview/evaluate",
                {
                    "question": questions[cq],
                    "answer": answer,
                    "role": st.session_state.interview_role,
                    "interview_type": st.session_state.interview_type,
                },
            )

        if not eval_result:
            return

        score = eval_result["score"]
        st.session_state.scores.append(score)

        st.divider()
        col1, col2 = st.columns(2)
        col1.metric("Score", f"{score}/10")
        col2.metric("Rating", "Excellent" if score >= 8 else ("Good" if score >= 6 else "Needs Work"))

        st.progress(score / 10)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("✅ Strengths")
            for s in eval_result.get("strengths", []):
                st.success(s)
        with c2:
            st.subheader("📈 Improvements")
            for imp in eval_result.get("improvements", []):
                st.warning(imp)

        if eval_result.get("ideal_answer_hint"):
            st.info(f"💡 **Ideal answer would include:** {eval_result['ideal_answer_hint']}")

        if eval_result.get("overall_feedback"):
            st.markdown(f"> {eval_result['overall_feedback']}")

        st.session_state.current_q += 1

        if st.session_state.current_q < len(questions):
            if st.button("➡️ Next Question", type="primary"):
                st.rerun()
        else:
            if st.button("🏁 View Results", type="primary"):
                st.rerun()
