"""
Security Logger - Creates detailed JSON logs for all honeypot activities
"""
import json
import os
from datetime import datetime
from pathlib import Path
from config import Config

class SecurityLogger:
    def __init__(self, log_dir='./logs/security'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create separate log files for different event types
        self.session_log = self.log_dir / 'sessions.json'
        self.auth_log = self.log_dir / 'auth_attempts.json'
        self.command_log = self.log_dir / 'commands.json'
        self.download_log = self.log_dir / 'downloads.json'
        self.threat_log = self.log_dir / 'threats.json'
        self.analysis_log = self.log_dir / 'analysis.json'
        
    def log_event(self, event_type, data):
        """Log an event with timestamp and severity"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'data': data,
            'severity': self._calculate_severity(event_type, data)
        }
        
        # Choose appropriate log file
        if event_type == 'session':
            log_file = self.session_log
        elif event_type == 'auth':
            log_file = self.auth_log
        elif event_type == 'command':
            log_file = self.command_log
        elif event_type == 'download':
            log_file = self.download_log
        elif event_type == 'threat':
            log_file = self.threat_log
        else:
            log_file = self.analysis_log
        
        # Append to log file
        self._append_log(log_file, log_entry)
        
        # Also create daily summary
        self._update_daily_summary(log_entry)
        
    def _append_log(self, log_file, entry):
        """Append entry to log file"""
        # Read existing logs
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        # Append new entry
        logs.append(entry)
        
        # Keep only last 10000 entries per file
        if len(logs) > 10000:
            logs = logs[-10000:]
        
        # Write back
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _calculate_severity(self, event_type, data):
        """Calculate threat severity (low, medium, high, critical)"""
        severity = 'low'
        
        if event_type == 'download':
            severity = 'critical'  # File downloads are always critical
        elif event_type == 'auth' and data.get('success'):
            severity = 'high'  # Successful auth is high risk
        elif event_type == 'command':
            # Check for dangerous commands
            dangerous_commands = [
                'wget', 'curl', 'nc', 'netcat', 'chmod', 'rm -rf',
                'dd', 'mkfs', 'iptables', 'useradd', 'passwd'
            ]
            cmd = data.get('input', '').lower()
            if any(danger in cmd for danger in dangerous_commands):
                severity = 'high'
            else:
                severity = 'medium'
        elif event_type == 'threat':
            severity = 'critical'
        
        return severity
    
    def _update_daily_summary(self, entry):
        """Update daily summary statistics"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        summary_file = self.log_dir / f'summary_{today}.json'
        
        # Read existing summary
        summary = {
            'date': today,
            'total_events': 0,
            'by_type': {},
            'by_severity': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
            'unique_ips': set(),
            'first_event': None,
            'last_event': None
        }
        
        if summary_file.exists():
            try:
                with open(summary_file, 'r') as f:
                    loaded = json.load(f)
                    summary.update(loaded)
                    summary['unique_ips'] = set(loaded.get('unique_ips', []))
            except:
                pass
        
        # Update summary
        summary['total_events'] += 1
        event_type = entry['event_type']
        summary['by_type'][event_type] = summary['by_type'].get(event_type, 0) + 1
        summary['by_severity'][entry['severity']] += 1
        
        # Track unique IPs
        if 'src_ip' in entry.get('data', {}):
            summary['unique_ips'].add(entry['data']['src_ip'])
        
        # Update timestamps
        if not summary['first_event']:
            summary['first_event'] = entry['timestamp']
        summary['last_event'] = entry['timestamp']
        
        # Convert set to list for JSON
        summary['unique_ips'] = list(summary['unique_ips'])
        
        # Write summary
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def get_recent_logs(self, log_type='all', limit=100):
        """Get recent log entries"""
        logs = []
        
        if log_type == 'all':
            log_files = [
                self.session_log, self.auth_log, self.command_log,
                self.download_log, self.threat_log
            ]
        else:
            log_map = {
                'session': self.session_log,
                'auth': self.auth_log,
                'command': self.command_log,
                'download': self.download_log,
                'threat': self.threat_log
            }
            log_files = [log_map.get(log_type, self.session_log)]
        
        for log_file in log_files:
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        file_logs = json.load(f)
                        logs.extend(file_logs)
                except:
                    pass
        
        # Sort by timestamp and return recent entries
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return logs[:limit]
    
    def get_daily_summary(self, date=None):
        """Get daily summary for a specific date"""
        if date is None:
            date = datetime.utcnow().strftime('%Y-%m-%d')
        
        summary_file = self.log_dir / f'summary_{date}.json'
        
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def create_threat_report(self, start_date=None, end_date=None):
        """Create a comprehensive threat report"""
        logs = self.get_recent_logs('all', limit=10000)
        
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'period': {
                'start': start_date or 'all_time',
                'end': end_date or 'now'
            },
            'statistics': {
                'total_events': len(logs),
                'by_severity': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
                'by_type': {},
                'unique_ips': set(),
                'top_attackers': {},
                'malicious_commands': [],
                'downloaded_files': []
            }
        }
        
        # Analyze logs
        for log in logs:
            severity = log.get('severity', 'low')
            report['statistics']['by_severity'][severity] += 1
            
            event_type = log.get('event_type')
            report['statistics']['by_type'][event_type] = \
                report['statistics']['by_type'].get(event_type, 0) + 1
            
            data = log.get('data', {})
            src_ip = data.get('src_ip')
            if src_ip:
                report['statistics']['unique_ips'].add(src_ip)
                report['statistics']['top_attackers'][src_ip] = \
                    report['statistics']['top_attackers'].get(src_ip, 0) + 1
            
            if event_type == 'command' and severity in ['high', 'critical']:
                report['statistics']['malicious_commands'].append({
                    'command': data.get('input'),
                    'ip': src_ip,
                    'timestamp': log.get('timestamp')
                })
            
            if event_type == 'download':
                report['statistics']['downloaded_files'].append({
                    'url': data.get('url'),
                    'hash': data.get('shasum'),
                    'ip': src_ip,
                    'timestamp': log.get('timestamp')
                })
        
        # Convert sets to lists and sort
        report['statistics']['unique_ips'] = list(report['statistics']['unique_ips'])
        report['statistics']['top_attackers'] = sorted(
            report['statistics']['top_attackers'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Save report
        report_file = self.log_dir.parent / 'analysis' / f'threat_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert for JSON serialization
        report['statistics']['unique_ips'] = list(report['statistics']['unique_ips'])
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


# Global logger instance
security_logger = SecurityLogger()
