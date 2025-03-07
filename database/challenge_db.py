import json
import streamlit as st
from database.connection import get_db_connection

def save_challenge(set_number, user_id, name, prerequisite_ids, questions):
    """Save a challenge to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First, create the set record
        cursor.execute(
            "INSERT INTO sets (set_number, type, created_by) VALUES (%s, %s, %s)",
            (set_number, 'challenge', user_id)
        )
        set_id = cursor.lastrowid
        
        # Then, create the challenge details record
        cursor.execute(
            "INSERT INTO challenge_details (set_id, name) VALUES (%s, %s)",
            (set_id, name)
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