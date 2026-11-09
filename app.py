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
    </style>""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    home_background()
    st.title("🧠 Decision-Forge")
    st.write("Welcome to our COSC 208 Discrete Structures Project!")
    st.header("Choose an Application")
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
