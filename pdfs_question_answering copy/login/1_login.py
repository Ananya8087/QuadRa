import streamlit as st
import subprocess

# Initialize a dictionary to store user credentials (username: password)
user_credentials = {
    "user1": "password1",
    "user2": "password2"
}

# Create a session_state variable to track user login state
if "user_logged_in" not in st.session_state:
    st.session_state["user_logged_in"] = False

# Apply custom CSS to position the login page on the top right
st.markdown(
    """
    <style>
    .login-container {
        position: fixed;
        top: 10px;
        right: 10px;
        padding: 10px;
        background-color: white;
        border: 1px solid #ccc;
        border-radius: 5px;
        z-index: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Define the main content
def main_content():
    #st.title("Main Content")
    st.write("Page is loading")

# Create a container for the login form
if not st.session_state["user_logged_in"]:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in user_credentials and user_credentials[username] == password:
            st.session_state["user_logged_in"] = True
            st.success("Login successful!")
            subprocess.Popen(["streamlit", "run", "/Users/ananya/Desktop/pdfs_question_answering/1_Summarize.py"])  # Run app_3.py
        else:
            st.warning("Incorrect username or password. Please try again.")

# Main application logic
if st.session_state["user_logged_in"]:
    main_content()
