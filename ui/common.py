import streamlit as st

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #333;
        margin-bottom: 20px;
    }
    .card {
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
    }
    .success-msg {
        color: #28a745;
        font-weight: bold;
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def display_header(title, subtitle=None):
    """
    Display a header with optional subtitle
    
    Args:
        title (str): The main title to display
        subtitle (str, optional): The subtitle to display
    """
    st.markdown(f"<h1 class='main-header'>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<h2 class='sub-header'>{subtitle}</h2>", unsafe_allow_html=True)

def display_success_message(message):
    """
    Display a success message
    
    Args:
        message (str): The success message to display
    """
    st.markdown(f"<div class='success-msg'>{message}</div>", unsafe_allow_html=True)

def display_card(title, content, button_text=None, button_key=None, on_click=None):
    """
    Display a card with optional button
    
    Args:
        title (str): The card title
        content (str): The card content
        button_text (str, optional): The button text
        button_key (str, optional): The button key
        on_click (function, optional): The button click handler
    """
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p>{content}</p>", unsafe_allow_html=True)
    
    if button_text and button_key:
        if st.button(button_text, key=button_key) and on_click:
            on_click()
    
    st.markdown("</div>", unsafe_allow_html=True)