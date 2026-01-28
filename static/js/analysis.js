// Analysis Page JavaScript
let charts = {};

document.addEventListener('DOMContentLoaded', function() {
    loadAnalysisData();
    setInterval(refreshAnalysis, 60000); // Refresh every minute
});

async function loadAnalysisData() {
    try {
        // Load all analysis data
        const [patterns, credentials, commands, threatReport] = await Promise.all([
            fetchAPI('/api/analysis/attack-patterns'),
            fetchAPI('/api/analysis/credentials'),
            fetchAPI('/api/analysis/commands'),
            fetchAPI('/api/analysis/threat-report')
        ]);

        updateThreatSummary(threatReport);
        updateHourlyChart(patterns.hourly_distribution);
        updateDailyChart(patterns.daily_distribution);
        updateCategoriesChart(commands.command_categories);
        updateProtocolChart(patterns.protocol_distribution);
        updateCredentialsTable(credentials.top_combinations);
        updateDangerousCommands(commands.dangerous_commands);
        updateMaliciousIPs(threatReport.statistics.top_attackers);
    } catch (error) {
        console.error('Error loading analysis data:', error);
    }
}

async function fetchAPI(endpoint) {
    const response = await fetch(endpoint);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
}

function updateThreatSummary(report) {
    const stats = report.statistics;
    
    // Calculate threat level
    const criticalCount = stats.by_severity.critical || 0;
    const highCount = stats.by_severity.high || 0;
    
    let threatLevel = 'LOW';
    if (criticalCount > 10) threatLevel = 'CRITICAL';
    else if (criticalCount > 5 || highCount > 20) threatLevel = 'HIGH';
    else if (highCount > 10) threatLevel = 'MEDIUM';
    
    document.getElementById('threat-level').textContent = threatLevel;
    document.getElementById('malware-count').textContent = stats.downloaded_files?.length || 0;
    document.getElementById('unique-countries').textContent = stats.unique_ips?.length || 0;
    document.getElementById('blocked-attacks').textContent = stats.total_events || 0;
}

function updateHourlyChart(data) {
    const ctx = document.getElementById('hourlyChart');
    if (charts.hourly) charts.hourly.destroy();
    
    // Ensure we have data for all 24 hours
    const hourlyData = Array(24).fill(0);
    data.forEach(item => {
        hourlyData[item.hour] = item.count;
    });
    
    charts.hourly = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({length: 24}, (_, i) => `${i}:00`),
            datasets: [{
                label: 'Attacks by Hour',
                data: hourlyData,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
            }
        }
    });
}

function updateDailyChart(data) {
    const ctx = document.getElementById('dailyChart');
    if (charts.daily) charts.daily.destroy();
    
    charts.daily = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.day),
            datasets: [{
                label: 'Attacks by Day',
                data: data.map(d => d.count),
                backgroundColor: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4']
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
            }
        }
    });
}

function updateCategoriesChart(categories) {
    const ctx = document.getElementById('categoriesChart');
    if (charts.categories) charts.categories.destroy();
    
    const labels = Object.keys(categories);
    const values = Object.values(categories);
    
    charts.categories = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
            datasets: [{
                data: values,
                backgroundColor: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'right', labels: { color: '#94a3b8', padding: 15 } }
            }
        }
    });
}

function updateProtocolChart(data) {
    const ctx = document.getElementById('protocolChart');
    if (charts.protocol) charts.protocol.destroy();
    
    charts.protocol = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(d => (d.protocol || 'Unknown').toUpperCase()),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 20 } }
            }
        }
    });
}

function updateCredentialsTable(credentials) {
    const tbody = document.querySelector('#credentials-table tbody');
    tbody.innerHTML = '';
    
    const max = credentials[0]?.count || 1;
    
    credentials.slice(0, 20).forEach((cred, index) => {
        const row = tbody.insertRow();
        const percentage = (cred.count / max) * 100;
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><code>${escapeHtml(cred.username)}</code></td>
            <td><code>${escapeHtml(cred.password)}</code></td>
            <td><strong>${cred.count}</strong></td>
            <td>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percentage}%"></div>
                </div>
            </td>
        `;
    });
}

function updateDangerousCommands(commands) {
    const tbody = document.querySelector('#dangerous-commands-table tbody');
    tbody.innerHTML = '';
    
    commands.forEach(cmd => {
        const row = tbody.insertRow();
        const severity = determineSeverity(cmd.input);
        row.innerHTML = `
            <td>${formatDateTime(cmd.timestamp)}</td>
            <td><code>${cmd.src_ip}</code></td>
            <td><div class="command">${escapeHtml(cmd.input)}</div></td>
            <td><span class="badge badge-${severity.level}">${severity.label}</span></td>
            <td><code>${cmd.session_id?.substring(0, 8)}</code></td>
        `;
    });
}

function updateMaliciousIPs(attackers) {
    const tbody = document.querySelector('#malicious-ips-table tbody');
    tbody.innerHTML = '';
    
    attackers.forEach((attacker, index) => {
        const row = tbody.insertRow();
        const [ip, attempts] = attacker;
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><code>${ip}</code></td>
            <td><strong>${attempts}</strong></td>
            <td>-</td>
            <td>-</td>
            <td><button class="btn-secondary" onclick="blockIP('${ip}')">Block</button></td>
        `;
    });
}

function determineSeverity(command) {
    const critical = ['rm -rf', 'dd if=', 'mkfs', '> /dev/sd'];
    const high = ['wget', 'curl', 'nc ', 'netcat', 'chmod +x'];
    const medium = ['cat /etc', 'useradd', 'passwd'];
    
    const cmdLower = command.toLowerCase();
    
    if (critical.some(c => cmdLower.includes(c))) return { level: 'danger', label: 'CRITICAL' };
    if (high.some(c => cmdLower.includes(c))) return { level: 'warning', label: 'HIGH' };
    if (medium.some(c => cmdLower.includes(c))) return { level: 'info', label: 'MEDIUM' };
    return { level: 'success', label: 'LOW' };
}

function formatDateTime(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
}

function escapeHtml(text) {
    if (!text) return '';
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

function refreshAnalysis() {
    loadAnalysisData();
}

async function generateReport() {
    try {
        const response = await fetch('/api/analysis/threat-report');
        const report = await response.json();
        
        const dataStr = JSON.stringify(report, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `threat_report_${new Date().toISOString()}.json`;
        a.click();
        
        alert('Threat report generated successfully!');
    } catch (error) {
        console.error('Error generating report:', error);
        alert('Error generating report. Please try again.');
    }
}

function blockIP(ip) {
    alert(`Block IP functionality would be implemented here for: ${ip}`);
}
