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
            {"title": "Visual Design", "score_weight": 30, "description": "Aesthetics, color scheme, typography, and overall visual appeal."},
            {"title": "User Experience", "score_weight": 40, "description": "Navigation, information architecture, and ease of use."},
            {"title": "Technical Implementation", "score_weight": 30, "description": "Code quality, performance, and proper implementation."}
        ]
    elif tournament_type == "hackathon":
        return [
            {"title": "Innovation", "score_weight": 30, "description": "Originality and creativity of the solution."},
            {"title": "Technical Complexity", "score_weight": 40, "description": "Sophistication of implementation and use of technologies."},
            {"title": "Functionality", "score_weight": 30, "description": "How well the solution works as intended with minimal bugs."}
        ]
    elif tournament_type == "coding_competition":
        return [
            {"title": "Code Quality", "score_weight": 35, "description": "Clean, maintainable code that follows best practices."},
            {"title": "Efficiency", "score_weight": 35, "description": "Performance and optimization of algorithms and solutions."},
            {"title": "Problem Solving", "score_weight": 30, "description": "Approach to solving challenges and handling edge cases."}
        ]
    elif tournament_type == "mobile":
        return [
            {"title": "User Interface", "score_weight": 30, "description": "Visual design, layout, and responsiveness of the app."},
            {"title": "App Functionality", "score_weight": 40, "description": "Features, performance, and user experience of the app."},
            {"title": "Innovation", "score_weight": 30, "description": "Originality and creative approaches to solving problems."}
        ]
    else:
        # Default rubrics for other tournament types
        return [
            {"title": "Strategy", "score_weight": 40, "description": "Approach to solving the challenge and planning."},
            {"title": "Execution", "score_weight": 30, "description": "Implementation quality and attention to detail."},
            {"title": "Creativity", "score_weight": 30, "description": "Original ideas and innovative solutions."}
        ]

def generate_judging_criteria_text(rubrics):
    """Generate formatted judging criteria text from rubrics
    
    Args:
        rubrics (list): List of valid rubric dictionaries
    
    Returns:
        str: Formatted judging criteria text
    """
    # Filter out empty rubrics
    valid_rubrics = [r for r in rubrics if r["title"].strip() and r["score_weight"] > 0]
    
    if not valid_rubrics:
        return ""
    
    criteria_lines = []
    for i, rubric in enumerate(valid_rubrics, 1):
        description = rubric.get("description", "[Add specific criteria for this category]")
        criteria_lines.append(f"{i}. {rubric['title']} ({rubric['score_weight']}%): {description}")
    
    return "\n".join(criteria_lines)

def create_tournament_rubrics_ui(rubrics, add_rubric_clicked=False, remove_rubric_index=None):
    """Create UI for editing tournament rubrics
    
    Args:
        rubrics (list): List of rubric dictionaries
        add_rubric_clicked (bool): Whether the add rubric button was clicked
        remove_rubric_index (int, optional): Index of rubric to remove
        
    Returns:
        list: Updated list of rubrics, judging_criteria_text
    """
    st.subheader("Rubrics")
    st.info("Define at least 3 rubric items. The total weight must equal 100.")
    
    # Handle adding a new rubric if the button was clicked
    if add_rubric_clicked:
        rubrics.append({"title": "", "score_weight": 0, "description": ""})
    
    # Handle removing a rubric if requested and if we have more than 3
    if remove_rubric_index is not None and remove_rubric_index < len(rubrics) and len(rubrics) > 3:
        rubrics.pop(remove_rubric_index)
    
    # Display the current total weight
    valid_rubrics = [r for r in rubrics if r["title"].strip() and r["score_weight"] > 0]
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
    
    for i, rubric in enumerate(rubrics):
        col1, col2, col3 = st.columns([3, 1, 0.5])
        
        with col1:
            title = st.text_input(
                f"Rubric #{i+1} Title",
                value=rubric.get("title", ""),
                key=f"rubric_title_{i}"
            )
        
        with col2:
            weight = st.number_input(
                f"Weight (%)",
                min_value=0,
                max_value=100,
                value=rubric.get("score_weight", 0),
                key=f"rubric_weight_{i}"
            )
            
        with col3:
            # For rubrics beyond the minimum 3, show "Remove" text in a small column
            # The actual removal will be handled through a checkbox in the form
            if len(rubrics) > 3 and i >= 3:
                st.markdown("Remove")
            else:
                st.write("")  # Empty space to maintain alignment
        
        # Add a description field for each rubric
        description = st.text_input(
            f"Description (optional)",
            value=rubric.get("description", ""),
            key=f"rubric_desc_{i}",
            placeholder="Describe the criteria for this rubric item"
        )
        
        updated_rubrics.append({
            "title": title,
            "score_weight": weight,
            "description": description
        })
    
    # Generate judging criteria text from the rubrics
    judging_criteria_text = generate_judging_criteria_text(updated_rubrics)
    
    return updated_rubrics, judging_criteria_text