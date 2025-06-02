import streamlit as st
from datetime import datetime, timedelta
import random
from ui.common import display_header, display_success_message
from database.tournament_db import save_tournament, get_judges
from services.tournament_service import generate_tournament_with_openai, generate_web_design_tournament, generate_creative_prompt
from services.tournament_helpers import validate_rubrics, generate_default_rubrics, generate_detailed_judging_criteria_text

def handle_back_to_menu():
    """Handle back to menu button click"""
    st.session_state.page = 'menu'
    st.session_state.tournament_data = None
    st.session_state.tournament_type = None
    st.session_state.last_tournament_prompt = None
    st.session_state.rubrics = [
        {"title": "", "score_weight": 0},
        {"title": "", "score_weight": 0},
        {"title": "", "score_weight": 0}
    ]
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

def update_judging_criteria_from_rubrics():
    """Update judging criteria in tournament_data based on current rubrics"""
    if 'rubrics' in st.session_state and st.session_state.rubrics:
        # Always generate criteria from current rubrics
        judging_criteria_text = generate_detailed_judging_criteria_text(st.session_state.rubrics)
        
        if judging_criteria_text:
            # Always update the judging criteria to match rubrics
            if 'tournament_data' in st.session_state and st.session_state.tournament_data:
                st.session_state.tournament_data["judging_criteria"] = judging_criteria_text
            
            # Also update the form field if it exists
            if 'tournament_judging_criteria' in st.session_state:
                st.session_state['tournament_judging_criteria'] = judging_criteria_text

def display_tournament_page():
    """Display the tournament creation page"""
    display_header("Create Tournament", "Design a competition for students")
    
    # Display information about Bloom's Taxonomy level used for Tournaments
    st.info("🚀 **Bloom's Taxonomy Level: Create**  \nThis tournament will promote activities focusing on designing, constructing, planning, producing, and inventing new solutions and approaches.")
    
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
        
    if 'rubrics' not in st.session_state:
        # Initialize with three empty rubrics
        st.session_state.rubrics = [
            {"title": "", "score_weight": 0},
            {"title": "", "score_weight": 0},
            {"title": "", "score_weight": 0}
        ]
    
    # Tournament type selection
    if not st.session_state.tournament_type:
        st.subheader("Select Tournament Type")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("Web Design", use_container_width=True):
                st.session_state.tournament_type = "web_design"
                # Initialize rubrics with default values
                st.session_state.rubrics = generate_default_rubrics("web_design")
                update_judging_criteria_from_rubrics()
                st.rerun()
                
        with col2:
            if st.button("Coup d'État", use_container_width=True):
                st.session_state.tournament_type = "coup_detat"
                st.session_state.rubrics = generate_default_rubrics("coup_detat")
                update_judging_criteria_from_rubrics()
                st.rerun()
                
        with col3:
            if st.button("Hackathon", use_container_width=True):
                st.session_state.tournament_type = "hackathon"
                st.session_state.rubrics = generate_default_rubrics("hackathon")
                update_judging_criteria_from_rubrics()
                st.rerun()
                
        with col4:
            if st.button("Coding Competition", use_container_width=True):
                st.session_state.tournament_type = "coding_competition"
                st.session_state.rubrics = generate_default_rubrics("coding_competition")
                update_judging_criteria_from_rubrics()
                st.rerun()
                
        with col5:
            if st.button("Mobile", use_container_width=True):
                st.session_state.tournament_type = "mobile"
                st.session_state.rubrics = generate_default_rubrics("mobile")
                update_judging_criteria_from_rubrics()
                st.rerun()
    
    # If a tournament type is selected, show the specific options
    elif st.session_state.tournament_type and not st.session_state.tournament_saved:
        st.subheader(f"{st.session_state.tournament_type.replace('_', ' ').title()} Tournament")
        
        # Options for creating a tournament
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Create My Own Tournament", key="create_own", use_container_width=True):
                # Initialize empty tournament data with the selected type
                st.session_state.tournament_data = {"type": st.session_state.tournament_type, "title": "", "description": "", "judging_criteria": ""}
                st.session_state.show_ai_input = False
                # Initialize judging criteria with detailed rubrics
                update_judging_criteria_from_rubrics()
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
                        if not tournament_description.strip():
                            st.error("Please enter a tournament description.")
                        else:
                            with st.spinner("Generating tournament data with AI..."):
                                # Save the prompt for potential regeneration
                                st.session_state.last_tournament_prompt = tournament_description
                                
                                # Pass the tournament type to the generator function
                                tournament_data = generate_tournament_with_openai(
                                    tournament_description, 
                                    st.session_state.tournament_type
                                )
                                st.session_state.tournament_data = tournament_data
                                
                                # Initialize rubrics with default values based on tournament type
                                st.session_state.rubrics = generate_default_rubrics(st.session_state.tournament_type)
                                
                                # Update judging criteria from rubrics
                                update_judging_criteria_from_rubrics()
                                
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
            st.session_state.rubrics = [
                {"title": "", "score_weight": 0},
                {"title": "", "score_weight": 0},
                {"title": "", "score_weight": 0}
            ]
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
                    # Update judging criteria from rubrics
                    update_judging_criteria_from_rubrics()
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
                    # Update judging criteria from rubrics
                    update_judging_criteria_from_rubrics()
                    st.rerun()
        
        # Get available judges
        available_judges = get_judges()
        
        if not available_judges:
            st.warning("No users with the judge flag are available. Please add users with the judge flag before creating tournaments.")
        
        # Handle rubric actions outside the form
        if st.button("+ Add Rubric Item", key="add_rubric_outside_form"):
            st.session_state.rubrics.append({"title": "", "score_weight": 0})
            # Update judging criteria when rubrics change
            update_judging_criteria_from_rubrics()
            st.rerun()
        
        # Get tournament data from session state
        tournament_data = st.session_state.tournament_data
        
        st.subheader("Tournament Details")
        st.info("💾 Your edits are automatically saved as you type. Click 'Save Tournament' to submit to database.")
        
        # Tournament type display
        st.markdown(f"**Tournament Type:** {st.session_state.tournament_type.replace('_', ' ').title()}")
        
        # Initialize form data in session state if not present
        form_fields = [
            'tournament_title', 'tournament_description', 'tournament_location', 
            'tournament_eligibility', 'tournament_rank', 'tournament_team_size',
            'tournament_rules', 'tournament_judging_criteria', 'tournament_project_submission'
        ]
        
        for field in form_fields:
            if field not in st.session_state:
                if field == 'tournament_title':
                    st.session_state[field] = tournament_data.get("title", "")
                elif field == 'tournament_description':
                    st.session_state[field] = tournament_data.get("description", "")
                elif field == 'tournament_location':
                    st.session_state[field] = tournament_data.get("location", "")
                elif field == 'tournament_eligibility':
                    st.session_state[field] = tournament_data.get("eligibility", "")
                elif field == 'tournament_rank':
                    rank_options = ["Unranked", "Bronze", "Silver", "Gold", "Master", "Grand Master", "One Above All"]
                    st.session_state[field] = tournament_data.get("minimum_rank", "Bronze") if tournament_data.get("minimum_rank") in rank_options else "Bronze"
                elif field == 'tournament_team_size':
                    st.session_state[field] = parse_team_size(tournament_data.get("team_size", 2))
                elif field == 'tournament_rules':
                    st.session_state[field] = tournament_data.get("rules", "")
                elif field == 'tournament_judging_criteria':
                    st.session_state[field] = tournament_data.get("judging_criteria", "")
                elif field == 'tournament_project_submission':
                    st.session_state[field] = tournament_data.get("project_submission", "")
        
        # Initialize date/time fields in session state if not present
        if 'tournament_date' not in st.session_state:
            date_default = datetime.now() + timedelta(days=30)
            date_str = tournament_data.get("date_time", date_default.strftime("%Y-%m-%d %H:%M:%S"))
            try:
                if isinstance(date_str, str):
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                else:
                    date_obj = date_default
            except:
                date_obj = date_default
            st.session_state['tournament_date'] = date_obj.date()
        
        if 'tournament_time' not in st.session_state:
            st.session_state['tournament_time'] = datetime.strptime("14:00:00", "%H:%M:%S").time()
        
        if 'tournament_deadline_date' not in st.session_state:
            deadline_default = datetime.now() + timedelta(days=25)
            deadline_str = tournament_data.get("deadline", deadline_default.strftime("%Y-%m-%d %H:%M:%S"))
            try:
                if isinstance(deadline_str, str):
                    deadline_obj = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
                else:
                    deadline_obj = deadline_default
            except:
                deadline_obj = deadline_default
            st.session_state['tournament_deadline_date'] = deadline_obj.date()
        
        if 'tournament_deadline_time' not in st.session_state:
            st.session_state['tournament_deadline_time'] = datetime.strptime("23:59:59", "%H:%M:%S").time()
        
        if 'tournament_judging_date' not in st.session_state:
            judging_default = datetime.now() + timedelta(days=26)
            judging_date_str = tournament_data.get("judging_date", judging_default.strftime("%Y-%m-%d %H:%M:%S"))
            try:
                if isinstance(judging_date_str, str):
                    judging_date_obj = datetime.strptime(judging_date_str, "%Y-%m-%d %H:%M:%S")
                else:
                    judging_date_obj = judging_default
            except:
                judging_date_obj = judging_default
            st.session_state['tournament_judging_date'] = judging_date_obj.date()
        
        if 'tournament_judging_time' not in st.session_state:
            st.session_state['tournament_judging_time'] = datetime.strptime("10:00:00", "%H:%M:%S").time()
        
        # Basic details without on_change callbacks
        title = st.text_input("Title", key="tournament_title")
        description = st.text_area("Description", key="tournament_description")
        
        col1, col2 = st.columns(2)
        with col1:
            date_time = st.date_input("Date", key="tournament_date")
            time = st.time_input("Time", key="tournament_time")
            
        with col2:
            location = st.text_input("Location", key="tournament_location")
            eligibility = st.text_area("Eligibility", key="tournament_eligibility")
            
            rank_options = ["Unranked", "Bronze", "Silver", "Gold", "Master", "Grand Master", "One Above All"]
            minimum_rank = st.selectbox("Minimum Rank", rank_options, key="tournament_rank")
            
            team_size = st.number_input("Team Size", min_value=1, max_value=5, key="tournament_team_size")
        
        # Deadline
        deadline_date = st.date_input("Submission Deadline Date", key="tournament_deadline_date")
        deadline_time = st.time_input("Submission Deadline Time", key="tournament_deadline_time")
        
        # Judging Date
        judging_date = st.date_input("Judging Date", key="tournament_judging_date", help="Date when judging will begin. Must be on or after the submission deadline.")
        judging_time = st.time_input("Judging Time", key="tournament_judging_time")
        
        # Rules field
        rules = st.text_area("Rules", key="tournament_rules")
        
        # Rubrics Section
        st.subheader("Rubrics")
        st.info("Define at least 3 rubric items. The total weight must equal 100. Detailed explanations will be automatically generated for common rubric items.")
        
        # Display the current total weight
        valid_rubrics = [r for r in st.session_state.rubrics if r["title"].strip() and r["score_weight"] > 0]
        total_weight = sum(rubric['score_weight'] for rubric in valid_rubrics)
        
        # Create a status indicator for the total weight
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write("##### Rubric Items")
        with col2:
            if total_weight != 100:
                st.warning(f"Current total weight: {total_weight}%. Must equal 100%.")
            else:
                st.success(f"Current total weight: {total_weight}%")
        
        # Create rubrics UI with at least 3 rubrics
        updated_rubrics = []
        remove_indices = []
        
        for i, rubric in enumerate(st.session_state.rubrics):
            col1, col2, col3 = st.columns([3, 1, 0.5])
            
            with col1:
                title_key = f"rubric_title_{i}"
                if title_key not in st.session_state:
                    st.session_state[title_key] = rubric.get("title", "")
                title = st.text_input(f"Rubric #{i+1} Title", key=title_key)
            
            with col2:
                weight_key = f"rubric_weight_{i}"
                if weight_key not in st.session_state:
                    st.session_state[weight_key] = rubric.get("score_weight", 0)
                weight = st.number_input(f"Weight (%)", min_value=0, max_value=100, key=weight_key)
                
            with col3:
                # For rubrics beyond the minimum 3, show a checkbox for removal
                if len(st.session_state.rubrics) > 3 and i >= 3:
                    if st.checkbox("🗑️", key=f"remove_rubric_{i}"):
                        remove_indices.append(i)
                else:
                    st.write("")  # Empty space to maintain alignment
            
            updated_rubrics.append({
                "title": title,
                "score_weight": weight
            })
        
        # Update rubrics in session state (filtered to remove any marked for deletion)
        if remove_indices:
            new_rubrics = []
            for i, rubric in enumerate(updated_rubrics):
                if i not in remove_indices:
                    new_rubrics.append(rubric)
            st.session_state.rubrics = new_rubrics
            # Update judging criteria when rubrics change
            update_judging_criteria_from_rubrics()
            st.rerun()
        else:
            # Check if rubrics have changed
            old_rubrics = st.session_state.rubrics
            rubrics_changed = False
            
            if len(old_rubrics) != len(updated_rubrics):
                rubrics_changed = True
            else:
                for i, (old, new) in enumerate(zip(old_rubrics, updated_rubrics)):
                    if old.get("title", "") != new.get("title", "") or old.get("score_weight", 0) != new.get("score_weight", 0):
                        rubrics_changed = True
                        break
            
            # Update rubrics in session state
            st.session_state.rubrics = updated_rubrics
            
            # Update judging criteria if rubrics changed
            if rubrics_changed:
                update_judging_criteria_from_rubrics()
        
        # Judging criteria text area - now automatically populated from rubrics
        if 'tournament_judging_criteria' not in st.session_state:
            # Initialize with rubric-based criteria
            update_judging_criteria_from_rubrics()
        
        judging_criteria = st.text_area(
            "Judging Criteria", 
            height=300,
            key="tournament_judging_criteria",
            help="These criteria are automatically generated from your rubric items above. You can edit them if needed."
        )
        
        # Project submission requirements
        project_submission = st.text_area("Project Submission Requirements", key="tournament_project_submission")
        
        # Judge selection
        st.subheader("Select Judges")
        
        if available_judges:
            # Initialize selected judges in session state
            if 'selected_judges' not in st.session_state:
                st.session_state['selected_judges'] = []
            
            selected_judges = []
            st.write("Select judges for this tournament:")
            for judge in available_judges:
                judge_key = f"judge_{judge['id']}"
                if judge_key not in st.session_state:
                    st.session_state[judge_key] = False
                
                if st.checkbox(f"{judge['name']} ({judge['username']})", key=judge_key):
                    selected_judges.append(judge['id'])
            
            st.session_state['selected_judges'] = selected_judges
            
            if not selected_judges:
                st.warning("Please select at least one judge.")
        else:
            st.error("No judges available. Please add users with the judge flag first.")
            selected_judges = []
        
        # Final Submit Button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("💾 Save Tournament to Database", key="save_tournament_final", use_container_width=True, type="primary"):
                # Get final values from session state
                final_title = st.session_state.get("tournament_title", "")
                final_description = st.session_state.get("tournament_description", "")
                final_location = st.session_state.get("tournament_location", "")
                final_eligibility = st.session_state.get("tournament_eligibility", "")
                final_minimum_rank = st.session_state.get("tournament_rank", "Bronze")
                final_team_size = st.session_state.get("tournament_team_size", 2)
                final_rules = st.session_state.get("tournament_rules", "")
                final_judging_criteria = st.session_state.get("tournament_judging_criteria", "")
                final_project_submission = st.session_state.get("tournament_project_submission", "")
                final_selected_judges = st.session_state.get("selected_judges", [])
                
                # Construct datetime strings from separate date and time inputs
                final_date_time = datetime.combine(
                    st.session_state.get("tournament_date", datetime.now().date()),
                    st.session_state.get("tournament_time", datetime.strptime("14:00:00", "%H:%M:%S").time())
                ).strftime("%Y-%m-%d %H:%M:%S")
                
                final_deadline = datetime.combine(
                    st.session_state.get("tournament_deadline_date", datetime.now().date()),
                    st.session_state.get("tournament_deadline_time", datetime.strptime("23:59:59", "%H:%M:%S").time())
                ).strftime("%Y-%m-%d %H:%M:%S")
                
                final_judging_date = datetime.combine(
                    st.session_state.get("tournament_judging_date", datetime.now().date()),
                    st.session_state.get("tournament_judging_time", datetime.strptime("10:00:00", "%H:%M:%S").time())
                ).strftime("%Y-%m-%d %H:%M:%S")
                
                # Validate form
                if not final_title or not final_description:
                    st.error("Please fill in all required fields.")
                elif not final_selected_judges:
                    st.error("Please select at least one judge.")
                elif datetime.strptime(final_judging_date, "%Y-%m-%d %H:%M:%S").date() < datetime.strptime(final_deadline, "%Y-%m-%d %H:%M:%S").date():
                    st.error("Judging date must be on or after the submission deadline.")
                else:
                    # Validate rubrics
                    is_valid, message, filtered_rubrics = validate_rubrics(st.session_state.rubrics)
                    
                    if not is_valid:
                        st.error(message)
                    else:
                        # Save tournament to database
                        success = save_tournament(
                            st.session_state.user['id'],
                            final_title,
                            final_description,
                            final_date_time,
                            final_location,
                            final_eligibility,
                            final_minimum_rank,
                            final_team_size,
                            final_deadline,
                            final_rules,
                            final_judging_criteria,
                            final_project_submission,
                            final_selected_judges,
                            filtered_rubrics,
                            tournament_type=st.session_state.tournament_type,
                            judging_date=final_judging_date
                        )
                        
                        if success:
                            # Clear all tournament-related session state
                            keys_to_clear = [
                                'tournament_data', 'tournament_title', 'tournament_description',
                                'tournament_location', 'tournament_eligibility', 'tournament_rank',
                                'tournament_team_size', 'tournament_date', 'tournament_time',
                                'tournament_deadline_date', 'tournament_deadline_time',
                                'tournament_judging_date', 'tournament_judging_time',
                                'tournament_rules', 'tournament_judging_criteria',
                                'tournament_project_submission', 'selected_judges'
                            ]
                            
                            for key in keys_to_clear:
                                if key in st.session_state:
                                    del st.session_state[key]
                            
                            # Clear judge checkboxes
                            for judge in available_judges:
                                judge_key = f"judge_{judge['id']}"
                                if judge_key in st.session_state:
                                    del st.session_state[judge_key]
                            
                            # Clear rubric fields
                            for i in range(10):  # Clear up to 10 rubric fields
                                for field_type in ['title', 'weight']:
                                    field_key = f"rubric_{field_type}_{i}"
                                    if field_key in st.session_state:
                                        del st.session_state[field_key]
                            
                            st.session_state.tournament_saved = True
                            st.session_state.rubrics = [
                                {"title": "", "score_weight": 0},
                                {"title": "", "score_weight": 0},
                                {"title": "", "score_weight": 0}
                            ]
                            st.rerun()
    
    # Back button - always show this
    if st.button("Back to Menu", key="back_button"):
        handle_back_to_menu()