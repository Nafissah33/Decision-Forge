import streamlit as st

# Website title
st.title("Decision-Forge 🧠")

st.write("Welcome to our COSC 208 Discrete Structures Project!")

# Create two buttons
if st.button("🚌 Commute Assistant"):
    st.success("Welcome to the Commute Assistant!")
    st.write("This application will help Maya plan her commute.")

if st.button("🔐 Login System"):
    st.success("Welcome to the Login System!")
    st.write("This application will handle user login and logout.")
    
