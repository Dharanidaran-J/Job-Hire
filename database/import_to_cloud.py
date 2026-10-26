"""
ChallengeHire - Automated Cloud Database Importer
Run this script to automatically import all tables and seed data
into ANY cloud-hosted MySQL or PostgreSQL database.

Usage:
    python database/import_to_cloud.py
    OR
    python database/import_to_cloud.py "mysql+pymysql://user:pass@host:port/dbname?ssl_verify_cert=true"
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from config import Config
from models import db
from database.init_db import seed_database

def import_to_cloud(db_url=None):
    if not db_url:
        if len(sys.argv) > 1 and sys.argv[1].strip():
            db_url = sys.argv[1].strip()
        else:
            print("=" * 60)
            print("  ChallengeHire: Cloud Database Setup & Importer")
            print("=" * 60)
            db_url = input("\nEnter your Cloud Database Connection String:\n(e.g. mysql+pymysql://root:pass@host:4000/test?ssl_verify_cert=true)\n> ").strip()

    if not db_url:
        print("[ERROR] No database URL provided. Exiting.")
        return

    print("\n[1/3] Initializing connection to cloud database...")
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        try:
            print("[2/3] Creating all 18 normalized tables in cloud database...")
            db.create_all()
            print("      ✓ Tables created successfully!")

            print("[3/3] Populating realistic seed data...")
            seed_database(app)
            print("      ✓ Seed records (skills, jobs, challenges, users) inserted!")

            print("\n" + "=" * 60)
            print("  SUCCESS! Your online database is fully configured and live!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Update your .env file with this connection string:")
            print(f"   DATABASE_URL={db_url}")
            print("   USE_SQLITE_FALLBACK=false")
            print("2. Run your app: python run.py")

        except Exception as e:
            print(f"\n[ERROR] Database import failed: {e}")
            print("\nTip: If using TiDB Cloud or Aiven, ensure you appended '?ssl_verify_cert=true' to the URL.")

if __name__ == '__main__':
    import_to_cloud()
