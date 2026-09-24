import streamlit as st
from pathlib import Path
from modules.ai import AIClient
from modules.job_search import search_opportunities
from modules.cv_generator import build_tailored_cv, build_cover_letter
from modules.utils import load_profile, save_json, load_json, clean_text

st.set_page_config(
    page_title="Khawar AI Career Assistant",
    page_icon="🤖",
    layout="wide",
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

PROFILE_FILE = DATA_DIR / "profile.json"
SAVED_FILE = DATA_DIR / "saved_opportunities.json"

profile = load_profile(PROFILE_FILE)
saved = load_json(SAVED_FILE, [])

if "results" not in st.session_state:
    st.session_state.results = []
if "selected" not in st.session_state:
    st.session_state.selected = None
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""
if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = ""

st.title("🤖 Khawar AI Career Assistant")
st.caption("Jobs • Remote Work • Fully Funded PhD • Scholarships • Tailored CV • Cover Letters")

with st.sidebar:
    st.header("Search")
    search_type = st.selectbox(
        "Opportunity type",
        ["Jobs", "Fully Funded PhD / Scholarships", "Jobs + PhD / Scholarships"],
    )
    location = st.selectbox(
        "Location",
        ["Worldwide", "Pakistan", "Europe", "USA & Canada", "Gulf / Middle East", "Asia-Pacific"],
    )
    work_mode = st.selectbox("Work mode", ["Any", "Remote", "On-site", "Hybrid"])
    funding = st.selectbox("Funding", ["Any", "Fully funded", "Funded / stipend", "Scholarship"])
    max_results = st.slider("Number of results", 5, 30, 15)
    exclude_municipal = st.checkbox(
        "Exclude Municipal Officer/local-government jobs in Pakistan",
        value=True,
    )
    custom_keywords = st.text_input(
        "Extra keywords",
        placeholder="e.g. GIS, Smart Cities, AI, transportation",
    )
    search_button = st.button("🚀 Search opportunities", use_container_width=True, type="primary")

tabs = st.tabs(["🔎 Opportunities", "📄 Tailored CV", "✉️ Cover Letter", "👤 My Profile", "⭐ Saved"])

if search_button:
    with st.spinner("Searching and analyzing opportunities..."):
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
        )
        st.session_state.results = results
        st.session_state.selected = None

with tabs[0]:
    st.subheader("Matching opportunities")
    results = st.session_state.results

    if not results:
        st.info("Set your filters in the sidebar and click **Search opportunities**.")
    else:
        st.success(f"Found {len(results)} analyzed opportunities.")
        for i, item in enumerate(results):
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"### {item.get('title', 'Untitled opportunity')}")
                    st.write(
                        f"**Organization:** {item.get('organization', 'Not stated')}  \n"
                        f"**Location:** {item.get('location', 'Not stated')}  \n"
                        f"**Type:** {item.get('type', 'Opportunity')}  \n"
                        f"**Funding:** {item.get('funding', 'Not stated')}"
                    )
                with c2:
                    st.metric("Match", f"{item.get('match_score', 0)}%")

                st.write(item.get("summary", ""))
                if item.get("match_reasons"):
                    st.markdown("**Why it matches:**")
                    for reason in item["match_reasons"]:
                        st.write(f"• {reason}")

                if item.get("deadline"):
                    st.write(f"**Deadline:** {item['deadline']}")

                if item.get("url"):
                    st.link_button("Open opportunity", item["url"])

                b1, b2, b3 = st.columns(3)
                if b1.button("📄 Tailor CV", key=f"cv_{i}"):
                    st.session_state.selected = item
                    with st.spinner("Generating tailored CV..."):
                        st.session_state.cv_text = build_tailored_cv(profile, item)
                    st.toast("Tailored CV generated.")

                if b2.button("✉️ Cover letter", key=f"cl_{i}"):
                    st.session_state.selected = item
                    with st.spinner("Generating cover letter..."):
                        st.session_state.cover_letter = build_cover_letter(profile, item)
                    st.toast("Cover letter generated.")

                if b3.button("⭐ Save", key=f"save_{i}"):
                    if not any(x.get("url") == item.get("url") for x in saved):
                        saved.append(item)
                        save_json(SAVED_FILE, saved)
                        st.toast("Saved.")
                    else:
                        st.info("Already saved.")

with tabs[1]:
    st.subheader("Tailored CV")
    if st.session_state.cv_text:
        st.text_area("CV content", st.session_state.cv_text, height=550)
        st.download_button(
            "⬇️ Download CV as TXT",
            st.session_state.cv_text,
            file_name="tailored_cv.txt",
            mime="text/plain",
        )
    else:
        st.info("Select an opportunity and click **Tailor CV**.")

with tabs[2]:
    st.subheader("Cover Letter")
    if st.session_state.cover_letter:
        st.text_area("Cover letter", st.session_state.cover_letter, height=500)
        st.download_button(
            "⬇️ Download cover letter",
            st.session_state.cover_letter,
            file_name="cover_letter.txt",
            mime="text/plain",
        )
    else:
        st.info("Select an opportunity and click **Cover letter**.")

with tabs[3]:
    st.subheader("Your career profile")
    st.json(profile)
    st.caption("Edit data/profile.json in GitHub to permanently update your profile.")

with tabs[4]:
    st.subheader("Saved opportunities")
    if not saved:
        st.info("No saved opportunities yet.")
    else:
        for item in saved:
            with st.container(border=True):
                st.markdown(f"### {item.get('title', 'Untitled')}")
                st.write(
                    f"{item.get('organization', '')} • "
                    f"{item.get('location', '')} • "
                    f"Match: {item.get('match_score', 0)}%"
                )
                if item.get("url"):
                    st.link_button("Open", item["url"])

st.divider()
st.caption("Khawar AI Career Assistant V1 • Personal career research tool")
