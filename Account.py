import streamlit as st
import pyrebase
import time
import os

# Configure Firebase
firebaseConfig = {
    "apiKey": "AIzaSyCeEx-SAOs_zGfY-TXJq2zWYsoPZ-QO5po",
    "authDomain": "finacncebnpdashboard.firebaseapp.com",
    "databaseURL": "https://finacncebnpdashboard-default-rtdb.firebaseio.com",
    "projectId": "finacncebnpdashboard",
    "storageBucket": "finacncebnpdashboard.firebasestorage.app",
    "messagingSenderId": "358537377294",
    "appId": "1:358537377294:web:587571a115b7f9eb3e2e5f",
    "measurementId": "G-KY428G7Q3P"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

# Hide all streamlit pages in sidebar when not logged in
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.set_page_config(
        page_title="Login",
        page_icon="🔒",
        initial_sidebar_state="collapsed",
        layout="wide"
    )

    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .css-1rs6os {visibility: hidden;}
        .css-17ziqus {visibility: hidden;}
        .css-1lamwuk {visibility: hidden;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
else:
    st.set_page_config(
        page_title="Dashboard",
        page_icon="📊",
        layout="wide"
    )


def send_reset_email(email):
    try:
        auth.send_password_reset_email(email)
        st.success("Password reset email sent! Please check your inbox.")
        return True
    except Exception as e:
        st.error("Failed to send reset email. Please verify your email address.")
        return False


def forgot_password():
    st.subheader("Reset Password")
    reset_email = st.text_input("Enter your email address", key="reset_email")

    if st.button("Send Reset Link", key="reset_button"):
        if reset_email:
            send_reset_email(reset_email)
        else:
            st.warning("Please enter your email address")


def login_signup():
    st.title("Welcome to the Financial Dashboard 💰")

    # Create tabs for Login, Sign Up, and Forgot Password
    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Forgot Password"])

    # Login tab
    with tab1:
        st.header("Login")
        login_email = st.text_input("Email Address", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        col1, col2 = st.columns([1, 2])

        with col1:
            if st.button("Login", key="login_button"):
                if login_email and login_password:
                    try:
                        user = auth.sign_in_with_email_and_password(login_email, login_password)
                        st.session_state['authenticated'] = True
                        st.session_state['user'] = user
                        st.success("Login successful! Redirecting...")
                        time.sleep(1)
                        st.switch_page("pages/Home.py")
                    except Exception as e:
                        st.error("Login failed. Please check your credentials.")
                else:
                    st.warning("Please fill in all fields")

    # Sign Up tab
    with tab2:
        st.header("Create New Account")
        signup_email = st.text_input("Email Address", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

        if st.button("Sign Up", key="signup_button"):
            if signup_email and signup_password and confirm_password:
                if signup_password == confirm_password:
                    try:
                        user = auth.create_user_with_email_and_password(signup_email, signup_password)
                        st.success("Account created successfully!")
                        st.success("Please login with your new credentials")
                    except Exception as e:
                        st.error("Sign up failed.")
                else:
                    st.error("Passwords do not match")
            else:
                st.warning("Please fill in all fields")

    # Forgot Password tab
    with tab3:
        forgot_password()


def main():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        login_signup()
    else:
        st.switch_page("pages/Home.py")


if __name__ == "__main__":
    main()