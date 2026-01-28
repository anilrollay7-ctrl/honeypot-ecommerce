#!/usr/bin/env python3
"""
Cowrie to MongoDB Logger
Reads Cowrie JSON logs and sends them to MongoDB dashboard in real-time
"""

import json
import time
import os
from datetime import datetime
from pymongo import MongoClient
from collections import defaultdict

# ============================================
# CONFIGURATION - UPDATE THIS!
# ============================================
MONGO_URI = "mongodb+srv://honeypot_db:anil@777A@cluster0.1o5fm7u.mongodb.net/"
DB_NAME = "honeypot_db"

# Cowrie log file path
COWRIE_LOG = "/opt/cowrie/var/log/cowrie/cowrie.json"

# How often to check for new log entries (seconds)
POLL_INTERVAL = 2

# ============================================
# MongoDB Connection
# ============================================
print("🔗 Connecting to MongoDB...")
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

# Collections
brute_force_attacks = db.brute_force_attacks
shell_interactions = db.shell_interactions
malware_downloads = db.malware_downloads
sessions = db.sessions
auth_attempts = db.auth_attempts
commands = db.commands
downloads = db.downloads

print("✅ MongoDB connected successfully!")

# ============================================
# Session Tracking
# ============================================
active_sessions = {}  # session_id -> session data
session_commands = defaultdict(list)  # session_id -> list of commands
session_auth_attempts = defaultdict(list)  # session_id -> list of login attempts

# ============================================
# Helper Functions
# ============================================

def parse_timestamp(ts_str):
    """Convert Cowrie timestamp to datetime"""
    try:
        # Cowrie format: 2024-01-28T10:30:45.123456Z
        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except:
        return datetime.utcnow()

def get_country_from_ip(ip):
    """Simple GeoIP (you can enhance with geoip2 library)"""
    # Placeholder - can integrate MaxMind GeoIP2 for real geolocation
    if ip.startswith('192.168') or ip.startswith('10.') or ip.startswith('172.'):
        return "Local"
    # Add simple IP range detection or use geoip2 library
    return "Unknown"

# ============================================
# Event Handlers
# ============================================

def handle_session_connect(event):
    """Handle new connection"""
    session_id = event.get('session')
    src_ip = event.get('src_ip')
    
    session_data = {
        'session_id': session_id,
        'src_ip': src_ip,
        'src_port': event.get('src_port'),
        'dst_port': event.get('dst_port'),
        'protocol': event.get('protocol', 'ssh'),
        'start_time': parse_timestamp(event.get('timestamp')),
        'status': 'active',
        'country': get_country_from_ip(src_ip)
    }
    
    active_sessions[session_id] = session_data
    sessions.insert_one(session_data.copy())
    print(f"🔵 New connection: {src_ip} [{session_id}]")

def handle_login_attempt(event):
    """Handle login attempt (success or failed)"""
    session_id = event.get('session')
    username = event.get('username')
    password = event.get('password')
    success = event.get('eventid') == 'cowrie.login.success'
    
    auth_data = {
        'session_id': session_id,
        'timestamp': parse_timestamp(event.get('timestamp')),
        'username': username,
        'password': password,
        'success': success,
        'src_ip': active_sessions.get(session_id, {}).get('src_ip', 'unknown')
    }
    
    auth_attempts.insert_one(auth_data)
    session_auth_attempts[session_id].append(auth_data)
    
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"🔐 Login attempt: {username}:{password} - {status}")

def handle_command(event):
    """Handle executed command"""
    session_id = event.get('session')
    input_cmd = event.get('input', '')
    
    cmd_data = {
        'session_id': session_id,
        'timestamp': parse_timestamp(event.get('timestamp')),
        'command': input_cmd,
        'src_ip': active_sessions.get(session_id, {}).get('src_ip', 'unknown')
    }
    
    commands.insert_one(cmd_data)
    session_commands[session_id].append(input_cmd)
    
    print(f"⚡ Command executed: {input_cmd}")

def handle_file_download(event):
    """Handle file download attempt"""
    session_id = event.get('session')
    url = event.get('url', '')
    outfile = event.get('outfile', '')
    
    download_data = {
        'session_id': session_id,
        'timestamp': parse_timestamp(event.get('timestamp')),
        'url': url,
        'filename': os.path.basename(outfile),
        'filepath': outfile,
        'src_ip': active_sessions.get(session_id, {}).get('src_ip', 'unknown')
    }
    
    downloads.insert_one(download_data)
    
    # Log malware download
    malware_data = {
        'timestamp': download_data['timestamp'],
        'attack_id': session_id,
        'src_ip': download_data['src_ip'],
        'malware_url': url,
        'filename': download_data['filename'],
        'country': get_country_from_ip(download_data['src_ip'])
    }
    malware_downloads.insert_one(malware_data)
    
    print(f"📥 File downloaded: {url} -> {download_data['filename']}")

def handle_session_closed(event):
    """Handle session closed"""
    session_id = event.get('session')
    
    if session_id not in active_sessions:
        return
    
    session_data = active_sessions[session_id]
    end_time = parse_timestamp(event.get('timestamp'))
    duration = (end_time - session_data['start_time']).total_seconds()
    
    # Update session
    sessions.update_one(
        {'session_id': session_id},
        {'$set': {
            'end_time': end_time,
            'duration': duration,
            'status': 'closed'
        }}
    )
    
    # Check if this was a brute force attack (multiple failed logins)
    failed_attempts = [a for a in session_auth_attempts[session_id] if not a['success']]
    if len(failed_attempts) >= 3:
        # Log as brute force attack
        usernames_tried = list(set([a['username'] for a in failed_attempts]))
        passwords_tried = list(set([a['password'] for a in failed_attempts]))
        
        brute_force_data = {
            'timestamp': session_data['start_time'],
            'attack_id': session_id,
            'src_ip': session_data['src_ip'],
            'attempts': len(failed_attempts),
            'usernames_tried': usernames_tried,
            'passwords_tried': passwords_tried,
            'country': session_data.get('country', 'Unknown'),
            'duration': duration
        }
        brute_force_attacks.insert_one(brute_force_data)
        print(f"🔴 BRUTE FORCE ATTACK DETECTED: {session_data['src_ip']} ({len(failed_attempts)} attempts)")
    
    # Check if shell interaction occurred (successful login + commands)
    successful_login = any([a['success'] for a in session_auth_attempts[session_id]])
    if successful_login and len(session_commands[session_id]) > 0:
        # Log shell interaction
        shell_data = {
            'timestamp': session_data['start_time'],
            'attack_id': session_id,
            'src_ip': session_data['src_ip'],
            'username': next((a['username'] for a in session_auth_attempts[session_id] if a['success']), 'unknown'),
            'commands_executed': session_commands[session_id],
            'num_commands': len(session_commands[session_id]),
            'duration': duration,
            'country': session_data.get('country', 'Unknown')
        }
        shell_interactions.insert_one(shell_data)
        print(f"🟢 SHELL INTERACTION LOGGED: {session_data['src_ip']} ({len(session_commands[session_id])} commands)")
    
    # Cleanup
    del active_sessions[session_id]
    del session_auth_attempts[session_id]
    del session_commands[session_id]
    
    print(f"🔴 Session closed: {session_id} (duration: {duration:.1f}s)")

# ============================================
# Event Dispatcher
# ============================================

EVENT_HANDLERS = {
    'cowrie.session.connect': handle_session_connect,
    'cowrie.login.success': handle_login_attempt,
    'cowrie.login.failed': handle_login_attempt,
    'cowrie.command.input': handle_command,
    'cowrie.session.file_download': handle_file_download,
    'cowrie.session.closed': handle_session_closed,
}

def process_event(event):
    """Process a single Cowrie event"""
    event_id = event.get('eventid')
    handler = EVENT_HANDLERS.get(event_id)
    
    if handler:
        try:
            handler(event)
        except Exception as e:
            print(f"❌ Error processing event {event_id}: {e}")
    # Silently ignore unhandled events

# ============================================
# Main Loop - Tail Cowrie JSON Log
# ============================================

def tail_log_file(filename):
    """Tail a log file like 'tail -f'"""
    # Wait for file to exist
    while not os.path.exists(filename):
        print(f"⏳ Waiting for log file: {filename}")
        time.sleep(5)
    
    print(f"📖 Reading log file: {filename}")
    
    with open(filename, 'r') as f:
        # Seek to end of file
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            
            if not line:
                # No new data, sleep and retry
                time.sleep(POLL_INTERVAL)
                continue
            
            # Parse JSON event
            try:
                event = json.loads(line.strip())
                process_event(event)
            except json.JSONDecodeError:
                pass  # Skip invalid JSON
            except Exception as e:
                print(f"❌ Error: {e}")

# ============================================
# Entry Point
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🍯 Cowrie → MongoDB Logger")
    print("=" * 60)
    print(f"📁 Log file: {COWRIE_LOG}")
    print(f"🗄️  Database: {DB_NAME}")
    print(f"🔄 Poll interval: {POLL_INTERVAL}s")
    print("=" * 60)
    print("")
    print("🚀 Starting real-time log processing...")
    print("   Press Ctrl+C to stop")
    print("")
    
    try:
        tail_log_file(COWRIE_LOG)
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
    finally:
        client.close()
        print("👋 Goodbye!")
