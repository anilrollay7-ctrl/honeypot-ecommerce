"""
ADVANCED SECURITY SYSTEM - Complete Attack Detection & IP Blocking
Features:
- Real-time attack detection
- IP address blocking
- User blocking
- Brute force detection
- Post-login activity monitoring
- Suspicious behavior tracking
- Comprehensive logging
"""

from flask import request, jsonify, g
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps
import re

# ==========================================
# GLOBAL TRACKING DICTIONARIES
# ==========================================
ip_failed_attempts = defaultdict(list)  # IP -> [timestamps]
user_failed_attempts = defaultdict(list)  # Username -> [timestamps]
blocked_ips = set()  # Blocked IP addresses
blocked_users = set()  # Blocked usernames
user_activities = defaultdict(list)  # User -> [activities]
ip_activities = defaultdict(list)  # IP -> [activities]
blocked_users_per_ip = defaultdict(set)  # IP -> {blocked usernames} - track which users are blocked from each IP

# ==========================================
# CONFIGURATION
# ==========================================
MAX_FAILED_ATTEMPTS = 5  # Block user after 5 failed logins
MAX_BLOCKED_USERS_PER_IP = 3  # Block IP after 3 different users from same IP are blocked
BLOCK_DURATION_SECONDS = 3600  # Block for 1 hour
SUSPICIOUS_ACTIVITY_COUNT = 10  # Flag after 10 rapid actions
RATE_LIMIT_WINDOW = 60  # 1 minute window
MAX_REQUESTS_PER_MINUTE = 100  # Max requests per IP per minute

class AdvancedSecurityLogger:
    """Comprehensive security monitoring and attack prevention"""
    
    def __init__(self, db):
        self.db = db
        
    # ==========================================
    # IP BLOCKING & CHECKS
    # ==========================================
    
    def is_ip_blocked(self, ip):
        """Check if IP is currently blocked"""
        # Whitelist localhost IPs for testing
        if ip in ['127.0.0.1', 'localhost', '::1']:
            return False
        return ip in blocked_ips
    
    def is_user_blocked(self, username):
        """Check if user is currently blocked"""
        return username in blocked_users
    
    def block_ip(self, ip, reason, email=None):
        """Block an IP address"""
        blocked_ips.add(ip)
        
        # Log to database with email
        if self.db.blocked_ips is not None:
            self.db.blocked_ips.insert_one({
                'ip': ip,
                'email': email,
                'reason': reason,
                'timestamp': datetime.utcnow(),
                'blocked_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(seconds=BLOCK_DURATION_SECONDS),
                'status': 'active'
            })
        
        # Add to threat intelligence
        if self.db.threat_intelligence is not None:
            self.db.threat_intelligence.insert_one({
                'ip': ip,
                'email': email,
                'threat_type': 'blocked_ip',
                'reason': reason,
                'timestamp': datetime.utcnow(),
                'severity': 'high',
                'source': 'honeypot_detection'
            })
        
        print(f"🚫 BLOCKED IP: {ip} ({email}) - Reason: {reason}")
    
    def block_user(self, email, reason, ip=None):
        """Block a user account and check if IP should also be blocked"""
        blocked_users.add(email)
        
        # Track which users are blocked from this IP
        if ip:
            blocked_users_per_ip[ip].add(email)
            print(f"🔒 IP {ip} now has {len(blocked_users_per_ip[ip])} blocked user(s): {blocked_users_per_ip[ip]}")
            
            # Check if we should block the IP (after 3 different users from same IP are blocked)
            if len(blocked_users_per_ip[ip]) >= MAX_BLOCKED_USERS_PER_IP:
                self.block_ip(ip, f'{len(blocked_users_per_ip[ip])} different users blocked from this IP', email=email)
                print(f"🚨 IP {ip} BLOCKED after {len(blocked_users_per_ip[ip])} users were blocked from it")
        
        # Log to database
        if self.db.blocked_users is not None:
            self.db.blocked_users.insert_one({
                'email': email,
                'reason': reason,
                'ip': ip,
                'timestamp': datetime.now(),
                'blocked_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=BLOCK_DURATION_SECONDS),
                'status': 'active'
            })
        
        print(f"🚫 BLOCKED USER: {email} from IP {ip} - Reason: {reason}")
    
    def check_failed_login_attempts(self, identifier, is_ip=True):
        """Check if IP/user has too many failed attempts"""
        attempts = ip_failed_attempts[identifier] if is_ip else user_failed_attempts[identifier]
        
        # Remove old attempts (older than 10 minutes)
        cutoff_time = datetime.now() - timedelta(minutes=10)
        attempts = [t for t in attempts if t > cutoff_time]
        
        if is_ip:
            ip_failed_attempts[identifier] = attempts
        else:
            user_failed_attempts[identifier] = attempts
        
        return len(attempts) >= MAX_FAILED_ATTEMPTS
    
    # ==========================================
    # ATTACK DETECTION
    # ==========================================
    
    def detect_sql_injection(self, data):
        """Detect SQL injection attempts"""
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|#|\/\*|\*\/)",
            r"('|(\")|;|\)|(\%27)|(\%22))",
            r"(\bOR\b\s+\d+\s*=\s*\d+)",
            r"(\bAND\b\s+\d+\s*=\s*\d+)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, str(data), re.IGNORECASE):
                return True
        return False
    
    def detect_xss(self, data):
        """Detect XSS (Cross-Site Scripting) attempts"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
            r"<iframe",
            r"<img[^>]+src",
            r"alert\s*\(",
            r"document\.cookie"
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, str(data), re.IGNORECASE):
                return True
        return False
    
    def detect_path_traversal(self, data):
        """Detect path traversal attempts"""
        path_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"/etc/passwd",
            r"/etc/shadow",
            r"c:\\windows",
            r"%2e%2e",
            r"\.\.%2f"
        ]
        
        for pattern in path_patterns:
            if re.search(pattern, str(data), re.IGNORECASE):
                return True
        return False
    
    def detect_command_injection(self, data):
        """Detect command injection attempts"""
        cmd_patterns = [
            r";\s*(ls|cat|whoami|id|pwd|uname)",
            r"\|\s*(ls|cat|whoami|id|pwd|uname)",
            r"&&\s*(ls|cat|whoami|id|pwd|uname)",
            r"`.*`",
            r"\$\(.*\)"
        ]
        
        for pattern in cmd_patterns:
            if re.search(pattern, str(data), re.IGNORECASE):
                return True
        return False
    
    def is_suspicious_user_agent(self, user_agent):
        """Check if user agent is suspicious (bot/scanner)"""
        suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zap', 'burp',
            'metasploit', 'havij', 'acunetix', 'nessus', 'openvas',
            'scanner', 'bot', 'crawler', 'spider'
        ]
        
        user_agent_lower = user_agent.lower()
        return any(agent in user_agent_lower for agent in suspicious_agents)
    
    # ==========================================
    # ACTIVITY TRACKING
    # ==========================================
    
    def log_user_activity(self, username, action, details=None):
        """Log user activity after login and update session last_activity"""
        ip = request.remote_addr
        timestamp = datetime.utcnow()
        activity = {
            'email': username,  # Changed from 'username' to 'email'
            'ip': ip,
            'action': action,
            'details': details,
            'timestamp': timestamp,
            'path': request.path,
            'method': request.method
        }
        
        # Store in memory
        user_activities[username].append(activity)
        ip_activities[ip].append(activity)
        
        # Store in database
        if self.db.user_activities is not None:
            self.db.user_activities.insert_one(activity)
        
        # Update session last_activity time
        if self.db.sessions is not None:
            self.db.sessions.update_one(
                {
                    '$or': [
                        {'email': username},
                        {'username': username}
                    ],
                    'ip': ip,
                    'status': 'active'
                },
                {
                    '$set': {'last_activity': timestamp},
                    '$push': {'actions': {'action': action, 'timestamp': timestamp}}
                },
                upsert=False
            )
        
        # Check for suspicious rapid activity
        recent_activities = [a for a in user_activities[username] 
                           if a['timestamp'] > datetime.utcnow() - timedelta(minutes=1)]
        
        if len(recent_activities) > SUSPICIOUS_ACTIVITY_COUNT:
            self.log_attack('suspicious_activity', f'User {username} performed {len(recent_activities)} actions in 1 minute', 'medium')
            self.block_user(username, f'Suspicious rapid activity: {len(recent_activities)} actions/minute', ip=ip)
    
    def log_failed_login(self, username, ip, password=None):
        """Log failed login attempt and check for brute force"""
        timestamp = datetime.now()  # Use local time instead of UTC
        
        # Track failed attempts
        ip_failed_attempts[ip].append(timestamp)
        user_failed_attempts[username].append({
            'timestamp': timestamp,
            'password': password,
            'username': username
        })
        
        # Log to database - auth_attempts collection
        attempt_data = {
            'email': username,
            'username': username,
            'password': password,
            'ip': ip,
            'timestamp': timestamp,
            'success': False,
            'method': request.method,
            'path': request.path,
            'user_agent': username  # Store attempted username/email in user_agent field
        }
        
        if self.db.auth_attempts is not None:
            self.db.auth_attempts.insert_one(attempt_data)
        
        if self.db.failed_logins is not None:
            self.db.failed_logins.insert_one(attempt_data)
        
        # Check if should block user (not IP yet)
        if self.check_failed_login_attempts(ip, is_ip=True):
            # Don't block IP here anymore, just log the attempts
            self.log_attack('brute_force', f'IP {ip} has {len(ip_failed_attempts[ip])} failed login attempts', 'high', email=username)
            
            # Log brute force attack with all attempts
            if self.db.brute_force_attacks is not None:
                self.db.brute_force_attacks.insert_one({
                    'ip': ip,
                    'target_email': username,
                    'attempts_count': len(ip_failed_attempts[ip]),
                    'timestamp': timestamp,
                    'blocked': False,  # IP not blocked yet
                    'failed_attempts_timestamps': list(ip_failed_attempts[ip])
                })
        
        if self.check_failed_login_attempts(username, is_ip=False):
            # Block user and pass IP so we can track blocked users per IP
            self.block_user(username, f'Brute force target: {len(user_failed_attempts[username])} failed attempts', ip=ip)
            
            # Add to threat intelligence
            if self.db.threat_intelligence is not None:
                self.db.threat_intelligence.insert_one({
                    'email': username,
                    'ip': ip,
                    'threat_type': 'brute_force_target',
                    'reason': f'{len(user_failed_attempts[username])} failed login attempts',
                    'timestamp': timestamp,
                    'severity': 'high',
                    'source': 'honeypot_detection'
                })
            
            # Get all attempted credentials
            attempted_credentials = [
                {
                    'username': attempt['username'],
                    'password': attempt['password'],
                    'timestamp': attempt['timestamp']
                }
                for attempt in user_failed_attempts[username]
            ]
            
            # Log brute force for this user email with all attempted passwords
            if self.db.brute_force_attacks is not None:
                self.db.brute_force_attacks.insert_one({
                    'email': username,
                    'ip': ip,
                    'attempts_count': len(user_failed_attempts[username]),
                    'timestamp': timestamp,
                    'blocked': True,
                    'attempted_credentials': attempted_credentials  # Store all username/password attempts
                })
    
    def log_successful_login(self, username, ip):
        """Log successful login"""
        timestamp = datetime.utcnow()
        login_data = {
            'email': username,
            'username': username,
            'ip': ip,
            'timestamp': timestamp,
            'success': True,
            'method': request.method,
            'path': request.path,
            'user_agent': username  # Store username in user_agent field
        }
        
        if self.db.successful_logins is not None:
            self.db.successful_logins.insert_one(login_data)
        
        if self.db.auth_attempts is not None:
            self.db.auth_attempts.insert_one(login_data)
        
        # Create a session for this login
        if self.db.sessions is not None:
            session_data = {
                'email': username,
                'username': username,
                'ip': ip,
                'start_time': timestamp,
                'timestamp': timestamp,
                'last_activity': timestamp,
                'status': 'active',
                'user_agent': username,  # Store username in user_agent field
                'actions': []
            }
            self.db.sessions.insert_one(session_data)
        
        # Clear failed attempts for this user/IP
        if username in user_failed_attempts:
            del user_failed_attempts[username]
        if ip in ip_failed_attempts:
            del ip_failed_attempts[ip]
    
    # ==========================================
    # ATTACK LOGGING
    # ==========================================
    
    def log_attack(self, attack_type, description, severity='medium', email=None):
        """Log detected attack to database"""
        ip = request.remote_addr
        timestamp = datetime.utcnow()
        
        attack_data = {
            'timestamp': timestamp,
            'attack_type': attack_type,
            'ip': ip,
            'email': email,
            'description': description,
            'severity': severity,
            'path': request.path,
            'method': request.method,
            'headers': dict(request.headers),
            'data': self.safe_get_request_data()
        }
        
        if self.db.web_attacks is not None:
            self.db.web_attacks.insert_one(attack_data)
        
        if self.db.attack_patterns is not None:
            self.db.attack_patterns.insert_one(attack_data)
        
        # Add to threat intelligence for high severity attacks
        if severity in ['high', 'critical'] and self.db.threat_intelligence is not None:
            self.db.threat_intelligence.insert_one({
                'ip': ip,
                'email': email,
                'threat_type': attack_type,
                'reason': description,
                'timestamp': timestamp,
                'severity': severity,
                'source': 'honeypot_detection'
            })
        
        print(f"🔴 ATTACK DETECTED: {attack_type} from {ip} ({email}) - {description}")
    
    def safe_get_request_data(self):
        """Safely get request data"""
        try:
            if request.is_json:
                return request.get_json()
            elif request.form:
                return dict(request.form)
            elif request.args:
                return dict(request.args)
            return {}
        except:
            return {}
    
    # ==========================================
    # MIDDLEWARE
    # ==========================================
    
    def check_request(self):
        """Check every incoming request for attacks"""
        ip = request.remote_addr
        
        # Try to get email from request data
        email = None
        try:
            req_data = self.safe_get_request_data()
            email = req_data.get('email') or req_data.get('username')
        except:
            pass
        
        # Whitelist internal IPs (Render's internal network)
        if ip in ['127.0.0.1', 'localhost', '::1'] or ip.startswith('10.') or ip.startswith('172.'):
            return None
        
        # Check if IP is blocked
        if self.is_ip_blocked(ip):
            return jsonify({'error': 'IP address blocked due to suspicious activity'}), 403
        
        # Rate limiting
        recent_requests = [a for a in ip_activities[ip] 
                          if a['timestamp'] > datetime.utcnow() - timedelta(seconds=RATE_LIMIT_WINDOW)]
        
        if len(recent_requests) > MAX_REQUESTS_PER_MINUTE:
            self.block_ip(ip, f'Rate limit exceeded: {len(recent_requests)} requests/minute', email=email)
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # Check for attacks in request data
        request_data = str(self.safe_get_request_data())
        
        if self.detect_sql_injection(request_data):
            self.log_attack('sql_injection', f'SQL injection attempt detected', 'high', email=email)
            self.block_ip(ip, 'SQL injection attempt', email=email)
            return jsonify({'error': 'Invalid request'}), 400
        
        if self.detect_xss(request_data):
            self.log_attack('xss', f'XSS attempt detected', 'high', email=email)
            self.block_ip(ip, 'XSS attempt', email=email)
            return jsonify({'error': 'Invalid request'}), 400
        
        if self.detect_path_traversal(request_data):
            self.log_attack('path_traversal', f'Path traversal attempt detected', 'high', email=email)
            self.block_ip(ip, 'Path traversal attempt', email=email)
            return jsonify({'error': 'Invalid request'}), 400
        
        if self.detect_command_injection(request_data):
            self.log_attack('command_injection', f'Command injection attempt detected', 'critical', email=email)
            self.block_ip(ip, 'Command injection attempt', email=email)
            return jsonify({'error': 'Invalid request'}), 400
        
        # Log normal activity
        ip_activities[ip].append({
            'timestamp': datetime.utcnow(),
            'path': request.path,
            'method': request.method
        })
        
        return None  # Allow request to continue

# Create global instance
advanced_security = None

def init_advanced_security(db):
    """Initialize advanced security system"""
    global advanced_security
    advanced_security = AdvancedSecurityLogger(db)
    return advanced_security

def require_security_check(f):
    """Decorator to check request security before processing"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if advanced_security:
            result = advanced_security.check_request()
            if result:  # If check returns something, it's an error response
                return result
        return f(*args, **kwargs)
    return decorated_function
