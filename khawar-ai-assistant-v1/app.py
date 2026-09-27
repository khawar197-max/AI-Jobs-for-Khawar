import streamlit as st
from pathlib import Path

from modules.ai import AIClient
from modules.job_search import search_opportunities
from modules.cv_generator import build_tailored_cv, build_cover_letter
from modules.utils import load_profile, save_json, load_json


st.set_page_config(
    page_title="Khawar AI Career Assistant",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# FILES
# ============================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

PROFILE_FILE = DATA_DIR / "profile.json"
SAVED_FILE = DATA_DIR / "saved_opportunities.json"
APPLIED_FILE = DATA_DIR / "applied_opportunities.json"


# ============================================================
# LOAD DATA
# ============================================================

profile = load_profile(PROFILE_FILE)

saved = load_json(
    SAVED_FILE,
    []
)

applied = load_json(
    APPLIED_FILE,
    []
)


# ============================================================
# SESSION STATE
# ============================================================

if "results" not in st.session_state:
    st.session_state.results = []

if "selected" not in st.session_state:
    st.session_state.selected = None

if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""

if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = ""


# ============================================================
# HEADER
# ============================================================

st.title("🤖 Khawar AI Career Assistant")

st.caption(
    "Jobs • Remote Work • PhD • Scholarships • "
    "Tailored CV • Cover Letters • Application Tracking"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🔎 Search Opportunities")

    search_type = st.selectbox(
        "Opportunity type",
        [
            "Jobs",
            "Fully Funded PhD / Scholarships",
            "Jobs + PhD / Scholarships",
        ],
    )

    career_area = st.selectbox(
        "Career area",
        [
            "All Career Areas",
            "Civil Engineering",
            "Geotechnical Engineering",
            "Highway & Transportation",
            "Urban Planning",
            "GIS",
            "Smart Cities",
            "Project Management",
            "Administration & Operations",
            "Data Entry",
            "Virtual Assistant",
            "Digital Marketing",
            "Social Media Management",
            "Content Management",
            "AI & Automation",
            "Research",
        ],
    )

    location = st.selectbox(
        "Location",
        [
            "Worldwide",
            "Pakistan",
            "Europe",
            "USA & Canada",
            "Gulf / Middle East",
            "Asia-Pacific",
        ],
    )

    work_mode = st.selectbox(
        "Work mode",
        [
            "Any",
            "Remote",
            "On-site",
            "Hybrid",
        ],
    )

    funding = st.selectbox(
        "Funding",
        [
            "Any",
            "Fully funded",
            "Funded / stipend",
            "Scholarship",
        ],
    )

    max_results = st.slider(
        "Number of results",
        5,
        50,
        20,
    )

    exclude_municipal = st.checkbox(
        "Exclude Municipal Officer/local-government jobs in Pakistan",
        value=True,
    )

    custom_keywords = st.text_input(
        "Extra keywords",
        placeholder="e.g. Excel, AutoCAD, Python, SEO, Canva",
    )

    search_button = st.button(
        "🚀 Search opportunities",
        use_container_width=True,
        type="primary",
    )


# ============================================================
# TABS
# ============================================================

tabs = st.tabs(
    [
        "🔎 Opportunities",
        "📄 Tailored CV",
        "✉️ Cover Letter",
        "📋 Applications",
        "👤 My Profile",
        "⭐ Saved",
    ]
)


# ============================================================
# SEARCH
# ============================================================

if search_button:

    with st.spinner(
        "Searching multiple career areas and analyzing opportunities..."
    ):

        ai = AIClient()

        results = search_opportunities(
            profile=profile,
            opportunity_type=search_type,
            location=location,
            work_mode=work_mode,
            funding=funding,
            custom_keywords=custom_keywords,
            max_results=max_results,
            exclude_municipal=exclude_municipal,
            ai=ai,
            career_area=career_area,
        )

        st.session_state.results = results
        st.session_state.selected = None

    st.toast(
        f"Found {len(results)} opportunities."
    )


# ============================================================
# OPPORTUNITIES TAB
# ============================================================

with tabs[0]:

    st.subheader("Matching Opportunities")

    results = st.session_state.results

    if not results:

        st.info(
            "Select your career area and filters from the sidebar, "
            "then click **Search opportunities**."
        )

    else:

        st.success(
            f"Found {len(results)} analyzed opportunities."
        )

        for i, item in enumerate(results):

            with st.container(border=True):

                c1, c2 = st.columns(
                    [5, 1]
                )

                with c1:

                    st.markdown(
                        f"### {item.get('title', 'Untitled opportunity')}"
                    )

                    st.write(
                        f"**Organization:** "
                        f"{item.get('organization', 'Not stated')}  \n"
                        f"**Location:** "
                        f"{item.get('location', 'Not stated')}  \n"
                        f"**Career area:** "
                        f"{item.get('career_area', 'General')}  \n"
                        f"**Type:** "
                        f"{item.get('type', 'Opportunity')}  \n"
                        f"**Source:** "
                        f"{item.get('source', 'Web')}"
                    )

                with c2:

                    st.metric(
                        "Match",
                        f"{item.get('match_score', 0)}%"
                    )

                st.write(
                    item.get(
                        "summary",
                        ""
                    )
                )

                if item.get("match_reasons"):

                    st.markdown(
                        "**Why it matches:**"
                    )

                    for reason in item["match_reasons"]:

                        st.write(
                            f"• {reason}"
                        )

                if item.get("deadline"):

                    st.write(
                        f"**Deadline:** "
                        f"{item['deadline']}"
                    )

                if item.get("url"):

                    st.link_button(
                        "🌐 Open opportunity",
                        item["url"]
                    )

                b1, b2, b3, b4 = st.columns(4)

                # ------------------------------------------------
                # Tailor CV
                # ------------------------------------------------

                if b1.button(
                    "📄 Tailor CV",
                    key=f"cv_{i}"
                ):

                    st.session_state.selected = item

                    with st.spinner(
                        "Generating tailored CV..."
                    ):

                        st.session_state.cv_text = (
                            build_tailored_cv(
                                profile,
                                item
                            )
                        )

                    st.toast(
                        "Tailored CV generated."
                    )

                # ------------------------------------------------
                # Cover Letter
                # ------------------------------------------------

                if b2.button(
                    "✉️ Cover Letter",
                    key=f"cl_{i}"
                ):

                    st.session_state.selected = item

                    with st.spinner(
                        "Generating cover letter..."
                    ):

                        st.session_state.cover_letter = (
                            build_cover_letter(
                                profile,
                                item
                            )
                        )

                    st.toast(
                        "Cover letter generated."
                    )

                # ------------------------------------------------
                # Save
                # ------------------------------------------------

                if b3.button(
                    "⭐ Save",
                    key=f"save_{i}"
                ):

                    already_saved = any(
                        x.get("url") == item.get("url")
                        for x in saved
                    )

                    if not already_saved:

                        saved.append(item)

                        save_json(
                            SAVED_FILE,
                            saved
                        )

                        st.toast(
                            "Opportunity saved."
                        )

                    else:

                        st.info(
                            "Already saved."
                        )

                # ------------------------------------------------
                # Mark Applied
                # ------------------------------------------------

                if b4.button(
                    "✅ Applied",
                    key=f"apply_{i}"
                ):

                    already_applied = any(
                        x.get("url") == item.get("url")
                        for x in applied
                    )

                    if not already_applied:

                        item_copy = dict(item)

                        item_copy["status"] = "Applied"

                        applied.append(
                            item_copy
                        )

                        save_json(
                            APPLIED_FILE,
                            applied
                        )

                        st.toast(
                            "Added to Applications."
                        )

                    else:

                        st.info(
                            "Already in Applications."
                        )


# ============================================================
# TAILORED CV
# ============================================================

with tabs[1]:

    st.subheader("📄 Tailored CV")

    if st.session_state.cv_text:

        st.text_area(
            "CV content",
            st.session_state.cv_text,
            height=550,
        )

        st.download_button(
            "⬇️ Download CV as TXT",
            st.session_state.cv_text,
            file_name="tailored_cv.txt",
            mime="text/plain",
        )

    else:

        st.info(
            "Select an opportunity and click "
            "**Tailor CV**."
        )


# ============================================================
# COVER LETTER
# ============================================================

with tabs[2]:

    st.subheader("✉️ Cover Letter")

    if st.session_state.cover_letter:

        st.text_area(
            "Cover letter",
            st.session_state.cover_letter,
            height=500,
        )

        st.download_button(
            "⬇️ Download Cover Letter",
            st.session_state.cover_letter,
            file_name="cover_letter.txt",
            mime="text/plain",
        )

    else:

        st.info(
            "Select an opportunity and click "
            "**Cover Letter**."
        )


# ============================================================
# APPLICATION TRACKER
# ============================================================

with tabs[3]:

    st.subheader("📋 My Applications")

    if not applied:

        st.info(
            "No applications tracked yet. "
            "Click **✅ Applied** on an opportunity."
        )

    else:

        st.write(
            f"**Total applications: {len(applied)}**"
        )

        for i, item in enumerate(applied):

            with st.container(border=True):

                st.markdown(
                    f"### {item.get('title', 'Untitled')}"
                )

                st.write(
                    f"**Organization:** "
                    f"{item.get('organization', 'Not stated')}  \n"
                    f"**Location:** "
                    f"{item.get('location', 'Not stated')}  \n"
                    f"**Career:** "
                    f"{item.get('career_area', 'General')}"
                )

                status = st.selectbox(
                    "Application status",
                    [
                        "Applied",
                        "Under Review",
                        "Interview",
                        "Offer",
                        "Rejected",
                    ],
                    index=[
                        "Applied",
                        "Under Review",
                        "Interview",
                        "Offer",
                        "Rejected",
                    ].index(
                        item.get(
                            "status",
                            "Applied"
                        )
                    ),
                    key=f"status_{i}",
                )

                if status != item.get("status"):

                    item["status"] = status

                    save_json(
                        APPLIED_FILE,
                        applied
                    )

                    st.success(
                        "Status updated."
                    )

                if item.get("url"):

                    st.link_button(
                        "🌐 Open opportunity",
                        item["url"]
                    )


# ============================================================
# PROFILE
# ============================================================

with tabs[4]:

    st.subheader(
        "👤 Your Career Profile"
    )

    st.json(profile)

    st.caption(
        "Edit data/profile.json in GitHub "
        "to permanently update your profile."
    )


# ============================================================
# SAVED
# ============================================================

with tabs[5]:

    st.subheader(
        "⭐ Saved Opportunities"
    )

    if not saved:

        st.info(
            "No saved opportunities yet."
        )

    else:

        for item in saved:

            with st.container(border=True):

                st.markdown(
                    f"### {item.get('title', 'Untitled')}"
                )

                st.write(
                    f"{item.get('organization', '')} • "
                    f"{item.get('location', '')} • "
                    f"Career: {item.get('career_area', 'General')} • "
                    f"Match: {item.get('match_score', 0)}%"
                )

                if item.get("url"):

                    st.link_button(
                        "🌐 Open",
                        item["url"]
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Khawar AI Career Assistant V2 • "
    "Personal career research and application tool"
)
