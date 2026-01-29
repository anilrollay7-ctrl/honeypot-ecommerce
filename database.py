"""
MongoDB Database Handler for Honeypot
"""
from pymongo import MongoClient, DESCENDING
from datetime import datetime, timedelta
import json
from config import Config

class DatabaseHandler:
    def __init__(self):
        try:
            # MongoDB connection with SSL/TLS configuration
            self.client = MongoClient(
                Config.MONGODB_URI, 
                serverSelectionTimeoutMS=5000,
                tls=True,
                tlsAllowInvalidCertificates=False
            )
            self.client.server_info()  # Test connection
            self.db = self.client[Config.MONGODB_DATABASE]
            
            # Cowrie honeypot collections
            self.sessions = self.db[Config.COLLECTION_SESSIONS]
            self.auth_attempts = self.db[Config.COLLECTION_AUTH_ATTEMPTS]
            self.commands = self.db[Config.COLLECTION_COMMANDS]
            self.downloads = self.db[Config.COLLECTION_DOWNLOADS]
            self.stats = self.db[Config.COLLECTION_STATS]
            
            # Attack analysis collections
            self.brute_force_attacks = self.db['brute_force_attacks']
            self.shell_interactions = self.db['shell_interactions']
            self.malware_downloads = self.db['malware_downloads']
            self.attack_patterns = self.db['attack_patterns']
            self.threat_intelligence = self.db['threat_intelligence']
            
            # Advanced security collections
            self.blocked_ips = self.db['blocked_ips']
            self.blocked_users = self.db['blocked_users']
            self.user_activities = self.db['user_activities']
            self.failed_logins = self.db['failed_logins']
            self.successful_logins = self.db['successful_logins']
            self.web_attacks = self.db['web_attacks']
            
            self.connected = True
            # Create indexes
            self._create_indexes()
            print("✓ MongoDB connected successfully")
        except Exception as e:
            print(f"⚠ MongoDB not available: {e}")
            print("⚠ Running in demo mode without database")
            self.connected = False
            self.db = None
            
            # Set all collections to None for demo mode
            self.sessions = None
            self.auth_attempts = None
            self.commands = None
            self.downloads = None
            self.stats = None
            self.brute_force_attacks = None
            self.shell_interactions = None
            self.malware_downloads = None
            self.attack_patterns = None
            self.threat_intelligence = None
            self.blocked_ips = None
            self.blocked_users = None
            self.user_activities = None
            self.failed_logins = None
            self.successful_logins = None
            self.web_attacks = None
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        if not self.connected:
            return
        try:
            # Cowrie indexes
            self.sessions.create_index([('timestamp', DESCENDING)])
            self.sessions.create_index([('src_ip', 1)])
            self.auth_attempts.create_index([('timestamp', DESCENDING)])
            self.auth_attempts.create_index([('username', 1)])
            self.commands.create_index([('timestamp', DESCENDING)])
            self.downloads.create_index([('timestamp', DESCENDING)])
            
            # Attack analysis indexes
            self.brute_force_attacks.create_index([('timestamp', DESCENDING)])
            self.brute_force_attacks.create_index([('src_ip', 1)])
            self.shell_interactions.create_index([('timestamp', DESCENDING)])
            self.shell_interactions.create_index([('session_id', 1)])
            self.malware_downloads.create_index([('timestamp', DESCENDING)])
            self.attack_patterns.create_index([('pattern_type', 1)])
            self.threat_intelligence.create_index([('ip_address', 1)])
        except Exception as e:
            print(f"⚠ Error creating indexes: {e}")
    
    def insert_session(self, session_data):
        """Insert a new session"""
        if not self.connected:
            return None
        return self.sessions.insert_one(session_data)
    
    def insert_auth_attempt(self, auth_data):
        """Insert an authentication attempt"""
        if not self.connected:
            return None
        return self.auth_attempts.insert_one(auth_data)
    
    def insert_command(self, command_data):
        """Insert a command execution"""
        if not self.connected:
            return None
        return self.commands.insert_one(command_data)
    
    def insert_download(self, download_data):
        """Insert a file download event"""
        if not self.connected:
            return None
        return self.downloads.insert_one(download_data)
    
    def get_recent_sessions(self, limit=50):
        """Get recent sessions"""
        sessions = self.sessions.find().sort('timestamp', DESCENDING).limit(limit)
        return list(sessions)
    
    def get_recent_auth_attempts(self, limit=100):
        """Get recent authentication attempts"""
        attempts = self.auth_attempts.find().sort('timestamp', DESCENDING).limit(limit)
        return list(attempts)
    
    def get_recent_commands(self, limit=100):
        """Get recent commands"""
        commands = self.commands.find().sort('timestamp', DESCENDING).limit(limit)
        return list(commands)
    
    def get_stats(self):
        """Get overall statistics"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        stats = {
            'total_sessions': self.sessions.count_documents({}),
            'total_auth_attempts': self.auth_attempts.count_documents({}),
            'total_commands': self.commands.count_documents({}),
            'total_downloads': self.downloads.count_documents({}),
            'sessions_24h': self.sessions.count_documents({'timestamp': {'$gte': last_24h}}),
            'auth_attempts_24h': self.auth_attempts.count_documents({'timestamp': {'$gte': last_24h}}),
            'sessions_7d': self.sessions.count_documents({'timestamp': {'$gte': last_7d}}),
            'unique_ips': len(self.sessions.distinct('src_ip')),
            'unique_usernames': len(self.auth_attempts.distinct('username')),
            'success_auth_rate': self._calculate_success_rate(),
        }
        
        return stats
    
    def _calculate_success_rate(self):
        """Calculate authentication success rate"""
        total = self.auth_attempts.count_documents({})
        if total == 0:
            return 0
        successful = self.auth_attempts.count_documents({'success': True})
        return round((successful / total) * 100, 2)
    
    def get_top_attackers(self, limit=10):
        """Get top attacking IPs"""
        pipeline = [
            {'$group': {'_id': '$src_ip', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        result = list(self.sessions.aggregate(pipeline))
        return [{'ip': item['_id'], 'count': item['count']} for item in result]
    
    def get_top_usernames(self, limit=10):
        """Get most common usernames"""
        pipeline = [
            {'$group': {'_id': '$username', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        result = list(self.auth_attempts.aggregate(pipeline))
        return [{'username': item['_id'], 'count': item['count']} for item in result]
    
    def get_top_passwords(self, limit=10):
        """Get most common passwords"""
        pipeline = [
            {'$group': {'_id': '$password', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        result = list(self.auth_attempts.aggregate(pipeline))
        return [{'password': item['_id'], 'count': item['count']} for item in result]
    
    def get_top_commands(self, limit=10):
        """Get most executed commands"""
        pipeline = [
            {'$group': {'_id': '$input', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        result = list(self.commands.aggregate(pipeline))
        return [{'command': item['_id'], 'count': item['count']} for item in result]
    
    def get_attack_timeline(self, days=7):
        """Get attack timeline for the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        pipeline = [
            {'$match': {'timestamp': {'$gte': start_date}}},
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$timestamp'
                        }
                    },
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'_id': 1}}
        ]
        result = list(self.sessions.aggregate(pipeline))
        return [{'date': item['_id'], 'count': item['count']} for item in result]
    
    def get_country_stats(self):
        """Get attacks by country (requires GeoIP data)"""
        pipeline = [
            {'$group': {'_id': '$country', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        result = list(self.sessions.aggregate(pipeline))
        return [{'country': item['_id'] or 'Unknown', 'count': item['count']} for item in result]
    
    def get_most_active_hours(self):
        """Get most active attack hours"""
        pipeline = [
            {
                '$project': {
                    'hour': {'$hour': '$timestamp'}
                }
            },
            {
                '$group': {
                    '_id': '$hour',
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        result = list(self.sessions.aggregate(pipeline))
        return [{'hour': item['_id'], 'count': item['count']} for item in result]
    
    def get_attack_frequency(self):
        """Get attack frequency statistics"""
        total = self.sessions.count_documents({})
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        
        last_hour = self.sessions.count_documents({'timestamp': {'$gte': now - timedelta(hours=1)}})
        last_day = self.sessions.count_documents({'timestamp': {'$gte': now - timedelta(days=1)}})
        last_week = self.sessions.count_documents({'timestamp': {'$gte': now - timedelta(days=7)}})
        
        return {
            'total': total,
            'last_hour': last_hour,
            'last_day': last_day,
            'last_week': last_week,
            'average_per_day': last_week / 7 if last_week > 0 else 0
        }
    
    def get_success_failure_ratio(self):
        """Get authentication success vs failure ratio"""
        total = self.auth_attempts.count_documents({})
        success = self.auth_attempts.count_documents({'success': True})
        failure = total - success
        
        return {
            'total': total,
            'success': success,
            'failure': failure,
            'success_rate': round((success / total * 100), 2) if total > 0 else 0
        }
    
    def get_malicious_ips(self, threshold=10):
        """Get IPs with more than threshold attempts"""
        pipeline = [
            {'$group': {'_id': '$src_ip', 'count': {'$sum': 1}}},
            {'$match': {'count': {'$gte': threshold}}},
            {'$sort': {'count': -1}}
        ]
        result = list(self.sessions.aggregate(pipeline))
        return [{'ip': item['_id'], 'attempts': item['count']} for item in result]
    
    def get_dangerous_commands(self):
        """Get potentially dangerous commands"""
        dangerous_keywords = ['wget', 'curl', 'nc', 'netcat', 'chmod', 'rm -rf', 'dd', 'mkfs']
        dangerous_commands = []
        
        for cmd in self.commands.find().sort('timestamp', -1).limit(1000):
            cmd_input = cmd.get('input', '').lower()
            if any(keyword in cmd_input for keyword in dangerous_keywords):
                dangerous_commands.append(cmd)
        
        return dangerous_commands[:50]
    
    def get_malware_count(self):
        """Get count of malware downloads"""
        return self.downloads.count_documents({})
    
    def search_sessions(self, query):
        """Search sessions by IP or other fields"""
        results = list(self.sessions.find({'src_ip': {'$regex': query, '$options': 'i'}}).limit(50))
        return results
    
    def search_auth_attempts(self, query):
        """Search auth attempts by username or password"""
        results = list(self.auth_attempts.find({
            '$or': [
                {'username': {'$regex': query, '$options': 'i'}},
                {'password': {'$regex': query, '$options': 'i'}}
            ]
        }).limit(50))
        return results
    
    def search_commands(self, query):
        """Search commands by input"""
        results = list(self.commands.find({'input': {'$regex': query, '$options': 'i'}}).limit(50))
        return results
    
    def get_hourly_distribution(self):
        """Get attack distribution by hour"""
        pipeline = [
            {'$project': {'hour': {'$hour': '$timestamp'}}},
            {'$group': {'_id': '$hour', 'count': {'$sum': 1}}},
            {'$sort': {'_id': 1}}
        ]
        result = list(self.sessions.aggregate(pipeline))
        return [{'hour': item['_id'], 'count': item['count']} for item in result]
    
    def get_daily_distribution(self):
        """Get attack distribution by day of week"""
        pipeline = [
            {'$project': {'dayOfWeek': {'$dayOfWeek': '$timestamp'}}},
            {'$group': {'_id': '$dayOfWeek', 'count': {'$sum': 1}}},
            {'$sort': {'_id': 1}}
        ]
        result = list(self.sessions.aggregate(pipeline))
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        return [{'day': days[item['_id'] - 1], 'count': item['count']} for item in result]
    
    def get_protocol_distribution(self):
        """Get distribution by protocol"""
        pipeline = [
            {'$group': {'_id': '$protocol', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        result = list(self.sessions.aggregate(pipeline))
        return [{'protocol': item['_id'], 'count': item['count']} for item in result]
    
    def get_top_credential_combinations(self, limit=20):
        """Get most common username/password combinations"""
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'username': '$username',
                        'password': '$password'
                    },
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        result = list(self.auth_attempts.aggregate(pipeline))
        return [{
            'username': item['_id']['username'],
            'password': item['_id']['password'],
            'count': item['count']
        } for item in result]
    
    def get_success_rate_by_username(self):
        """Get success rate for each username"""
        pipeline = [
            {
                '$group': {
                    '_id': '$username',
                    'total': {'$sum': 1},
                    'success': {
                        '$sum': {'$cond': ['$success', 1, 0]}
                    }
                }
            },
            {'$sort': {'total': -1}},
            {'$limit': 20}
        ]
        result = list(self.auth_attempts.aggregate(pipeline))
        return [{
            'username': item['_id'],
            'total': item['total'],
            'success': item['success'],
            'rate': round((item['success'] / item['total'] * 100), 2) if item['total'] > 0 else 0
        } for item in result]
    
    def categorize_commands(self):
        """Categorize commands into groups"""
        categories = {
            'reconnaissance': ['ls', 'pwd', 'whoami', 'uname', 'cat /etc', 'ps', 'netstat', 'ifconfig'],
            'download': ['wget', 'curl', 'fetch', 'tftp'],
            'execution': ['sh', 'bash', 'python', 'perl', 'ruby', 'chmod +x', './'],
            'persistence': ['crontab', 'systemctl', 'service', 'rc.local'],
            'destruction': ['rm ', 'dd', 'mkfs', '> /dev/'],
            'other': []
        }
        
        command_counts = {'reconnaissance': 0, 'download': 0, 'execution': 0, 'persistence': 0, 'destruction': 0, 'other': 0}
        
        for cmd in self.commands.find():
            cmd_input = cmd.get('input', '').lower()
            categorized = False
            
            for category, keywords in categories.items():
                if category != 'other' and any(keyword in cmd_input for keyword in keywords):
                    command_counts[category] += 1
                    categorized = True
                    break
            
            if not categorized:
                command_counts['other'] += 1
        
        return command_counts
    
    def get_command_sequences(self):
        """Get common command sequences"""
        if not self.connected:
            return []
        pipeline = [
            {'$sort': {'timestamp': 1}},
            {
                '$group': {
                    '_id': '$session_id',
                    'commands': {'$push': '$input'}
                }
            },
            {'$match': {'commands': {'$size': {'$gte': 3}}}},
            {'$limit': 20}
        ]
        result = list(self.commands.aggregate(pipeline))
        return [{'session': item['_id'], 'sequence': item['commands'][:10]} for item in result]
    
    # ==================== BRUTE FORCE ATTACK TRACKING ====================
    
    def log_brute_force_attack(self, attack_data):
        """Log a brute force attack"""
        if not self.connected:
            return None
        
        attack = {
            'src_ip': attack_data.get('src_ip'),
            'target_port': attack_data.get('target_port', 22),
            'protocol': attack_data.get('protocol', 'SSH'),
            'attempts_count': attack_data.get('attempts_count', 0),
            'usernames_tried': attack_data.get('usernames_tried', []),
            'passwords_tried': attack_data.get('passwords_tried', []),
            'success': attack_data.get('success', False),
            'duration': attack_data.get('duration', 0),
            'timestamp': datetime.utcnow(),
            'geolocation': attack_data.get('geolocation', {}),
            'threat_level': attack_data.get('threat_level', 'medium')
        }
        return self.brute_force_attacks.insert_one(attack)
    
    def log_shell_interaction(self, interaction_data):
        """Log shell interaction details"""
        if not self.connected:
            return None
        
        interaction = {
            'session_id': interaction_data.get('session_id'),
            'src_ip': interaction_data.get('src_ip'),
            'username': interaction_data.get('username'),
            'commands_executed': interaction_data.get('commands_executed', []),
            'files_accessed': interaction_data.get('files_accessed', []),
            'files_modified': interaction_data.get('files_modified', []),
            'downloads': interaction_data.get('downloads', []),
            'uploads': interaction_data.get('uploads', []),
            'duration': interaction_data.get('duration', 0),
            'timestamp': datetime.utcnow(),
            'attack_vector': interaction_data.get('attack_vector', 'unknown'),
            'severity': interaction_data.get('severity', 'medium')
        }
        return self.shell_interactions.insert_one(interaction)
    
    def log_malware_download(self, malware_data):
        """Log malware download attempt"""
        if not self.connected:
            return None
        
        malware = {
            'session_id': malware_data.get('session_id'),
            'src_ip': malware_data.get('src_ip'),
            'url': malware_data.get('url'),
            'filename': malware_data.get('filename'),
            'file_size': malware_data.get('file_size', 0),
            'file_hash': malware_data.get('file_hash'),
            'file_type': malware_data.get('file_type'),
            'download_method': malware_data.get('download_method', 'wget'),
            'timestamp': datetime.utcnow(),
            'analyzed': malware_data.get('analyzed', False),
            'threat_score': malware_data.get('threat_score', 0)
        }
        return self.malware_downloads.insert_one(malware)
    
    def log_attack_pattern(self, pattern_data):
        """Log identified attack pattern"""
        if not self.connected:
            return None
        
        pattern = {
            'pattern_type': pattern_data.get('pattern_type'),
            'description': pattern_data.get('description'),
            'indicators': pattern_data.get('indicators', []),
            'src_ips': pattern_data.get('src_ips', []),
            'frequency': pattern_data.get('frequency', 0),
            'first_seen': pattern_data.get('first_seen', datetime.utcnow()),
            'last_seen': datetime.utcnow(),
            'severity': pattern_data.get('severity', 'medium')
        }
        return self.attack_patterns.insert_one(pattern)
    
    # ==================== ADVANCED ANALYTICS ====================
    
    def get_brute_force_stats(self):
        """Get brute force attack statistics"""
        if not self.connected:
            return {
                'total_attacks': 0,
                'successful_attacks': 0,
                'unique_attackers': 0,
                'avg_attempts': 0,
                'most_targeted_ports': []
            }
        
        total = self.brute_force_attacks.count_documents({})
        successful = self.brute_force_attacks.count_documents({'success': True})
        unique_ips = len(self.brute_force_attacks.distinct('src_ip'))
        
        # Average attempts
        pipeline = [{'$group': {'_id': None, 'avg': {'$avg': '$attempts_count'}}}]
        avg_result = list(self.brute_force_attacks.aggregate(pipeline))
        avg_attempts = round(avg_result[0]['avg'], 2) if avg_result else 0
        
        # Most targeted ports
        port_pipeline = [
            {'$group': {'_id': '$target_port', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        port_result = list(self.brute_force_attacks.aggregate(port_pipeline))
        
        return {
            'total_attacks': total,
            'successful_attacks': successful,
            'unique_attackers': unique_ips,
            'avg_attempts': avg_attempts,
            'most_targeted_ports': [{'port': r['_id'], 'count': r['count']} for r in port_result]
        }
    
    def get_shell_interaction_stats(self):
        """Get shell interaction statistics"""
        if not self.connected:
            return {
                'total_sessions': 0,
                'total_commands': 0,
                'avg_duration': 0,
                'files_accessed': 0
            }
        
        total_sessions = self.shell_interactions.count_documents({})
        
        # Total commands
        pipeline = [
            {'$project': {'cmd_count': {'$size': '$commands_executed'}}},
            {'$group': {'_id': None, 'total': {'$sum': '$cmd_count'}}}
        ]
        cmd_result = list(self.shell_interactions.aggregate(pipeline))
        total_commands = cmd_result[0]['total'] if cmd_result else 0
        
        # Average duration
        duration_pipeline = [{'$group': {'_id': None, 'avg': {'$avg': '$duration'}}}]
        dur_result = list(self.shell_interactions.aggregate(duration_pipeline))
        avg_duration = round(dur_result[0]['avg'], 2) if dur_result else 0
        
        # Files accessed
        files_pipeline = [
            {'$project': {'file_count': {'$size': '$files_accessed'}}},
            {'$group': {'_id': None, 'total': {'$sum': '$file_count'}}}
        ]
        files_result = list(self.shell_interactions.aggregate(files_pipeline))
        files_accessed = files_result[0]['total'] if files_result else 0
        
        return {
            'total_sessions': total_sessions,
            'total_commands': total_commands,
            'avg_duration': avg_duration,
            'files_accessed': files_accessed
        }
    
    def get_malware_stats(self):
        """Get malware download statistics"""
        if not self.connected:
            return {
                'total_downloads': 0,
                'unique_malware': 0,
                'total_size': 0,
                'most_common_types': []
            }
        
        total = self.malware_downloads.count_documents({})
        unique = len(self.malware_downloads.distinct('file_hash'))
        
        # Total size
        size_pipeline = [{'$group': {'_id': None, 'total': {'$sum': '$file_size'}}}]
        size_result = list(self.malware_downloads.aggregate(size_pipeline))
        total_size = size_result[0]['total'] if size_result else 0
        
        # Most common types
        type_pipeline = [
            {'$group': {'_id': '$file_type', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        type_result = list(self.malware_downloads.aggregate(type_pipeline))
        
        return {
            'total_downloads': total,
            'unique_malware': unique,
            'total_size': total_size,
            'most_common_types': [{'type': r['_id'], 'count': r['count']} for r in type_result]
        }
    
    def get_attack_heatmap(self, days=7):
        """Get attack heatmap data for visualization"""
        if not self.connected:
            return []
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {'$match': {'timestamp': {'$gte': start_date}}},
            {
                '$group': {
                    '_id': {
                        'hour': {'$hour': '$timestamp'},
                        'day': {'$dayOfWeek': '$timestamp'}
                    },
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'_id.day': 1, '_id.hour': 1}}
        ]
        
        result = list(self.auth_attempts.aggregate(pipeline))
        return [{
            'day': item['_id']['day'],
            'hour': item['_id']['hour'],
            'count': item['count']
        } for item in result]
    
    def get_recent_attacks(self, limit=20):
        """Get most recent attack activities"""
        if not self.connected:
            return []
        
        attacks = []
        
        # Recent brute force
        for attack in self.brute_force_attacks.find().sort('timestamp', DESCENDING).limit(limit):
            attacks.append({
                'type': 'Brute Force',
                'src_ip': attack.get('src_ip'),
                'details': f"{attack.get('attempts_count')} attempts on port {attack.get('target_port')}",
                'timestamp': attack.get('timestamp'),
                'severity': attack.get('threat_level', 'medium')
            })
        
        # Recent shell interactions
        for interaction in self.shell_interactions.find().sort('timestamp', DESCENDING).limit(limit):
            attacks.append({
                'type': 'Shell Interaction',
                'src_ip': interaction.get('src_ip'),
                'details': f"{len(interaction.get('commands_executed', []))} commands executed",
                'timestamp': interaction.get('timestamp'),
                'severity': interaction.get('severity', 'medium')
            })
        
        # Sort by timestamp
        attacks.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        return attacks[:limit]
    
    # ==================== GENERIC DOCUMENT OPERATIONS ====================
    
    def insert_document(self, collection_name, document):
        """Insert a document into any collection"""
        if not self.connected:
            return None
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            print(f"Error inserting document: {e}")
            return None
    
    def find_document(self, collection_name, query):
        """Find a single document"""
        if not self.connected:
            return None
        try:
            collection = self.db[collection_name]
            return collection.find_one(query)
        except Exception as e:
            print(f"Error finding document: {e}")
            return None
    
    def find_documents(self, collection_name, query):
        """Find multiple documents"""
        if not self.connected:
            return []
        try:
            collection = self.db[collection_name]
            return list(collection.find(query))
        except Exception as e:
            print(f"Error finding documents: {e}")
            return []
    
    def update_document(self, collection_name, query, update_data):
        """Update a document"""
        if not self.connected:
            return None
        try:
            collection = self.db[collection_name]
            return collection.update_one(query, {'$set': update_data})
        except Exception as e:
            print(f"Error updating document: {e}")
            return None

