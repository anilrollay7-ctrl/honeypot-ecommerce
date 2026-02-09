"""
Backfill sessions from existing successful logins
"""
from database import DatabaseHandler
from datetime import datetime

db = DatabaseHandler()

if not db.connected:
    print("Database not connected")
    exit(1)

# Get all successful logins
successful_logins = list(db.successful_logins.find())
print(f"Found {len(successful_logins)} successful logins")

# Create sessions for each login
sessions_created = 0
for login in successful_logins:
    # Check if session already exists for this login
    existing = db.sessions.find_one({
        'email': login.get('username') or login.get('email'),
        'timestamp': login.get('timestamp')
    })
    
    if not existing:
        session_data = {
            'email': login.get('username') or login.get('email'),
            'username': login.get('username') or login.get('email'),
            'ip': login.get('ip'),
            'start_time': login.get('timestamp'),
            'timestamp': login.get('timestamp'),
            'last_activity': login.get('timestamp'),
            'status': 'active',
            'user_agent': login.get('user_agent', 'Unknown'),
            'actions': []
        }
        db.sessions.insert_one(session_data)
        sessions_created += 1
        print(f"Created session for {login.get('username') or login.get('email')}")

print(f"\n✓ Created {sessions_created} new sessions")
print(f"Total sessions now: {db.sessions.count_documents({})}")
