import json
import streamlit as st
from database.connection import get_db_connection

def save_tournament(user_id, title, description, date_time, location, eligibility, minimum_rank, team_size, deadline, rules, judging_criteria, project_submission, judges, tournament_type="web_design"):
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
        judges (list): List of judge dictionaries with name and role
        tournament_type (str): Type of tournament (web_design, coup_detat, hackathon, etc.)
        
    Returns:
        bool: Success status
    """
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
        
        # Add judges
        for judge in judges:
            cursor.execute(
                "INSERT INTO tournament_judges (tournament_id, name, role) VALUES (%s, %s, %s)",
                (tournament_id, judge['name'], judge.get('role', ''))
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
                "SELECT name, role FROM tournament_judges WHERE tournament_id = %s",
                (tournament['id'],)
            )
            tournament['judges'] = cursor.fetchall()
            
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
                "SELECT name, role FROM tournament_judges WHERE tournament_id = %s",
                (tournament_id,)
            )
            tournament['judges'] = cursor.fetchall()
            
        return tournament
    except Exception as e:
        st.error(f"Error fetching tournament: {e}")
        return None
    finally:
        cursor.close()
        conn.close()