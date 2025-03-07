import streamlit as st
from services.auth import authenticate_user
from ui.common import display_header

def display_login_page():
    """Display the login page"""
    display_header("Quiz Generator System", "Lecturer Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            user = authenticate_user(username, password)
            if user and user['role'] == 'lecturer':
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.page = 'menu'
                st.rerun()
            else:
                st.error("Invalid credentials or you do not have lecturer privileges.")