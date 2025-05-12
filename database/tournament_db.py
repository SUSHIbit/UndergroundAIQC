import json
import streamlit as st
from database.connection import get_db_connection

def get_judges():
    """Get all users with is_judge flag set to true
    
    Returns:
        list: List of judge user dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Updated to use is_judge flag instead of role
        cursor.execute(
            """SELECT id, name, username, email, profile_picture 
               FROM users 
               WHERE is_judge = 1
               ORDER BY name"""
        )
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching judges: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def save_tournament(user_id, title, description, date_time, location, eligibility, minimum_rank, team_size, deadline, rules, judging_criteria, project_submission, judge_ids, rubrics, tournament_type="web_design"):
    """Save a tournament to the database
    
    Args:
        user_id (int): The ID of the user creating the tournament
        title (str): Tournament title
        description (str): Tournament description
        date_time (str): Date and time of the tournament
        location (str): Tournament location
        eligibility (str): Eligibility requirements
        minimum_rank (str): Minimum rank required
        team_size (int): Team size
        deadline (str): Submission deadline
        rules (str): Tournament rules
        judging_criteria (str): Judging criteria
        project_submission (str): Project submission guidelines
        judge_ids (list): List of user IDs for judges
        rubrics (list): List of rubric dictionaries with title and score_weight
        tournament_type (str): Type of tournament (web_design, coup_detat, hackathon, etc.)
        
    Returns:
        bool: Success status
    """
    # Validate rubrics before saving
    is_valid, message, filtered_rubrics = validate_rubrics(rubrics)
    if not is_valid:
        st.error(message)
        return False
    
    if not judge_ids:
        st.error("Please select at least one judge.")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First, create the tournament record
        cursor.execute(
            """INSERT INTO tournaments 
               (title, description, date_time, location, eligibility, minimum_rank, team_size, deadline, 
               rules, judging_criteria, project_submission, created_by, status, tournament_type) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (title, description, date_time, location, eligibility, minimum_rank, team_size, deadline, 
             rules, judging_criteria, project_submission, user_id, 'draft', tournament_type)
        )
        tournament_id = cursor.lastrowid
        
        # Add judge relationships
        for judge_id in judge_ids:
            cursor.execute(
                "INSERT INTO tournament_judge_users (tournament_id, user_id) VALUES (%s, %s)",
                (tournament_id, judge_id)
            )
        
        # Add rubrics
        for rubric in filtered_rubrics:
            cursor.execute(
                "INSERT INTO tournament_rubrics (tournament_id, title, score_weight) VALUES (%s, %s, %s)",
                (tournament_id, rubric['title'], rubric['score_weight'])
            )
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error saving tournament: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

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

def get_tournaments_by_type(tournament_type=None):
    """Get tournaments by type
    
    Args:
        tournament_type (str, optional): Type of tournaments to fetch. If None, fetch all.
        
    Returns:
        list: List of tournament dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if tournament_type:
            cursor.execute(
                """SELECT t.*, u.name as creator_name 
                   FROM tournaments t
                   JOIN users u ON t.created_by = u.id
                   WHERE t.tournament_type = %s
                   ORDER BY t.date_time DESC""", 
                (tournament_type,)
            )
        else:
            cursor.execute(
                """SELECT t.*, u.name as creator_name 
                   FROM tournaments t
                   JOIN users u ON t.created_by = u.id
                   ORDER BY t.date_time DESC"""
            )
        
        tournaments = cursor.fetchall()
        
        # Fetch judges for each tournament
        for tournament in tournaments:
            cursor.execute(
                """SELECT j.id, j.name, j.username, tju.role
                   FROM tournament_judge_users tju
                   JOIN users j ON tju.user_id = j.id
                   WHERE tju.tournament_id = %s""",
                (tournament['id'],)
            )
            tournament['judges'] = cursor.fetchall()
            
            # Fetch rubrics for each tournament
            cursor.execute(
                """SELECT id, title, score_weight
                   FROM tournament_rubrics
                   WHERE tournament_id = %s
                   ORDER BY id""",
                (tournament['id'],)
            )
            tournament['rubrics'] = cursor.fetchall()
            
        return tournaments
    except Exception as e:
        st.error(f"Error fetching tournaments: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_tournament_by_id(tournament_id):
    """Get a specific tournament by ID
    
    Args:
        tournament_id (int): The tournament ID to fetch
        
    Returns:
        dict: Tournament details or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            """SELECT t.*, u.name as creator_name 
               FROM tournaments t
               JOIN users u ON t.created_by = u.id
               WHERE t.id = %s""", 
            (tournament_id,)
        )
        
        tournament = cursor.fetchone()
        
        if tournament:
            # Fetch judges
            cursor.execute(
                """SELECT j.id, j.name, j.username, tju.role
                   FROM tournament_judge_users tju
                   JOIN users j ON tju.user_id = j.id
                   WHERE tju.tournament_id = %s""",
                (tournament_id,)
            )
            tournament['judges'] = cursor.fetchall()
            
            # Fetch rubrics
            cursor.execute(
                """SELECT id, title, score_weight
                   FROM tournament_rubrics
                   WHERE tournament_id = %s
                   ORDER BY id""",
                (tournament_id,)
            )
            tournament['rubrics'] = cursor.fetchall()
            
        return tournament
    except Exception as e:
        st.error(f"Error fetching tournament: {e}")
        return None
    finally:
        cursor.close()
        conn.close()