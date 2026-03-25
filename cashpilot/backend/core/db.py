import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load the .env file from the root directory
# __file__ is backend/core/db.py
# parent is core
# parent.parent is backend
# parent.parent.parent is root (cashpilot)
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
dotenv_path = os.path.join(root_dir, '.env')

load_dotenv(dotenv_path)

def get_db_connection():
    """
    Creates and returns a strict Postgres connection using psycopg2 and RealDictCursor.
    Zero hallucination policy: Uses DATABASE_URL from the root .env.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables. Make sure .env is at the root directory.")
    
    try:
        # We add connect_timeout to prevent the script from hanging
        conn = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor,
            connect_timeout=10,
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"🔥 Connection Error: {e}")
        return None
