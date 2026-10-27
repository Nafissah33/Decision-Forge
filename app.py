import streamlit as st

st.title("🧠 Decision-Forge")
st.write("Welcome to our COSC 208 Discrete Structures Project!")

st.header("Choose an Application")

if st.button("🚌 Commute Assistant"):
    st.success("Commute Assistant is working!")

if st.button("🔐 Login System"):
    st.success("Login System is working!")
