import mysql.connector
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database configuration from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def get_db_connection():
    """
    Create and return a connection to the MySQL database
    """
    try:
        # Hardcoded values for testing
        return mysql.connector.connect(
            host="srv482.hstgr.io",  # Direct value instead of environment variable
            user="u975692652_sushimaru4",
            password="K~s2ivj~33K",
            database="u975692652_projectugf",
            port=3306
        )
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None