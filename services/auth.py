import streamlit as st
from database.connection import get_db_connection
import bcrypt

def verify_password(stored_hash, provided_password):
    """
    Verify a bcrypt password hash against the provided password.
    
    Args:
        stored_hash (str): The bcrypt hash from the database
        provided_password (str): The password provided during login
    
    Returns:
        bool: True if the password matches, False otherwise
    """
    try:
        # Convert inputs to bytes
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        if isinstance(provided_password, str):
            provided_password = provided_password.encode('utf-8')
            
        # Check if the stored_hash is a valid bcrypt hash format
        if stored_hash.startswith(b'$2y$') or stored_hash.startswith(b'$2a$') or stored_hash.startswith(b'$2b$'):
            # Verify password with bcrypt
            return bcrypt.checkpw(provided_password, stored_hash)
        else:
            # Fall back to direct comparison for non-bcrypt passwords
            return stored_hash == provided_password
    except Exception as e:
        st.error(f"Password verification error: {e}")
        return False

def authenticate_user(username, password):
    """
    Authenticate a user and return their details if valid.
    Supports bcrypt hashed passwords from Laravel or other frameworks.
    
    Args:
        username (str): The username to check
        password (str): The password to verify
    
    Returns:
        dict: User data if authentication succeeds, None otherwise
    """
    conn = get_db_connection()
    if not conn:
        st.error("Could not connect to database")
        return None
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get the user by username only
        cursor.execute(
            "SELECT * FROM users WHERE username = %s", 
            (username,)
        )
        user = cursor.fetchone()
        
        if user:
            # Verify the password against the stored hash
            stored_password = user.get('password', '')
            
            if verify_password(stored_password, password) and user.get('role') == 'lecturer':
                return user
        
        return None
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()