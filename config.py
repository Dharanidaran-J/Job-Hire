import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-challengehire-secret-key-2025-secure')
    
    # SQLite Database fallback path
    SQLITE_DATABASE_PATH = os.path.join(BASE_DIR, 'challengehire.db')
    SQLITE_DATABASE_URL = f"sqlite:///{SQLITE_DATABASE_PATH}"
    
    USE_SQLITE_FALLBACK = os.getenv('USE_SQLITE_FALLBACK', 'true').lower() in ('true', '1', 'yes')
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)) # 16 MB
    ALLOWED_EXTENSIONS = {'zip', 'pdf', 'tar', 'gz', 'py', 'js', 'html', 'json', 'txt'}
    
    # AI Engine Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

    @classmethod
    def get_database_uri(cls):
        """
        Supports PostgreSQL, MySQL, and SQLite fallback.
        Gracefully handles driver availability and dialect prefixes.
        """
        db_url = os.getenv('DATABASE_URL', '').strip()
        
        # Fix Render/Supabase legacy postgres:// prefix
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
            
        # If PostgreSQL URL is provided
        if db_url.startswith('postgresql'):
            # Check which PostgreSQL driver is available in the environment
            available_driver = None
            for driver_mod in ('psycopg', 'psycopg2', 'pg8000'):
                try:
                    __import__(driver_mod)
                    available_driver = driver_mod
                    break
                except ImportError:
                    pass
            
            if available_driver == 'pg8000':
                # Use pure-Python pg8000 dialect and strip incompatible libpq params
                base = db_url.split('?')[0]
                return base.replace('postgresql://', 'postgresql+pg8000://', 1)
            elif available_driver in ('psycopg', 'psycopg2'):
                return db_url
            else:
                # No postgres driver currently installed
                print("[Notice] No PostgreSQL driver found in Python. Falling back to SQLite for local server.")
                return cls.SQLITE_DATABASE_URL

        # If user explicitly configured MySQL without fallback
        if db_url.startswith('mysql') and not cls.USE_SQLITE_FALLBACK:
            return db_url
            
        # Test MySQL connection if provided; fallback to SQLite if unreachable
        if db_url.startswith('mysql'):
            try:
                import pymysql
                from urllib.parse import urlparse
                parsed = urlparse(db_url)
                conn = pymysql.connect(
                    host=parsed.hostname or 'localhost',
                    port=parsed.port or 3306,
                    user=parsed.username or 'root',
                    password=parsed.password or '',
                    database=parsed.path.lstrip('/') or 'challengehire_db',
                    connect_timeout=2
                )
                conn.close()
                return db_url
            except Exception:
                return cls.SQLITE_DATABASE_URL
                
        return cls.SQLITE_DATABASE_URL
