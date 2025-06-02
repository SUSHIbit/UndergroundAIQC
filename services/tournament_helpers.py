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

def get_detailed_rubric_explanations():
    """Get detailed explanations for common rubric criteria
    
    Returns:
        dict: Dictionary mapping rubric titles to detailed explanations
    """
    return {
        # Web Design Rubrics
        "Visual Design": {
            "description": "Evaluates the aesthetic appeal, visual hierarchy, and overall design quality",
            "criteria": [
                "Color scheme consistency and typography choices",
                "Layout balance and effective use of whitespace",
                "Overall aesthetic appeal and professionalism"
            ]
        },
        "User Experience": {
            "description": "Assesses how intuitive, accessible, and user-friendly the solution is",
            "criteria": [
                "Navigation clarity and ease of use",
                "Mobile responsiveness and accessibility",
                "Overall usability and user satisfaction"
            ]
        },
        "Technical Implementation": {
            "description": "Reviews the quality of code, technical architecture, and implementation standards",
            "criteria": [
                "Code quality, structure, and maintainability",
                "Performance optimization and best practices",
                "Technical innovation and problem-solving approach"
            ]
        },
        
        # Hackathon Rubrics
        "Innovation": {
            "description": "Measures creativity, originality, and novel approaches to problem-solving",
            "criteria": [
                "Uniqueness of the solution approach",
                "Creative use of technology and tools",
                "Potential for real-world impact and adoption"
            ]
        },
        "Technical Complexity": {
            "description": "Evaluates the sophistication and technical depth of the implementation",
            "criteria": [
                "Integration of multiple technologies and APIs",
                "Advanced features and technical capabilities",
                "Technical challenges overcome during development"
            ]
        },
        "Functionality": {
            "description": "Assesses how well the solution works and meets the intended requirements",
            "criteria": [
                "Core features working as intended",
                "Reliability and stability of the application",
                "Overall system performance and efficiency"
            ]
        },
        
        # Coding Competition Rubrics
        "Code Quality": {
            "description": "Evaluates the cleanliness, structure, and maintainability of the code",
            "criteria": [
                "Code readability and clear naming conventions",
                "Proper code organization and structure",
                "Efficient algorithms and data structure choices"
            ]
        },
        "Efficiency": {
            "description": "Measures algorithm performance, optimization, and resource utilization",
            "criteria": [
                "Time and space complexity optimization",
                "Performance under different input sizes",
                "Resource utilization and system efficiency"
            ]
        },
        "Problem Solving": {
            "description": "Assesses the approach to understanding and solving the given challenges",
            "criteria": [
                "Understanding of problem requirements",
                "Logical approach to problem decomposition",
                "Creative problem-solving techniques"
            ]
        },
        
        # Mobile Development Rubrics
        "User Interface": {
            "description": "Evaluates the mobile app's visual design and interface elements",
            "criteria": [
                "Mobile-first design principles",
                "Touch-friendly interface elements",
                "Overall aesthetic appeal on mobile devices"
            ]
        },
        "App Functionality": {
            "description": "Assesses the core features and functionality of the mobile application",
            "criteria": [
                "Core app features working correctly",
                "Smooth navigation and user experience",
                "Performance on target mobile devices"
            ]
        },
        
        # General/Strategic Rubrics
        "Strategy": {
            "description": "Evaluates the strategic thinking and planning behind the solution",
            "criteria": [
                "Clear understanding of target audience",
                "Strategic approach to problem-solving",
                "Long-term vision and scalability planning"
            ]
        },
        "Execution": {
            "description": "Measures how well the team implemented their planned solution",
            "criteria": [
                "Quality of final deliverable",
                "Meeting project requirements and constraints",
                "Effective use of available time and resources"
            ]
        },
        "Creativity": {
            "description": "Assesses original thinking and creative approaches to the challenge",
            "criteria": [
                "Original and unique ideas",
                "Creative problem-solving approaches",
                "Innovative use of existing technologies"
            ]
        },
        
        # Presentation and Communication
        "Presentation": {
            "description": "Evaluates how effectively the team communicates their solution",
            "criteria": [
                "Clarity of explanation and demonstration",
                "Professional presentation skills",
                "Ability to answer questions confidently"
            ]
        }
    }

def generate_detailed_judging_criteria_text(rubrics):
    """Generate detailed judging criteria text with explanations for each rubric
    
    Args:
        rubrics (list): List of valid rubric dictionaries
    
    Returns:
        str: Detailed judging criteria text with explanations
    """
    # Filter out empty rubrics
    valid_rubrics = [r for r in rubrics if r["title"].strip() and r["score_weight"] > 0]
    
    if not valid_rubrics:
        return ""
    
    explanations = get_detailed_rubric_explanations()
    criteria_lines = []
    
    criteria_lines.append("**Judging Criteria:**")
    criteria_lines.append("")
    
    for i, rubric in enumerate(valid_rubrics, 1):
        title = rubric['title']
        weight = rubric['score_weight']
        
        # Start with the basic rubric line
        criteria_lines.append(f"**{i}. {title} ({weight}%)**")
        
        # Add detailed explanation if available
        if title in explanations:
            explanation = explanations[title]
            criteria_lines.append(f"*{explanation['description']}*")
            criteria_lines.append("")
            criteria_lines.append("**Evaluation Criteria:**")
            for criterion in explanation['criteria']:
                criteria_lines.append(f"• {criterion}")
        else:
            # Generic explanation for custom rubric items
            criteria_lines.append(f"*This criterion evaluates the quality, completeness, and effectiveness of the {title.lower()} aspects of your submission. Teams will be assessed on how well they demonstrate mastery and innovation in this area.*")
            criteria_lines.append("")
            criteria_lines.append("**Evaluation Focus:**")
            criteria_lines.append(f"• Overall quality and execution of {title.lower()}")
            criteria_lines.append(f"• Innovation and creativity in {title.lower()} approach")
            criteria_lines.append(f"• Professional standards and best practices in {title.lower()}")
        
        criteria_lines.append("")
        criteria_lines.append("---")
        criteria_lines.append("")
    
    # Add footer
    criteria_lines.append("**Total: 100%**")
    criteria_lines.append("")
    criteria_lines.append("*Each criterion will be scored individually, and the final score will be calculated based on the weighted percentages shown above.*")
    
    return "\n".join(criteria_lines)

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
        # Default rubrics for coup_detat and other tournament types
        return [
            {"title": "Strategy", "score_weight": 40},
            {"title": "Execution", "score_weight": 30},
            {"title": "Creativity", "score_weight": 30}
        ]

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
        rubrics.append({"title": "", "score_weight": 0})
    
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
        
        updated_rubrics.append({
            "title": title,
            "score_weight": weight
        })
    
    # Generate detailed judging criteria text from the rubrics
    judging_criteria_text = generate_detailed_judging_criteria_text(updated_rubrics)
    
    return updated_rubrics, judging_criteria_text