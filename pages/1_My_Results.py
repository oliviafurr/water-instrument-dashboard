"""
Page 1 — My Results
Per-item response distributions organized by ACS Anchoring Concept, with click-to-expand
item detail (question text, alternate conceptions, vocabulary notes, tailored resources).

When the user arrives via a "View flagged items in {AC}" button on the
Predicted vs. Actual page, st.session_state["preselect_ac"] is set; this page
consumes it once to filter the AC multiselect down to that concept.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import auth
from data import ANCHORING_CONCEPTS, ITEMS, RESOURCES, CORRECT_ANSWERS, get_data
from theme import (
    inject_css, page_header, data_banner, sidebar_about,
    CC_COLOR, AC_COLOR, AC_FADED_COLOR, FLAG_COLOR, TEXT_MUTED, TEXT,
)

st.set_page_config(page_title="Anchoring Concept Trends", page_icon=None, layout="wide")
auth.require_login()
inject_css()

page_header(
    "Anchoring Concept Trends",
    "Response distributions for every question, with expandable details and tailored resources.",
)

df, is_real = get_data()
data_banner(df, is_real)

# ── Summary stats ─────────────────────────────────────────────────────────────
flagged_df = df[df["prominent_ac"] == True]
total_items = len(df)
flagged_count = len(flagged_df)
resource_count = sum(len(v) for v in RESOURCES.values())

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f'<div class="stat"><div class="num">{total_items}</div>'
        f'<div class="label">Total Questions</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f'<div class="stat"><div class="num flag">{flagged_count}</div>'
        f'<div class="label">Questions with Prominent Alternate Conceptions</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f'<div class="stat"><div class="num cc">{resource_count}</div>'
        f'<div class="label">Tailored Resources Available</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Cross-page preselect ─────────────────────────────────────────────────────
# When the user clicked "View flagged items in {AC}" on Predicted vs. Actual,
# session_state["preselect_ac"] is the AC name. We pop it (one-shot), then
# overwrite the multiselect's persisted state so the next render shows that
# AC alone. After the user changes the multiselect, their choice persists
# normally (Streamlit keeps widget state by key).
_preselect_ac = st.session_state.pop("preselect_ac", None)
if _preselect_ac and _preselect_ac in ANCHORING_CONCEPTS:
    st.session_state["ac_filter_widget"] = [_preselect_ac]

# ── Controls ──────────────────────────────────────────────────────────────────
SORT_OPTIONS = [
    ("Question Number",                       "item_number"),
    ("Prominent Alternate Conceptions First", "prominent_first"),
]
SORT_LABELS = [label for label, _ in SORT_OPTIONS]
SORT_LABEL_TO_KEY = {label: key for label, key in SORT_OPTIONS}

# Preset groups of Anchoring Concepts. Edit the labels and the names inside
# each list. The names must match the Anchoring Concept names EXACTLY
# (same spelling, capitalization and punctuation as in the multiselect below).
# None means "all concepts".
AC_PRESETS = {
    "All Anchoring Concepts": None,
    "Assessment Time Point 1": ["AC1: Atoms", "AC2: Bonding", "AC3: Sturcture and Function", "AC5: Reactions"],"],
    "Assessment Time Point 2": ["AC4: Intermolecular Forces",],
    "Assessment Time Point 3": ["AC6: Energy and Thermodynamics", "AC7: Kinetics"],
    "Assessment Time Point 4": ["AC8: Equilibrium"],
}

ALL_ACS = list(ANCHORING_CONCEPTS.keys())

# Start with every concept selected the first time the page loads.
if "ac_filter_widget" not in st.session_state:
    st.session_state["ac_filter_widget"] = ALL_ACS


def _apply_preset():
    """Runs when the Quick view dropdown changes; fills in the multiselect."""
    names = AC_PRESETS[st.session_state["ac_preset"]]
    if names is None:
        st.session_state["ac_filter_widget"] = ALL_ACS
    else:
        # Keep only names that really exist, so a typo can't crash the page.
        st.session_state["ac_filter_widget"] = [n for n in names if n in ANCHORING_CONCEPTS]


col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([2, 2, 2, 2])
with col_ctrl1:
    sort_label = st.selectbox(
        "Sort questions within each Anchoring Concept by",
        SORT_LABELS,
    )
    sort_key = SORT_LABEL_TO_KEY[sort_label]
with col_ctrl2:
    show_flagged_only = st.checkbox("Show Flagged Questions Only", value=False)
with col_ctrl3:
    st.selectbox(
        "Quick view: preset Anchoring Concepts",
        list(AC_PRESETS.keys()),
        key="ac_preset",
        on_change=_apply_preset,
    )
with col_ctrl4:
    selected_acs = st.multiselect(
        "Filter by Anchoring Concept",
        ALL_ACS,
        key="ac_filter_widget",
    )

# ── Legend ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="legend-row">
        <span><span class="legend-dot" style="background:{CC_COLOR};"></span> Most Correct Conception</span>
        <span><span class="legend-dot" style="background:{AC_COLOR};"></span> Prominent Alternate Conception</span>
        <span><span class="legend-dot" style="background:{AC_FADED_COLOR};"></span> Alternate Conception</span>
        <span style="color:{FLAG_COLOR}; font-weight:600;">▲ Flagged for follow-up</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _prominent_set(row) -> set:
    """Return the set of choice numbers (1..4) flagged as prominent for this
    row. Empty set when no AC crosses the prominence threshold."""
    raw = row.get("prominent_choices")
    if raw is None:
        return set()
    try:
        return {int(c) for c in raw if c is not None}
    except TypeError:
        return set()


def _pill_style(choice: int, correct: int, prominent_set: set):
    """Return (pill_class, role_tag) for a given answer choice."""
    if choice == correct:
        return "pill cc", "Most Correct Conception"
    if choice in prominent_set:
        return "pill prominent", "Prominent Alternate Conception"
    return "pill ac", "Alternate Conception"


def render_resource_card(res: dict) -> str:
    """Return the HTML for one tailored-resource card."""
    return (
        f'<div class="resource-card">'
        f'<div class="resource-title">'
        f'<span class="resource-type">{res["type"]}</span>'
        f'<a href="{res["url"]}" target="_blank">{res["title"]}</a>'
        f'</div>'
        f'<p style="font-size:0.85rem; color:{TEXT_MUTED}; margin:0.4rem 0 0 0;">'
        f'{res["description"]}</p>'
        f'<div class="note asset" style="margin-top:0.5rem;">'
        f'<span class="label">Asset framing</span>{res["asset_note"]}</div>'
        f'</div>'
    )


def _choice_text(choice: int, correct: int, item: dict) -> str:
    """Return the conception text for a given answer choice (1..4).

    The alternate_conceptions list is stored in choice-number order
    (skipping the correct choice), so for correct=3 the wrong choices
    are [1, 2, 4] and map to alternate_conceptions[0], [1], [2].
    """
    if choice == correct:
        return item["correct_conception"]
    wrong_choices = [c for c in range(1, 5) if c != correct]
    try:
        ac_idx = wrong_choices.index(choice)
        return item["alternate_conceptions"][ac_idx]
    except (ValueError, IndexError):
        return ""


def render_inline_summary(iid: int, row, item: dict) -> None:
    """Compact summary shown under each question label.
    Walks A..D order. Shows the correct conception always, plus any alternate
    conception that at least one student selected."""
    counts = row["choice_counts"]
    correct = CORRECT_ANSWERS[iid]
    prominent_set = _prominent_set(row)
    n_choices = 1 + len(item["alternate_conceptions"])

    blocks = []
    for choice in (1, 2, 3, 4):
        if choice > n_choices:
            continue

        count = counts.get(choice, 0)
        is_correct = choice == correct

        # Skip alternate conceptions nobody selected
        if not is_correct and count == 0:
            continue

        letter = chr(ord("A") + choice - 1)
        text = _choice_text(choice, correct, item)
        pill_class, role_tag = _pill_style(choice, correct, prominent_set)
        selected_tag = " &middot; Student selected" if count > 0 else ""

        blocks.append(
            f'<div style="margin-bottom:0.6rem;">'
            f'<span class="{pill_class}">{letter} &middot; '
            f'<span style="font-weight:600;">{role_tag}</span>{selected_tag}</span>'
            f'<p style="color:{TEXT_MUTED}; font-size:0.82rem; line-height:1.5; '
            f'margin:0.3rem 0 0 0;">{text}</p>'
            f'</div>'
        )

    st.markdown("".join(blocks), unsafe_allow_html=True)


def render_full_detail(iid: int, row, item: dict, is_flagged: bool) -> None:
    """Full item detail: question text, all conceptions in A..D order,
    vocabulary note, and tailored resources."""
    correct = CORRECT_ANSWERS[iid]
    prominent_set = _prominent_set(row)
    n_choices = 1 + len(item["alternate_conceptions"])

    # Question text
    st.markdown(
        f'<p style="font-size:1rem; font-weight:500; color:{TEXT}; '
        f'margin:0 0 0.9rem 0; line-height:1.5;">{item["text"]}</p>',
        unsafe_allow_html=True,
    )

    # All conceptions in A..D order
    for choice in (1, 2, 3, 4):
        if choice > n_choices:
            continue
        letter = chr(ord("A") + choice - 1)
        text = _choice_text(choice, correct, item)
        pill_class, role_tag = _pill_style(choice, correct, prominent_set)

        st.markdown(
            f'<div style="margin-bottom:0.6rem;">'
            f'<span class="{pill_class}">{letter} &middot; {role_tag}</span>'
            f'<p style="color:{TEXT}; font-size:0.88rem; line-height:1.5; '
            f'margin:0.3rem 0 0 0.5rem;">{text}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Vocabulary notes follow the same gating rule as tailored resources:
    # only surface them when the item has at least one prominent AC.
    if is_flagged and item.get("vocab_note"):
        st.markdown(
            f'<div class="note"><span class="label">Vocabulary</span>'
            f'{item["vocab_note"]}</div>',
            unsafe_allow_html=True,
        )

    # Tailored resources (only for flagged items)
    if is_flagged and iid in RESOURCES:
        st.markdown(
            f'<p style="color:{TEXT_MUTED}; font-size:0.82rem; line-height:1.5; '
            f'margin:0.9rem 0 0.4rem 0;">'
            "Tailored pedagogical resources for this prominent alternate conception. "
            "These are framed positioning alternate conceptions as "
            "productive starting points rather than errors to correct."
            "</p>",
            unsafe_allow_html=True,
        )
        resources_html = "".join(render_resource_card(res) for res in RESOURCES[iid])
        st.markdown(resources_html, unsafe_allow_html=True)
    elif is_flagged:
        st.markdown(
            f'<p style="color:{TEXT_MUTED}; font-size:0.82rem; margin-top:0.9rem;">'
            "Resources for this alternate conception are being developed. "
            "The resource library grows as CER literature and tools expand.</p>",
            unsafe_allow_html=True,
        )


# ── Per-AC blocks ─────────────────────────────────────────────────────────────
for ac_name, ac_info in ANCHORING_CONCEPTS.items():
    if ac_name not in selected_acs:
        continue

    ac_items = [i for i in ac_info["items"] if i in ITEMS]
    ac_df = df[df["item_id"].isin(ac_items)].copy()

    if show_flagged_only:
        ac_df = ac_df[ac_df["prominent_ac"] == True]
        if ac_df.empty:
            continue

    if sort_key == "prominent_first":
        # Flagged items first; within each group, fall back to item number.
        ac_df = ac_df.sort_values(["prominent_ac", "item_id"], ascending=[False, True])
    else:  # item_number, default
        ac_df = ac_df.sort_values("item_id")

    n_flagged_in_ac = int(ac_df["prominent_ac"].sum())
    flag_html = (
        f'<span class="flag-badge">{n_flagged_in_ac} flagged</span>'
        if n_flagged_in_ac > 0 else ""
    )

    st.markdown(
        f'<div class="card" style="margin-bottom:0.5rem;">'
        f'<div style="display:flex; align-items:center; gap:0.5rem;">'
        f'<h3 style="margin:0;">{ac_name}</h3>{flag_html}</div>'
        f'<p style="color:{TEXT_MUTED}; font-size:0.82rem; margin: 0.25rem 0 0;">'
        f'{ac_info["description"]}</p></div>',
        unsafe_allow_html=True,
    )

    for _, row in ac_df.iterrows():
        iid = int(row["item_id"])
        item = ITEMS[iid]
        is_flagged = bool(row["prominent_ac"])

        # Question label
        flag_suffix = "  ▲" if is_flagged else ""
        st.markdown(
            f'<p style="font-size:0.95rem; font-weight:600; margin:0.8rem 0 0.3rem 0; '
            f'color:{FLAG_COLOR if is_flagged else TEXT};">Question {iid}{flag_suffix}</p>',
            unsafe_allow_html=True,
        )
        render_inline_summary(iid, row, item)

        # Click-to-expand: full question text, all conceptions, vocab, resources
        expander_label = (
            f"Full detail and resources for Question {iid}"
            if is_flagged
            else f"Full detail for Question {iid}"
        )
        with st.expander(expander_label):
            render_full_detail(iid, row, item, is_flagged)

sidebar_about()