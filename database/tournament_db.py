import json
import streamlit as st
from database.connection import get_db_connection

def save_tournament(user_id, title, description, date_time, location, eligibility, minimum_rank, team_size, deadline, rules, judging_criteria, project_submission, judges):
    """Save a tournament to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First, create the tournament record
        cursor.execute(
            """INSERT INTO tournaments 
               (title, description, date_time, location, eligibility, minimum_rank, team_size, deadline, rules, judging_criteria, project_submission, created_by, status) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (title, description, date_time, location, eligibility, minimum_rank, team_size, deadline, rules, judging_criteria, project_submission, user_id, 'draft')
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