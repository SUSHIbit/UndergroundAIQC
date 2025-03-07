import json
import streamlit as st
from database.connection import get_db_connection

def get_next_set_number():
    """Get the next available set number"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT MAX(set_number) FROM sets")
        result = cursor.fetchone()
        next_set = 1 if result[0] is None else result[0] + 1
        return next_set
    except Exception as e:
        st.error(f"Error getting next set number: {e}")
        return 1
    finally:
        cursor.close()
        conn.close()

def get_subjects():
    """Get all subjects from the database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM subjects ORDER BY name")
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching subjects: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def create_subject(name):
    """Create a new subject in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO subjects (name) VALUES (%s)", (name,))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        st.error(f"Error creating subject: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def get_topics(subject_id):
    """Get all topics for a specific subject"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT * FROM topics WHERE subject_id = %s ORDER BY name", 
            (subject_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching topics: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def create_topic(subject_id, name):
    """Create a new topic in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO topics (subject_id, name) VALUES (%s, %s)", 
            (subject_id, name)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        st.error(f"Error creating topic: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def get_quiz_sets():
    """Get all quiz sets from the database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT s.id, s.set_number, qd.subject_id, qd.topic_id, 
                   sub.name as subject_name, t.name as topic_name
            FROM sets s
            JOIN quiz_details qd ON s.id = qd.set_id
            JOIN subjects sub ON qd.subject_id = sub.id
            JOIN topics t ON qd.topic_id = t.id
            WHERE s.type = 'quiz'
            ORDER BY s.set_number
        """)
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching quiz sets: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def save_quiz(set_number, user_id, subject_id, topic_id, questions):
    """Save a quiz to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First, create the set record with 'draft' status
        cursor.execute(
            "INSERT INTO sets (set_number, type, created_by, status) VALUES (%s, %s, %s, %s)",
            (set_number, 'quiz', user_id, 'draft')
        )
        set_id = cursor.lastrowid
        
        # Then, create the quiz details record
        cursor.execute(
            "INSERT INTO quiz_details (set_id, subject_id, topic_id) VALUES (%s, %s, %s)",
            (set_id, subject_id, topic_id)
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
        st.error(f"Error saving quiz: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_quiz_questions(set_ids):
    """Get questions for specific quiz sets"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    questions = []
    try:
        # Convert set_ids to a comma-separated string for SQL IN clause
        set_ids_str = ', '.join(map(str, set_ids))
        
        cursor.execute(f"""
            SELECT q.*, s.set_number 
            FROM questions q
            JOIN sets s ON q.set_id = s.id
            WHERE q.set_id IN ({set_ids_str})
            ORDER BY s.set_number, q.question_number
        """)
        questions = cursor.fetchall()
        
        # Convert the JSON string to actual Python dictionaries
        for q in questions:
            q['options'] = json.loads(q['options'])
            
        return questions
    except Exception as e:
        st.error(f"Error fetching quiz questions: {e}")
        return []
    finally:
        cursor.close()
        conn.close()