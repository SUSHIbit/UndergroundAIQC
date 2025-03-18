import json
import streamlit as st
from database.connection import get_db_connection

def save_challenge(set_number, user_id, name, prerequisite_ids, questions, timer_minutes=None):
    """Save a challenge to the database
    
    Args:
        set_number (int): The challenge set number
        user_id (int): The ID of the user creating the challenge
        name (str): Challenge name
        prerequisite_ids (list): List of prerequisite set IDs
        questions (list): List of question dictionaries
        timer_minutes (int, optional): Time limit in minutes for the challenge
        
    Returns:
        bool: Success status
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First, create the set record
        cursor.execute(
            "INSERT INTO sets (set_number, type, created_by) VALUES (%s, %s, %s)",
            (set_number, 'challenge', user_id)
        )
        set_id = cursor.lastrowid
        
        # Then, create the challenge details record with timer
        cursor.execute(
            "INSERT INTO challenge_details (set_id, name, timer_minutes) VALUES (%s, %s, %s)",
            (set_id, name, timer_minutes)
        )
        challenge_id = cursor.lastrowid
        
        # Add prerequisite records
        for prereq_id in prerequisite_ids:
            cursor.execute(
                "INSERT INTO challenge_prerequisites (challenge_id, prerequisite_set_id) VALUES (%s, %s)",
                (challenge_id, prereq_id)
            )
        
        # Finally, insert all questions
        for i, q in enumerate(questions, 1):
            options_json = json.dumps(q['options'])
            cursor.execute(
                """INSERT INTO questions 
                   (set_id, question_number, question_text, options, correct_answer, reason)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (set_id, i, q['question'], options_json, q['answer'], q['reason'])
            )
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error saving challenge: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_challenge_sets():
    """Get all challenge sets from the database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT s.id, s.set_number, cd.name, cd.timer_minutes
            FROM sets s
            JOIN challenge_details cd ON s.id = cd.set_id
            WHERE s.type = 'challenge'
            ORDER BY s.set_number
        """)
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching challenge sets: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_challenge_timer(set_id):
    """Get the timer setting for a specific challenge set
    
    Args:
        set_id (int): The challenge set ID
        
    Returns:
        int or None: Timer minutes or None if not set
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT timer_minutes FROM challenge_details WHERE set_id = %s", 
            (set_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        st.error(f"Error fetching challenge timer: {e}")
        return None
    finally:
        cursor.close()
        conn.close()