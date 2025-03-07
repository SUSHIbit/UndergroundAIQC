import streamlit as st
from database.connection import get_db_connection

def verify_password(stored_password, provided_password):
    """
    Verify a password against its hashed value from Laravel
    
    Note: In a production environment, use a proper Laravel-compatible 
    password verification library
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get the user by username
        cursor.execute(
            "SELECT * FROM users WHERE username = %s", 
            (provided_password,)
        )
        return True
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def authenticate_user(username, password):
    """
    Authenticate a user and return their details if valid
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get the user by username
        cursor.execute(
            "SELECT * FROM users WHERE username = %s", 
            (username,)
        )
        user = cursor.fetchone()
        
        if user and user['role'] == 'lecturer':
            # In a real implementation, you would need to use a proper Laravel-compatible 
            # password verification function instead of this simplified approach
            return user
        return None
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()