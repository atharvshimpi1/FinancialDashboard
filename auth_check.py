import streamlit as st
import pyrebase

# Firebase configuration
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


def check_authentication():
    """
    Checks if user is authenticated and redirects to login if not.
    Returns the user object if authenticated.
    """
    # Check if authentication state exists
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # Check if user exists in session state
    if 'user' not in st.session_state:
        st.session_state['user'] = None

    # If not authenticated, redirect to login
    if not st.session_state['authenticated']:
        st.switch_page("Account.py")
        st.stop()

    return st.session_state['user']


def get_user_data():
    """
    Returns the current user's data from session state.
    """
    return st.session_state.get('user', None)


def logout():
    """
    Logs out the current user and clears session state.
    """
    st.session_state['authenticated'] = False
    st.session_state['user'] = None
    st.switch_page("Account.py")


# Optional: Function to check if token is expired and refresh if needed
def check_token():
    """
    Checks if the current user's token is valid and refreshes if needed.
    Returns True if token is valid, False otherwise.
    """
    if 'user' in st.session_state and st.session_state['user']:
        try:
            # Get user's ID token
            user = st.session_state['user']
            auth.refresh(user['refreshToken'])
            return True
        except Exception as e:
            st.session_state['authenticated'] = False
            st.session_state['user'] = None
            return False
    return False