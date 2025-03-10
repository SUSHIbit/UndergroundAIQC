import streamlit as st
from ui.common import display_header, display_card
from database.quiz_db import get_next_set_number
from ui.tournament_page import display_tournament_page

def handle_create_quiz():
    """Handle create quiz button click"""
    st.session_state.page = 'quiz'
    st.session_state.set_number = get_next_set_number()
    st.rerun()

def handle_create_challenge():
    """Handle create challenge button click"""
    st.session_state.page = 'challenge'
    st.session_state.set_number = get_next_set_number()
    st.rerun()
    
# Add this function
def handle_create_tournament():
    """Handle create tournament button click"""
    st.session_state.page = 'tournament'
    st.rerun()


def handle_logout():
    """Handle logout button click"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.page = 'login'
    st.rerun()

def display_menu_page():
    """Display the menu page"""
    display_header("Quiz Generator System", f"Welcome, {st.session_state.user['name']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_card(
            "Create Quiz",
            "Generate quiz questions from PowerPoint slides.",
            "Create Quiz",
            "create_quiz",
            handle_create_quiz
        )
    
    with col2:
        display_card(
            "Create Challenge",
            "Create harder questions based on prerequisite quizzes.",
            "Create Challenge",
            "create_challenge",
            handle_create_challenge
        )
    
    with col3:
        display_card(
            "Create Tournament",
            "Design competitions for students to showcase their skills.",
            "Create Tournament",
            "create_tournament",
            handle_create_tournament
        )
    
    if st.button("Logout"):
        handle_logout()