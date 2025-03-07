import streamlit as st
from dotenv import load_dotenv
import os

# Import UI components
from ui.common import apply_custom_css
from ui.login_page import display_login_page
from ui.menu_page import display_menu_page
from ui.quiz_page import display_quiz_page
from ui.challenge_page import display_challenge_page
from ui.tournament_page import display_tournament_page

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(page_title="Quiz Generator", layout="wide", page_icon="📚")

def main():
    """Main application function"""
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'set_number' not in st.session_state:
        st.session_state.set_number = None
    if 'tournament_data' not in st.session_state:
        st.session_state.tournament_data = None
    
    # Apply custom CSS
    apply_custom_css()
    
    # Route to the correct page based on session state
    if st.session_state.page == 'login':
        display_login_page()
    elif st.session_state.page == 'menu':
        display_menu_page()
    elif st.session_state.page == 'quiz':
        display_quiz_page()
    elif st.session_state.page == 'challenge':
        display_challenge_page()
    elif st.session_state.page == 'tournament':
        display_tournament_page()

if __name__ == "__main__":
    main()