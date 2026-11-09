import streamlit as st

from screens import commute_page
from screens import login_page

st.set_page_config(page_title="Decision-Forge", page_icon="🧠")

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
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
