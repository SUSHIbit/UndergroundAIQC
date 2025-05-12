import streamlit as st

def validate_rubrics(rubrics):
    """Validate tournament rubrics
    
    Args:
        rubrics (list): List of rubric dictionaries with title and score_weight
        
    Returns:
        tuple: (is_valid, message, filtered_rubrics)
    """
    # Filter out empty rubrics
    filtered_rubrics = []
    for rubric in rubrics:
        if rubric["title"].strip() and rubric["score_weight"] > 0:
            filtered_rubrics.append(rubric)
    
    # Check if we have at least 3 valid rubrics
    if len(filtered_rubrics) < 3:
        return False, f"You must define at least 3 rubric items. Currently defined: {len(filtered_rubrics)}", filtered_rubrics
    
    # Check if weights sum to 100
    total_weight = sum(rubric['score_weight'] for rubric in filtered_rubrics)
    if total_weight != 100:
        return False, f"The total weight of rubrics must be exactly 100%. Current total: {total_weight}%", filtered_rubrics
    
    return True, "Rubrics are valid.", filtered_rubrics

def generate_default_rubrics(tournament_type):
    """Generate default rubrics based on tournament type
    
    Args:
        tournament_type (str): Type of tournament
        
    Returns:
        list: List of default rubric dictionaries
    """
    if tournament_type == "web_design":
        return [
            {"title": "Visual Design", "score_weight": 30},
            {"title": "User Experience", "score_weight": 40},
            {"title": "Technical Implementation", "score_weight": 30}
        ]
    elif tournament_type == "hackathon":
        return [
            {"title": "Innovation", "score_weight": 30},
            {"title": "Technical Complexity", "score_weight": 40},
            {"title": "Functionality", "score_weight": 30}
        ]
    elif tournament_type == "coding_competition":
        return [
            {"title": "Code Quality", "score_weight": 35},
            {"title": "Efficiency", "score_weight": 35},
            {"title": "Problem Solving", "score_weight": 30}
        ]
    elif tournament_type == "mobile":
        return [
            {"title": "User Interface", "score_weight": 30},
            {"title": "App Functionality", "score_weight": 40},
            {"title": "Innovation", "score_weight": 30}
        ]
    else:
        # Default rubrics for other tournament types
        return [
            {"title": "Strategy", "score_weight": 40},
            {"title": "Execution", "score_weight": 30},
            {"title": "Creativity", "score_weight": 30}
        ]

def create_tournament_rubrics_ui(rubrics):
    """Create UI for editing tournament rubrics
    
    Args:
        rubrics (list): List of rubric dictionaries
        
    Returns:
        list: Updated list of rubrics
    """
    st.subheader("Rubrics")
    st.info("Define at least 3 rubric items. The total weight must equal 100.")
    
    # Display the current total weight
    total_weight = sum(rubric['score_weight'] for rubric in rubrics if rubric['score_weight'] > 0)
    
    if total_weight != 100:
        st.warning(f"Current total weight: {total_weight}. Weights must sum to 100.")
    else:
        st.success(f"Current total weight: {total_weight}")
    
    # Create rubrics UI with at least 3 rubrics
    updated_rubrics = []
    
    for i in range(max(3, len(rubrics))):
        # Ensure we have enough rubrics
        if i >= len(rubrics):
            current_rubric = {"title": "", "score_weight": 0}
        else:
            current_rubric = rubrics[i].copy()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            current_rubric["title"] = st.text_input(
                f"Rubric #{i+1} Title",
                value=current_rubric["title"],
                key=f"rubric_title_{i}"
            )
        
        with col2:
            current_rubric["score_weight"] = st.number_input(
                f"Weight (%)",
                min_value=0,
                max_value=100,
                value=current_rubric["score_weight"],
                key=f"rubric_weight_{i}"
            )
        
        updated_rubrics.append(current_rubric)
    
    # Add button to add more rubrics
    if st.checkbox("Add another rubric item"):
        updated_rubrics.append({"title": "", "score_weight": 0})
    
    return updated_rubrics