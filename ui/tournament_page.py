import streamlit as st
from datetime import datetime, timedelta
import random
from ui.common import display_header, display_success_message
from database.tournament_db import save_tournament, get_judges
from services.tournament_service import generate_tournament_with_openai, generate_web_design_tournament

def handle_back_to_menu():
    """Handle back to menu button click"""
    st.session_state.page = 'menu'
    st.session_state.tournament_data = None
    st.session_state.tournament_type = None
    st.session_state.last_tournament_prompt = None
    st.rerun()

def generate_creative_prompt(tournament_type):
    """Generate a creative prompt for tournament generation
    
    Args:
        tournament_type (str): Type of tournament to generate a prompt for
        
    Returns:
        str: A creative prompt
    """
    # Creative themes for different tournament types
    web_design_themes = [
        "Generate a creative web design tournament about a luxury pet hotel needing a website to showcase their premium services and attract high-end clientele.",
        "Generate a creative web design tournament about a virtual reality arcade trying to build an immersive website that reflects their futuristic gaming experiences.",
        "Generate a creative web design tournament about a sustainable fashion brand needing a website that highlights their eco-friendly practices and unique designs.",
        "Generate a creative web design tournament about a historic bookstore with rare collections needing a website that balances classic aesthetics with modern functionality.",
        "Generate a creative web design tournament about a food delivery service specialized in international cuisines needing a website to showcase global flavors.",
        "Generate a creative web design tournament about a space tourism company needing a website to attract adventurous travelers for their upcoming orbital flights.",
        "Generate a creative web design tournament about a music festival needing a dynamic website to promote their lineup of artists and sell tickets.",
        "Generate a creative web design tournament about an underwater photography gallery needing a website that captures the beauty of marine life.",
        "Generate a creative web design tournament about a smart home technology company needing a website that demonstrates their innovative products.",
        "Generate a creative web design tournament about a community garden organization needing a website to attract volunteers and share gardening resources."
    ]
    
    hackathon_themes = [
        "Generate a 36-hour hackathon focused on creating solutions for disaster response and emergency management systems.",
        "Generate a 36-hour hackathon focused on developing educational technology for children with learning disabilities.",
        "Generate a 36-hour hackathon focused on creating financial technology solutions for underbanked communities.",
        "Generate a 36-hour hackathon focused on building sustainable smart city infrastructure and monitoring systems.",
        "Generate a 36-hour hackathon focused on developing mental health support applications and resources.",
        "Generate a 36-hour hackathon focused on creating accessibility tools for people with disabilities.",
        "Generate a 36-hour hackathon focused on developing AI-powered agriculture solutions for small farms.",
        "Generate a 36-hour hackathon focused on creating privacy-focused alternatives to mainstream tech products.",
        "Generate a 36-hour hackathon focused on developing telehealth solutions for rural communities.",
        "Generate a 36-hour hackathon focused on creating augmented reality applications for industrial training."
    ]
    
    mobile_themes = [
        "Generate a mobile app development competition focused on health monitoring and wellness tracking.",
        "Generate a mobile app development competition focused on location-based augmented reality games.",
        "Generate a mobile app development competition focused on personal finance management and financial literacy.",
        "Generate a mobile app development competition focused on language learning and cultural exchange.",
        "Generate a mobile app development competition focused on community volunteering and social impact.",
        "Generate a mobile app development competition focused on sustainable living and carbon footprint reduction.",
        "Generate a mobile app development competition focused on collaborative music creation and sharing.",
        "Generate a mobile app development competition focused on mental health support and mindfulness.",
        "Generate a mobile app development competition focused on accessible navigation for people with disabilities.",
        "Generate a mobile app development competition focused on local tourism and hidden gem discovery."
    ]
    
    coding_themes = [
        "Generate a competitive programming contest focused on algorithm optimization for renewable energy systems.",
        "Generate a competitive programming contest focused on machine learning challenges for medical diagnosis.",
        "Generate a competitive programming contest focused on natural language processing for multilingual communication.",
        "Generate a competitive programming contest focused on computer vision for wildlife conservation.",
        "Generate a competitive programming contest focused on blockchain solutions for supply chain transparency.",
        "Generate a competitive programming contest focused on quantum computing algorithm simulation.",
        "Generate a competitive programming contest focused on cybersecurity challenges and ethical hacking.",
        "Generate a competitive programming contest focused on data analysis for climate change research.",
        "Generate a competitive programming contest focused on game AI development and strategy optimization.",
        "Generate a competitive programming contest focused on robotics control systems and automation."
    ]
    
    # Select themes based on tournament type
    if tournament_type == "web_design":
        themes = web_design_themes
    elif tournament_type == "hackathon":
        themes = hackathon_themes
    elif tournament_type == "mobile":
        themes = mobile_themes
    elif tournament_type == "coding_competition":
        themes = coding_themes
    else:
        # For other types, use a mix of themes
        themes = random.sample(web_design_themes, 3) + random.sample(hackathon_themes, 3) + random.sample(mobile_themes, 2)
    
    # Return a random theme
    return random.choice(themes)

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
    
    # Initialize session state variables
    if 'tournament_data' not in st.session_state:
        st.session_state.tournament_data = None
    
    if 'tournament_saved' not in st.session_state:
        st.session_state.tournament_saved = False
        
    if 'tournament_type' not in st.session_state:
        st.session_state.tournament_type = None
        
    if 'show_ai_input' not in st.session_state:
        st.session_state.show_ai_input = False
        
    if 'last_tournament_prompt' not in st.session_state:
        st.session_state.last_tournament_prompt = None
    
    # Tournament type selection
    if not st.session_state.tournament_type:
        st.subheader("Select Tournament Type")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("Web Design", use_container_width=True):
                st.session_state.tournament_type = "web_design"
                st.rerun()
                
        with col2:
            if st.button("Coup d'État", use_container_width=True):
                st.session_state.tournament_type = "coup_detat"
                st.rerun()
                
        with col3:
            if st.button("Hackathon", use_container_width=True):
                st.session_state.tournament_type = "hackathon"
                st.rerun()
                
        with col4:
            if st.button("Coding Competition", use_container_width=True):
                st.session_state.tournament_type = "coding_competition"
                st.rerun()
                
        with col5:
            if st.button("Mobile", use_container_width=True):
                st.session_state.tournament_type = "mobile"
                st.rerun()
    
    # If a tournament type is selected, show the specific options
    elif st.session_state.tournament_type and not st.session_state.tournament_saved:
        st.subheader(f"{st.session_state.tournament_type.replace('_', ' ').title()} Tournament")
        
        # Options for creating a tournament
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Create My Own Tournament", key="create_own", use_container_width=True):
                # Initialize empty tournament data with the selected type
                st.session_state.tournament_data = {"type": st.session_state.tournament_type, "title": "", "description": ""}
                st.session_state.show_ai_input = False
                st.rerun()
        
        with col2:
            if st.button("Generate with AI", key="generate_ai", use_container_width=True):
                st.session_state.show_ai_input = True
                # Initialize with default prompt for the tournament type
                if st.session_state.last_tournament_prompt is None:
                    default_prompts = {
                        "web_design": "Generate a creative web design tournament about a cat café struggling to attract customers and needing a better online presence to showcase their cats and menu.",
                        "hackathon": "Generate a 36-hour hackathon focused on building a medication tracking application for a healthcare provider.",
                        "coup_detat": "Generate a strategic game tournament where players compete to take control of a fictional government.",
                        "coding_competition": "Generate a competitive programming contest with algorithmic challenges.",
                        "mobile": "Generate a mobile app development competition focused on educational technology."
                    }
                    st.session_state.last_tournament_prompt = default_prompts.get(st.session_state.tournament_type, "Describe your tournament here.")
                st.rerun()

        # Show AI input field if the button was clicked
        if st.session_state.show_ai_input:
            with st.expander("AI Tournament Generator", expanded=True):
                # Use the stored prompt if available, otherwise use default
                tournament_description = st.text_area(
                    "Describe the tournament you want to create",
                    value=st.session_state.last_tournament_prompt
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Generate Tournament", key="generate_with_description"):
                        with st.spinner("Generating tournament data with AI..."):
                            # Save the prompt for potential regeneration
                            st.session_state.last_tournament_prompt = tournament_description
                            
                            # Pass the tournament type to the generator function
                            tournament_data = generate_tournament_with_openai(
                                tournament_description, 
                                st.session_state.tournament_type
                            )
                            st.session_state.tournament_data = tournament_data
                            st.session_state.show_ai_input = False
                            st.rerun()
                
                with col2:
                    if st.button("Re-generate Prompt", key="regenerate_prompt"):
                        # Generate a new creative prompt
                        new_prompt = generate_creative_prompt(st.session_state.tournament_type)
                        st.session_state.last_tournament_prompt = new_prompt
                        st.rerun()
    
    # Show success message and return button if tournament was just saved
    if st.session_state.tournament_saved:
        display_success_message("Tournament saved successfully!")
        if st.button("Return to Menu", key="return_after_save"):
            st.session_state.tournament_saved = False
            st.session_state.tournament_type = None
            st.session_state.last_tournament_prompt = None
            handle_back_to_menu()
    
    # Only display the form if a tournament type was selected and we have tournament data
    if st.session_state.tournament_type and st.session_state.tournament_data and not st.session_state.tournament_saved:
        # Show regenerate buttons at the top of the form
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate New Variation", key="regenerate_tournament_top"):
                with st.spinner("Generating new tournament variation..."):
                    # Use the same prompt but generate a new tournament
                    tournament_data = generate_tournament_with_openai(
                        st.session_state.last_tournament_prompt, 
                        st.session_state.tournament_type
                    )
                    st.session_state.tournament_data = tournament_data
                    st.rerun()
        
        with col2:
            if st.button("Try Different Theme", key="regenerate_prompt_top"):
                with st.spinner("Generating a completely new theme..."):
                    # Generate a new creative prompt
                    new_prompt = generate_creative_prompt(st.session_state.tournament_type)
                    st.session_state.last_tournament_prompt = new_prompt
                    
                    # Generate a tournament with the new prompt
                    tournament_data = generate_tournament_with_openai(
                        new_prompt,
                        st.session_state.tournament_type
                    )
                    st.session_state.tournament_data = tournament_data
                    st.rerun()
        
        # Get available judges
        available_judges = get_judges()
        
        if not available_judges:
            st.warning("No users with 'judge' role are available. Please create some judge users before creating tournaments.")
            
        # Form for tournament details
        with st.form("tournament_form"):
            # Get tournament data from session state
            tournament_data = st.session_state.tournament_data
            
            st.subheader("Tournament Details")
            
            # Tournament type display
            st.markdown(f"**Tournament Type:** {st.session_state.tournament_type.replace('_', ' ').title()}")
            
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
            
            # Judge selection
            st.subheader("Select Judges")
            
            if available_judges:
                # Create multiple selection for judges
                judge_options = {j['id']: f"{j['name']} ({j['username']})" for j in available_judges}
                selected_judges = []
                
                st.write("Select judges for this tournament:")
                for judge in available_judges:
                    if st.checkbox(f"{judge['name']} ({judge['username']})", key=f"judge_{judge['id']}"):
                        selected_judges.append(judge['id'])
                
                if not selected_judges:
                    st.warning("Please select at least one judge.")
            else:
                st.error("No judges available. Please add users with judge role first.")
                selected_judges = []
            
            submit_button = st.form_submit_button("Save Tournament")
            
            if submit_button:
                # Combine date and time
                date_time_combined = datetime.combine(date_time, time).strftime("%Y-%m-%d %H:%M:%S")
                deadline_combined = datetime.combine(deadline_date, deadline_time).strftime("%Y-%m-%d %H:%M:%S")
                
                # Validate form
                if not title or not description:
                    st.error("Please fill in all required fields.")
                elif not selected_judges:
                    st.error("Please select at least one judge.")
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
                        selected_judges,
                        tournament_type=st.session_state.tournament_type  # Pass the tournament type explicitly
                    )
                    
                    if success:
                        st.session_state.tournament_data = None
                        st.session_state.tournament_saved = True
                        st.rerun()  # Rerun to show success message outside the form
    
    # Back button - always show this
    if st.button("Back to Menu", key="back_button"):
        handle_back_to_menu()