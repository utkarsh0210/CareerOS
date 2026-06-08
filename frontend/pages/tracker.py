import streamlit as st
from frontend.utils import api_get, api_post, api_patch, api_delete, status_emoji, score_color

STATUSES = ["Applied", "OA", "Interview", "Offer", "Rejected"]


def render():
    st.header("📋 Application Tracker")
    st.caption("Track every application, status, and next action in one place.")

    # ── Add new application ──
    with st.expander("➕ Add New Application", expanded=False):
        with st.form("add_app_form"):
            c1, c2 = st.columns(2)
            company = c1.text_input("Company *", placeholder="e.g. Stripe")
            role = c2.text_input("Role *", placeholder="e.g. Backend Engineer")

            c3, c4, c5 = st.columns(3)
            applied_date = c3.date_input("Applied Date")
            status = c4.selectbox("Status", STATUSES)
            match_score = c5.number_input("Match Score (%)", min_value=0, max_value=100, value=70)

            next_action = st.text_input("Next Action", placeholder="e.g. Follow up in 5 days")

            add_btn = st.form_submit_button("Add Application", type="primary")

        if add_btn:
            if not company.strip() or not role.strip():
                st.warning("Company and Role are required.")
            else:
                result = api_post(
                    "/tracker/",
                    {
                        "company": company,
                        "role": role,
                        "applied_date": str(applied_date),
                        "status": status,
                        "match_score": match_score,
                        "next_action": next_action,
                    },
                )
                if result:
                    st.success(f"✅ Added {company} – {role}")
                    st.rerun()

    # ── Fetch and display ──
    apps = api_get("/tracker/")
    if apps is None:
        return

    if not apps:
        st.info("No applications yet. Add your first one above!")
        return

    # ── Summary metrics ──
    counts = {s: sum(1 for a in apps if a["status"] == s) for s in STATUSES}
    cols = st.columns(len(STATUSES))
    for col, status in zip(cols, STATUSES):
        col.metric(f"{status_emoji(status)} {status}", counts[status])

    st.divider()

    # ── Filter ──
    filter_status = st.selectbox("Filter by status", ["All"] + STATUSES, key="tracker_filter")
    filtered = apps if filter_status == "All" else [a for a in apps if a["status"] == filter_status]

    # ── Table ──
    for app in filtered:
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2, 2, 1.2, 1, 0.8])

            c1.markdown(f"**{app['company']}**  \n<small style='color:gray'>{app['role']}</small>", unsafe_allow_html=True)
            c2.markdown(f"{app.get('next_action','—')}  \n<small style='color:gray'>{app.get('applied_date','')}</small>", unsafe_allow_html=True)
            c3.markdown(f"{status_emoji(app['status'])} **{app['status']}**")

            score = app.get("match_score")
            if score is not None:
                c4.markdown(f"{score_color(score)} **{score}%**")
            else:
                c4.markdown("—")

            with c5:
                new_status = st.selectbox(
                    "Update",
                    STATUSES,
                    index=STATUSES.index(app["status"]),
                    key=f"status_{app['id']}",
                    label_visibility="collapsed",
                )
                if new_status != app["status"]:
                    api_patch(f"/tracker/{app['id']}/status", {"status": new_status})
                    st.rerun()

            st.divider()
