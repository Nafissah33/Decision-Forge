import base64
from pathlib import Path

import streamlit as st

from screens import commute_page
from screens import login_page

st.set_page_config(page_title="Decision-Forge", page_icon="🧠")

LOGO = Path(__file__).parent / "assets" / "wics_logo.jpg"


@st.cache_data
def _logo_b64():
    return base64.b64encode(LOGO.read_bytes()).decode()


def home_background():
    """WiCS logo behind the home page only (dimmed so the text stays readable)."""
    if not LOGO.exists():
        return
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: #000;
        background-image: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)),
                          url("data:image/jpeg;base64,{_logo_b64()}");
        background-size: contain;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stApp h1, .stApp h2, .stApp p {{ text-shadow: 0 2px 8px #000; }}
    .df-hero, .df-hero *, .stButton button p {{
        font-family: "Times New Roman", Times, serif !important;
    }}
    .df-hero {{ text-align: center; padding: 1.5rem 0 0.5rem; text-shadow: 0 2px 10px #000; }}
    .df-hero h1 {{ font-size: 3.4rem; font-weight: 700; color: #FFC72C; margin: 0; }}
    .df-hero .tag {{ font-size: 1.5rem; font-style: italic; color: #D9B8FF; margin: 0.3rem 0 1rem; }}
    .df-hero .sub {{ font-size: 1.15rem; color: #FFFFFF; margin: 0 0 1.2rem; }}
    .df-hero h2 {{ font-size: 1.8rem; color: #FFC72C; margin: 0; }}
    .stButton button p {{ font-size: 1.2rem; font-weight: 700; }}
    </style>""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    home_background()
    st.markdown("""
    <div class="df-hero">
      <h1>🧠 Decision-Forge</h1>
      <p class="tag">Think it through. Forge the decision.</p>
      <p class="sub">Logic you can see: truth tables, trees and graphs show exactly why
      every answer was chosen. Built for COSC 208 Discrete Structures.</p>
      <h2>✨ Pick your adventure ✨</h2>
    </div>""", unsafe_allow_html=True)
    if st.button("🚌 Commute Assistant"):
        st.session_state.page = "commute"
        st.rerun()
    if st.button("🔐 Login System"):
        st.session_state.page = "login"
        st.rerun()
else:
    if st.button("← Back to home"):
        st.session_state.page = "home"
        st.rerun()
    {"commute": commute_page, "login": login_page}[st.session_state.page].show()
