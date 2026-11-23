"""
Water Instrument Student Dashboard — landing page.
Authenticated entry point. After login, routes to the four data pages.
"""

import streamlit as st

import auth
from theme import inject_css, page_header, sidebar_about, AC_COLOR, CC_COLOR, TEXT, TEXT_MUTED

st.set_page_config(
    page_title="Water Instrument Student Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# Block until the user is signed in. Sets data_path / cohort_label / institution
# in session_state for downstream pages.
user = auth.require_login()

# ── Authenticated landing ─────────────────────────────────────────────────────
subtitle = (
    f"{user['cohort_label']} · {user['institution']}"
    if user.get("institution") else user.get("cohort_label", "")
)

page_header(
    f"Welcome back, {user['name'].split()[0]}",
    subtitle or "Where do your students think differently, and what can you do about it?",
)

st.markdown(
    f"""
    <div class="card">
        <p style="color:{TEXT}; line-height:1.6; margin:0;">
            This dashboard displays patterns in how you answered the
            <strong>Water Instrument</strong>, a research-based assessment covering eight of the
            ACS Anchoring Concepts for General Chemistry. Use it to find where your understanding
            may have diverged from the most correct conception, and to find evidence-based
            learning resouces that can help you arrive at a more scientifically accurate
            understanding.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Start here")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f"""
        <div class="card">
            <h4 style="margin-top:0;">My Results</h4>
            <p style="color:{TEXT_MUTED}; font-size:0.85rem; line-height:1.5; margin-bottom:0.5rem;">
                Start here to view your latest assessment feedback.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open results", key="go_radar", use_container_width=True):
        st.switch_page("pages/1_My_Results.py")

with col2:
    st.markdown(
        f"""
        <div class="card">
            <h4 style="margin-top:0;">My Confidence Results</h4>
            <p style="color:{TEXT_MUTED}; font-size:0.85rem; line-height:1.5; margin-bottom:0.5rem;">
                View your confidence results across conceptual areas.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open results", key="go_trends", use_container_width=True):
        st.switch_page("pages/2_My_Confidence_Results.py")

with col3:
    st.markdown(
        f"""
        <div class="card">
            <h4 style="margin-top:0;">My Learning Over Time</h4>
            <p style="color:{TEXT_MUTED}; font-size:0.85rem; line-height:1.5; margin-bottom:0.5rem;">
             View your results across multiple assessment time points to see your progress in chemistry
                understanding and confidence over time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open reflection task", key="go_conf", use_container_width=True):
        st.switch_page("pages/3_My_Learning_Over_Time.py")

with col4:
    st.markdown(
        f"""
        <div class="card">
            <h4 style="margin-top:0;">Reflection Task</h4>
            <p style="color:{TEXT_MUTED}; font-size:0.85rem; line-height:1.5; margin-bottom:0.5rem;">
                Click the button below to access the reflection task on the Blackboard course page.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open reflection", key="go_fourth", use_container_width=True):
        st.switch_page("pages/4_Refle.py")

st.markdown(
    f"""
    <div class="card" style="margin-top:1.25rem;">
        <p style="color:{TEXT_MUTED}; font-size:0.82rem; line-height:1.6; margin:0;">
            <strong style="color:{TEXT};">Why does this tool exist?</strong>
            Instructors can usually identify gaps in student understanding. The harder
            step is moving from <em>what to notice</em> to <em>what to do next</em>. This
            dashboard is built around that step. The
            <span style="color:{CC_COLOR};">tailored resources</span> on the
            Anchoring Concepts Trends page connect each prominent pattern in your data to a
            specific piece of literature or an evidence-based pedagogical tool.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

sidebar_about()
