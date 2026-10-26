#!/usr/bin/env python3
"""
ChallengeHire Runner Script
Start the web server: python run.py
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"=== ChallengeHire is starting on http://127.0.0.1:{port} ===")
    app.run(host='0.0.0.0', port=port, debug=True)
