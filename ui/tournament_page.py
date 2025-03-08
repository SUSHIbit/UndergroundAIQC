import streamlit as st
from datetime import datetime, timedelta
from ui.common import display_header, display_success_message
from database.tournament_db import save_tournament
from services.tournament_service import generate_tournament_with_openai, generate_web_design_tournament

def handle_back_to_menu():
    """Handle back to menu button click"""
    st.session_state.page = 'menu'
    st.session_state.tournament_data = None
    st.rerun()

def parse_team_size(team_size_value):
    """
    Parse the team size from different possible formats:
    - Integer
    - String with just a number
    - String with a range (e.g. "1-4 members per team")
    
    Returns an integer representing the team size or 2 as a default
    """
    if isinstance(team_size_value, int):
        return team_size_value
    
    if isinstance(team_size_value, str):
        # Try to parse as a simple integer
        try:
            return int(team_size_value)
        except ValueError:
            # Handle ranges like "1-4 members per team"
            import re
            matches = re.findall(r'\d+', team_size_value)
            if matches:
                # Take the first number in the string
                return int(matches[0])
    
    # Default value if parsing fails
    return 2

def display_tournament_page():
    """Display the tournament creation page"""
    display_header("Create Tournament", "Design a competition for students")
    
    # Initialize tournament data in session state if needed
    if 'tournament_data' not in st.session_state:
        st.session_state.tournament_data = None
    
    # Add a flag to track if a tournament was just saved
    if 'tournament_saved' not in st.session_state:
        st.session_state.tournament_saved = False
    
    # Container for AI generation options
    with st.container():
        st.subheader("Generate Tournament Data")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate with AI", key="generate_ai"):
                st.session_state.show_ai_input = True
        
        with col2:
            if st.button("Web Design Tournament", key="web_design"):
                # Generate web design tournament
                with st.spinner("Generating web design tournament..."):
                    tournament_data = generate_web_design_tournament()
                    st.session_state.tournament_data = tournament_data
    
    # Show AI input field if the button was clicked
    if st.session_state.get('show_ai_input', False):
        with st.expander("AI Generation", expanded=True):
            tournament_description = st.text_area(
                "Describe the tournament you want to create",
                "A web design competition for university students where they need to redesign a website for a cat-themed company."
            )
            
            if st.button("Generate", key="generate_with_description"):
                with st.spinner("Generating tournament data with AI..."):
                    tournament_data = generate_tournament_with_openai(tournament_description)
                    st.session_state.tournament_data = tournament_data
                    st.session_state.show_ai_input = False
    
    # Show success message and return button if tournament was just saved
    if st.session_state.tournament_saved:
        display_success_message("Tournament saved successfully!")
        if st.button("Return to Menu", key="return_after_save"):
            st.session_state.tournament_saved = False
            handle_back_to_menu()
    
    # Only display the form if a tournament wasn't just saved
    if not st.session_state.tournament_saved:
        # Form for tournament details
        with st.form("tournament_form"):
            # Get tournament data from session state or initialize empty values
            tournament_data = st.session_state.tournament_data or {}
            
            st.subheader("Tournament Details")
            
            # Basic details
            title = st.text_input("Title", value=tournament_data.get("title", ""))
            description = st.text_area("Description", value=tournament_data.get("description", ""))
            
            col1, col2 = st.columns(2)
            with col1:
                date_default = datetime.now() + timedelta(days=30)
                date_str = tournament_data.get("date_time", date_default.strftime("%Y-%m-%d %H:%M:%S"))
                try:
                    if isinstance(date_str, str):
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    else:
                        date_obj = date_default
                except:
                    date_obj = date_default
                    
                date_time = st.date_input("Date", value=date_obj)
                time = st.time_input("Time", value=datetime.strptime("14:00:00", "%H:%M:%S").time())
                
            with col2:
                location = st.text_input("Location", value=tournament_data.get("location", ""))
                
                # Eligibility
                eligibility = st.text_area("Eligibility", value=tournament_data.get("eligibility", ""))
                
                rank_options = ["Unranked", "Bronze", "Silver", "Gold", "Master", "Grand Master", "One Above All"]
                default_rank_index = rank_options.index(tournament_data.get("minimum_rank", "Bronze")) if tournament_data.get("minimum_rank") in rank_options else 1
                minimum_rank = st.selectbox("Minimum Rank", rank_options, index=default_rank_index)
                
                team_size = st.number_input("Team Size", min_value=1, max_value=5, 
                                           value=parse_team_size(tournament_data.get("team_size", 2)))
            
            # Deadline
            deadline_default = datetime.now() + timedelta(days=25)
            deadline_str = tournament_data.get("deadline", deadline_default.strftime("%Y-%m-%d %H:%M:%S"))
            try:
                if isinstance(deadline_str, str):
                    deadline_obj = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
                else:
                    deadline_obj = deadline_default
            except:
                deadline_obj = deadline_default
                
            deadline_date = st.date_input("Submission Deadline Date", value=deadline_obj)
            deadline_time = st.time_input("Submission Deadline Time", value=datetime.strptime("23:59:59", "%H:%M:%S").time())
            
            # Rules and criteria
            rules = st.text_area("Rules", value=tournament_data.get("rules", ""))
            judging_criteria = st.text_area("Judging Criteria", value=tournament_data.get("judging_criteria", ""))
            project_submission = st.text_area("Project Submission Requirements", value=tournament_data.get("project_submission", ""))
            
            # Judges
            st.subheader("Judges")
            
            judges_data = tournament_data.get("judges", [{"name": "", "role": ""}] * 4)
            if not isinstance(judges_data, list):
                judges_data = [{"name": "", "role": ""}] * 4
            
            # Ensure we have at least 4 judge slots
            while len(judges_data) < 4:
                judges_data.append({"name": "", "role": ""})
            
            judges = []
            for i in range(4):  # Allow 4 judges
                col1, col2 = st.columns([2, 3])
                with col1:
                    judge_name = st.text_input(f"Judge {i+1} Name", value=judges_data[i].get("name", ""), key=f"judge_{i}_name")
                with col2:
                    judge_role = st.text_input(f"Judge {i+1} Role", value=judges_data[i].get("role", ""), key=f"judge_{i}_role")
                
                if judge_name:  # Only add if name is provided
                    judges.append({"name": judge_name, "role": judge_role})
            
            submit_button = st.form_submit_button("Save Tournament")
            
            if submit_button:
                # Combine date and time
                date_time_combined = datetime.combine(date_time, time).strftime("%Y-%m-%d %H:%M:%S")
                deadline_combined = datetime.combine(deadline_date, deadline_time).strftime("%Y-%m-%d %H:%M:%S")
                
                # Validate form
                if not title or not description or not judges:
                    st.error("Please fill in all required fields and add at least one judge.")
                else:
                    # Save tournament to database
                    success = save_tournament(
                        st.session_state.user['id'],
                        title,
                        description,
                        date_time_combined,
                        location,
                        eligibility,
                        minimum_rank,
                        team_size,
                        deadline_combined,
                        rules,
                        judging_criteria,
                        project_submission,
                        judges
                    )
                    
                    if success:
                        st.session_state.tournament_data = None
                        st.session_state.tournament_saved = True
                        st.rerun()  # Rerun to show success message outside the form
    
    # Back button - outside the form
    if st.button("Back to Menu", key="back_button"):
        handle_back_to_menu()