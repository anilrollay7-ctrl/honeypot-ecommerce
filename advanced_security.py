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

# ==========================================
# CONFIGURATION
# ==========================================
MAX_FAILED_ATTEMPTS = 5  # Block after 5 failed logins
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
        return ip in blocked_ips
    
    def is_user_blocked(self, username):
        """Check if user is currently blocked"""
        return username in blocked_users
    
    def block_ip(self, ip, reason):
        """Block an IP address"""
        blocked_ips.add(ip)
        
        # Log to database
        self.db.blocked_ips.insert_one({
            'ip': ip,
            'reason': reason,
            'blocked_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(seconds=BLOCK_DURATION_SECONDS),
            'status': 'active'
        })
        
        print(f"🚫 BLOCKED IP: {ip} - Reason: {reason}")
    
    def block_user(self, username, reason):
        """Block a user account"""
        blocked_users.add(username)
        
        # Log to database
        self.db.blocked_users.insert_one({
            'username': username,
            'reason': reason,
            'blocked_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(seconds=BLOCK_DURATION_SECONDS),
            'status': 'active'
        })
        
        print(f"🚫 BLOCKED USER: {username} - Reason: {reason}")
    
    def check_failed_login_attempts(self, identifier, is_ip=True):
        """Check if IP/user has too many failed attempts"""
        attempts = ip_failed_attempts[identifier] if is_ip else user_failed_attempts[identifier]
        
        # Remove old attempts (older than 10 minutes)
        cutoff_time = datetime.utcnow() - timedelta(minutes=10)
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
        """Log user activity after login"""
        ip = request.remote_addr
        activity = {
            'username': username,
            'ip': ip,
            'action': action,
            'details': details,
            'timestamp': datetime.utcnow(),
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'path': request.path,
            'method': request.method
        }
        
        # Store in memory
        user_activities[username].append(activity)
        ip_activities[ip].append(activity)
        
        # Store in database
        self.db.user_activities.insert_one(activity)
        
        # Check for suspicious rapid activity
        recent_activities = [a for a in user_activities[username] 
                           if a['timestamp'] > datetime.utcnow() - timedelta(minutes=1)]
        
        if len(recent_activities) > SUSPICIOUS_ACTIVITY_COUNT:
            self.log_attack('suspicious_activity', f'User {username} performed {len(recent_activities)} actions in 1 minute', 'medium')
            self.block_user(username, f'Suspicious rapid activity: {len(recent_activities)} actions/minute')
    
    def log_failed_login(self, username, ip):
        """Log failed login attempt and check for brute force"""
        timestamp = datetime.utcnow()
        
        # Track failed attempts
        ip_failed_attempts[ip].append(timestamp)
        user_failed_attempts[username].append(timestamp)
        
        # Log to database
        self.db.failed_logins.insert_one({
            'username': username,
            'ip': ip,
            'timestamp': timestamp,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        })
        
        # Check if should block
        if self.check_failed_login_attempts(ip, is_ip=True):
            self.block_ip(ip, f'Brute force attack: {len(ip_failed_attempts[ip])} failed attempts')
            self.log_attack('brute_force', f'IP {ip} blocked after {len(ip_failed_attempts[ip])} failed login attempts', 'high')
        
        if self.check_failed_login_attempts(username, is_ip=False):
            self.block_user(username, f'Brute force target: {len(user_failed_attempts[username])} failed attempts')
    
    def log_successful_login(self, username, ip):
        """Log successful login"""
        self.db.successful_logins.insert_one({
            'username': username,
            'ip': ip,
            'timestamp': datetime.utcnow(),
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        })
        
        # Clear failed attempts for this user/IP
        if username in user_failed_attempts:
            del user_failed_attempts[username]
        if ip in ip_failed_attempts:
            del ip_failed_attempts[ip]
    
    # ==========================================
    # ATTACK LOGGING
    # ==========================================
    
    def log_attack(self, attack_type, description, severity='medium'):
        """Log detected attack to database"""
        ip = request.remote_addr
        
        attack_data = {
            'timestamp': datetime.utcnow(),
            'attack_type': attack_type,
            'ip': ip,
            'description': description,
            'severity': severity,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'path': request.path,
            'method': request.method,
            'headers': dict(request.headers),
            'data': self.safe_get_request_data()
        }
        
        if self.db.web_attacks is not None:
            self.db.web_attacks.insert_one(attack_data)
        print(f"🔴 ATTACK DETECTED: {attack_type} from {ip} - {description}")
    
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
            self.block_ip(ip, f'Rate limit exceeded: {len(recent_requests)} requests/minute')
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # Check user agent
        user_agent = request.headers.get('User-Agent', '')
        if self.is_suspicious_user_agent(user_agent):
            self.log_attack('suspicious_user_agent', f'Suspicious user agent: {user_agent}', 'low')
        
        # Check for attacks in request data
        request_data = str(self.safe_get_request_data())
        
        if self.detect_sql_injection(request_data):
            self.log_attack('sql_injection', f'SQL injection attempt detected', 'high')
            self.block_ip(ip, 'SQL injection attempt')
            return jsonify({'error': 'Invalid request'}), 400
        
        if self.detect_xss(request_data):
            self.log_attack('xss', f'XSS attempt detected', 'high')
            self.block_ip(ip, 'XSS attempt')
            return jsonify({'error': 'Invalid request'}), 400
        
        if self.detect_path_traversal(request_data):
            self.log_attack('path_traversal', f'Path traversal attempt detected', 'high')
            self.block_ip(ip, 'Path traversal attempt')
            return jsonify({'error': 'Invalid request'}), 400
        
        if self.detect_command_injection(request_data):
            self.log_attack('command_injection', f'Command injection attempt detected', 'critical')
            self.block_ip(ip, 'Command injection attempt')
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
