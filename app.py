"""
Enhanced Flask API with Real-time Updates and Analysis
"""
from flask import Flask, jsonify, render_template, request, Response, stream_with_context
from flask_cors import CORS
from database import DatabaseHandler
from security_logger import security_logger
from advanced_security import init_advanced_security, require_security_check
from config import Config
from ecommerce_api import ecommerce
# from attack_simulator import HoneypotAttackSimulator  # Disabled - real attacks only
import json
from bson import ObjectId
from datetime import datetime
import time

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Register ecommerce blueprint
app.register_blueprint(ecommerce)

db = DatabaseHandler()

# Initialize advanced security system
advanced_security = init_advanced_security(db)

# Connect advanced security to ecommerce API
from ecommerce_api import set_advanced_security
set_advanced_security(advanced_security)

# ========================================
# SYNTHETIC ATTACK SIMULATION DISABLED
# System now ready for REAL attacks only
# ========================================
# simulator = HoneypotAttackSimulator(db)
# simulator.start_background_simulation(interval=30)


# Custom JSON encoder for MongoDB ObjectId and datetime
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = JSONEncoder

# Security middleware - check every request
@app.before_request
def security_check():
    """Check request security before processing"""
    if advanced_security and not request.path.startswith('/static'):
        result = advanced_security.check_request()
        if result:
            return result

@app.route('/')
def index():
    """Serve React e-commerce application or honeypot dashboard"""
    import os
    static_folder = os.path.join(app.root_path, 'static')
    
    # If React build exists, serve it
    if os.path.exists(os.path.join(static_folder, 'index.html')):
        from flask import send_from_directory
        return send_from_directory(static_folder, 'index.html')
    
    # Otherwise serve honeypot dashboard
    return render_template('dashboard_honeypot.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files for React app"""
    import os
    from flask import send_from_directory
    static_folder = os.path.join(app.root_path, 'static')
    
    if os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    
    # For React Router, return index.html
    if os.path.exists(os.path.join(static_folder, 'index.html')):
        return send_from_directory(static_folder, 'index.html')
    
    return "Not Found", 404

@app.route('/dashboard')
def dashboard():
    """Original dashboard page"""
    return render_template('dashboard.html')

@app.route('/analysis')
def analysis_page():
    """Analysis results page"""
    return render_template('analysis.html')

@app.route('/logs')
def logs_page():
    """Security logs viewer page"""
    return render_template('logs.html')

@app.route('/realtime')
def realtime_page():
    """Real-time monitoring page"""
    return render_template('realtime.html')

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    try:
        stats = db.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions')
def get_sessions():
    """Get recent sessions"""
    try:
        limit = request.args.get('limit', 50, type=int)
        sessions = db.get_recent_sessions(limit)
        return jsonify(sessions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth-attempts')
def get_auth_attempts():
    """Get recent authentication attempts"""
    try:
        limit = request.args.get('limit', 100, type=int)
        attempts = db.get_recent_auth_attempts(limit)
        return jsonify(attempts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/commands')
def get_commands():
    """Get recent commands"""
    try:
        limit = request.args.get('limit', 100, type=int)
        commands = db.get_recent_commands(limit)
        return jsonify(commands)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-attackers')
def get_top_attackers():
    """Get top attacking IPs"""
    try:
        limit = request.args.get('limit', 10, type=int)
        attackers = db.get_top_attackers(limit)
        return jsonify(attackers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-usernames')
def get_top_usernames():
    """Get most common usernames"""
    try:
        limit = request.args.get('limit', 10, type=int)
        usernames = db.get_top_usernames(limit)
        return jsonify(usernames)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-passwords')
def get_top_passwords():
    """Get most common passwords"""
    try:
        limit = request.args.get('limit', 10, type=int)
        passwords = db.get_top_passwords(limit)
        return jsonify(passwords)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-commands')
def get_top_commands():
    """Get most executed commands"""
    try:
        limit = request.args.get('limit', 10, type=int)
        commands = db.get_top_commands(limit)
        return jsonify(commands)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timeline')
def get_timeline():
    """Get attack timeline"""
    try:
        days = request.args.get('days', 7, type=int)
        timeline = db.get_attack_timeline(days)
        return jsonify(timeline)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/downloads')
def get_downloads():
    """Get file downloads"""
    try:
        downloads = list(db.downloads.find().sort('timestamp', -1).limit(50))
        return jsonify(downloads)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.sessions.count_documents({})
        return jsonify({'status': 'healthy', 'database': 'connected', 'realtime': True, 'analysis': True})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/stream/events')
def stream_events():
    """Server-Sent Events stream for real-time updates"""
    def event_stream():
        while True:
            try:
                time.sleep(2)
                stats = db.get_stats()
                yield f"data: {json.dumps(stats, cls=JSONEncoder)}\n\n"
            except GeneratorExit:
                break
            except Exception as e:
                print(f"Stream error: {e}")
                break
    
    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )

@app.route('/api/logs/security')
def get_security_logs():
    """Get security logs"""
    try:
        log_type = request.args.get('type', 'all')
        limit = request.args.get('limit', 100, type=int)
        logs = security_logger.get_recent_logs(log_type, limit)
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/threat-report')
def get_threat_report():
    """Generate threat analysis report"""
    try:
        report = security_logger.create_threat_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ADVANCED SECURITY ENDPOINTS ====================

@app.route('/api/security/blocked-ips')
@require_security_check
def get_blocked_ips():
    """Get all blocked IP addresses"""
    try:
        blocked = list(db.blocked_ips.find().sort('blocked_at', -1).limit(100))
        return jsonify(blocked)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/blocked-users')
@require_security_check
def get_blocked_users():
    """Get all blocked users"""
    try:
        blocked = list(db.blocked_users.find().sort('blocked_at', -1).limit(100))
        return jsonify(blocked)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/user-activities/<username>')
@require_security_check
def get_user_activities(username):
    """Get all activities for a specific user"""
    try:
        activities = list(db.user_activities.find({'username': username}).sort('timestamp', -1).limit(200))
        return jsonify(activities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/ip-activities/<ip>')
@require_security_check
def get_ip_activities(ip):
    """Get all activities for a specific IP"""
    try:
        activities = list(db.user_activities.find({'ip': ip}).sort('timestamp', -1).limit(200))
        return jsonify(activities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/failed-logins')
@require_security_check
def get_failed_logins():
    """Get recent failed login attempts"""
    try:
        limit = request.args.get('limit', 100, type=int)
        failed = list(db.failed_logins.find().sort('timestamp', -1).limit(limit))
        return jsonify(failed)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/successful-logins')
@require_security_check
def get_successful_logins():
    """Get recent successful logins"""
    try:
        limit = request.args.get('limit', 100, type=int)
        successful = list(db.successful_logins.find().sort('timestamp', -1).limit(limit))
        return jsonify(successful)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/web-attacks')
@require_security_check
def get_web_attacks():
    """Get all web attacks (SQL, XSS, etc.)"""
    try:
        limit = request.args.get('limit', 100, type=int)
        attack_type = request.args.get('type', None)
        
        query = {}
        if attack_type:
            query['attack_type'] = attack_type
        
        attacks = list(db.web_attacks.find(query).sort('timestamp', -1).limit(limit))
        return jsonify(attacks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/stats')
@require_security_check
def get_security_stats():
    """Get comprehensive security statistics"""
    try:
        stats = {
            'blocked_ips_count': db.blocked_ips.count_documents({}),
            'blocked_users_count': db.blocked_users.count_documents({}),
            'failed_logins_count': db.failed_logins.count_documents({}),
            'successful_logins_count': db.successful_logins.count_documents({}),
            'web_attacks_count': db.web_attacks.count_documents({}),
            'total_user_activities': db.user_activities.count_documents({}),
            
            # Attack breakdown
            'attack_breakdown': {
                'sql_injection': db.web_attacks.count_documents({'attack_type': 'sql_injection'}),
                'xss': db.web_attacks.count_documents({'attack_type': 'xss'}),
                'path_traversal': db.web_attacks.count_documents({'attack_type': 'path_traversal'}),
                'command_injection': db.web_attacks.count_documents({'attack_type': 'command_injection'}),
                'brute_force': db.web_attacks.count_documents({'attack_type': 'brute_force'}),
                'suspicious_activity': db.web_attacks.count_documents({'attack_type': 'suspicious_activity'}),
            },
            
            # Recent activity
            'recent_blocked_ips': list(db.blocked_ips.find().sort('blocked_at', -1).limit(5)),
            'recent_attacks': list(db.web_attacks.find().sort('timestamp', -1).limit(10)),
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/unblock-ip/<ip>', methods=['POST'])
@require_security_check
def unblock_ip(ip):
    """Manually unblock an IP address"""
    try:
        from advanced_security import blocked_ips
        if ip in blocked_ips:
            blocked_ips.remove(ip)
        
        db.blocked_ips.update_one(
            {'ip': ip, 'status': 'active'},
            {'$set': {'status': 'unblocked', 'unblocked_at': datetime.utcnow()}}
        )
        
        return jsonify({'success': True, 'message': f'IP {ip} unblocked'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/security/unblock-user/<username>', methods=['POST'])
@require_security_check
def unblock_user(username):
    """Manually unblock a user"""
    try:
        from advanced_security import blocked_users
        if username in blocked_users:
            blocked_users.remove(username)
        
        db.blocked_users.update_one(
            {'username': username, 'status': 'active'},
            {'$set': {'status': 'unblocked', 'unblocked_at': datetime.utcnow()}}
        )
        
        return jsonify({'success': True, 'message': f'User {username} unblocked'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HONEYPOT ATTACK ENDPOINTS ====================

@app.route('/api/honeypot/brute-force')
def get_brute_force_attacks():
    """Get brute force attack statistics"""
    try:
        stats = db.get_brute_force_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/honeypot/shell-interactions')
def get_shell_interactions():
    """Get shell interaction statistics"""
    try:
        stats = db.get_shell_interaction_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/honeypot/malware')
def get_malware_stats():
    """Get malware download statistics"""
    try:
        stats = db.get_malware_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/honeypot/recent-attacks')
def get_recent_attacks():
    """Get recent attack activities"""
    try:
        limit = request.args.get('limit', 20, type=int)
        attacks = db.get_recent_attacks(limit)
        return jsonify(attacks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/honeypot/attack-heatmap')
def get_attack_heatmap():
    """Get attack heatmap data"""
    try:
        days = request.args.get('days', 7, type=int)
        heatmap = db.get_attack_heatmap(days)
        return jsonify(heatmap)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/honeypot/simulate-attack', methods=['POST'])
def simulate_attack():
    """Manually trigger attack simulation - DISABLED (Real attacks only)"""
    return jsonify({
        'status': 'disabled', 
        'message': 'Synthetic attacks disabled. System captures REAL attacks only.'
    }), 403

@app.route('/api/honeypot/dashboard-stats')
def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        stats = {
            'overview': db.get_stats(),
            'brute_force': db.get_brute_force_stats(),
            'shell_interactions': db.get_shell_interaction_stats(),
            'malware': db.get_malware_stats(),
            'top_attackers': db.get_top_attackers(10),
            'top_usernames': db.get_top_usernames(10),
            'top_passwords': db.get_top_passwords(10),
            'top_commands': db.get_top_commands(10),
            'recent_attacks': db.get_recent_attacks(10)
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"Starting Enhanced Honeypot Dashboard on {Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}")
    print(f"MongoDB URI: {Config.MONGODB_URI}")
    print(f"Database: {Config.MONGODB_DATABASE}")
    print(f"Real-time Updates: Enabled")
    print(f"Security Logs: Enabled")
    
    # Serve React frontend in production
    import os
    port = int(os.environ.get('PORT', Config.DASHBOARD_PORT))
    host = os.environ.get('HOST', Config.DASHBOARD_HOST)
    
    app.run(
        host=host,
        port=port,
        debug=False,  # Disable debug in production
        threaded=True
    )
