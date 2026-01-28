// Dashboard JavaScript
let charts = {};
let refreshInterval;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    updateTime();
    setInterval(updateTime, 1000);
    loadDashboardData();
    startAutoRefresh();
});

// Navigation
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            switchPage(page);
        });
    });
}

function switchPage(page) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-page="${page}"]`).classList.add('active');
    
    // Update page content
    document.querySelectorAll('.page-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${page}-page`).classList.add('active');
    
    // Update header
    const titles = {
        'dashboard': ['Dashboard Overview', 'Real-time honeypot monitoring'],
        'sessions': ['Connection Sessions', 'All SSH/Telnet connection attempts'],
        'auth': ['Authentication Attempts', 'Login attempts and credentials used'],
        'commands': ['Command Execution', 'Commands executed by attackers'],
        'analytics': ['Advanced Analytics', 'Detailed analysis and insights']
    };
    
    document.getElementById('page-title').textContent = titles[page][0];
    document.getElementById('page-subtitle').textContent = titles[page][1];
    
    // Load page-specific data
    loadPageData(page);
}

function loadPageData(page) {
    switch(page) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'sessions':
            loadSessions();
            break;
        case 'auth':
            loadAuthAttempts();
            break;
        case 'commands':
            loadCommands();
            break;
        case 'analytics':
            loadAnalytics();
            break;
    }
}

// Time display
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    const dateString = now.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
    document.getElementById('current-time').textContent = `${dateString} ${timeString}`;
}

// Data loading functions
async function loadDashboardData() {
    try {
        const stats = await fetchAPI('/api/stats');
        updateStats(stats);
        
        const timeline = await fetchAPI('/api/timeline?days=7');
        updateTimelineChart(timeline);
        
        const attackers = await fetchAPI('/api/top-attackers?limit=10');
        updateAttackersChart(attackers);
        
        const usernames = await fetchAPI('/api/top-usernames?limit=10');
        updateTopUsernamesTable(usernames);
        
        const passwords = await fetchAPI('/api/top-passwords?limit=10');
        updateTopPasswordsTable(passwords);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

async function loadSessions() {
    try {
        const sessions = await fetchAPI('/api/sessions?limit=100');
        updateSessionsTable(sessions);
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

async function loadAuthAttempts() {
    try {
        const attempts = await fetchAPI('/api/auth-attempts?limit=100');
        updateAuthTable(attempts);
    } catch (error) {
        console.error('Error loading auth attempts:', error);
    }
}

async function loadCommands() {
    try {
        const commands = await fetchAPI('/api/commands?limit=100');
        updateCommandsTable(commands);
    } catch (error) {
        console.error('Error loading commands:', error);
    }
}

async function loadAnalytics() {
    try {
        const topCommands = await fetchAPI('/api/top-commands?limit=10');
        updateCommandsChart(topCommands);
        
        const stats = await fetchAPI('/api/stats');
        updateAuthRateChart(stats);
        
        const downloads = await fetchAPI('/api/downloads');
        updateDownloadsTable(downloads);
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// API helper
async function fetchAPI(endpoint) {
    const response = await fetch(endpoint);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

// Update functions
function updateStats(stats) {
    document.getElementById('total-sessions').textContent = formatNumber(stats.total_sessions);
    document.getElementById('total-auth').textContent = formatNumber(stats.total_auth_attempts);
    document.getElementById('total-commands').textContent = formatNumber(stats.total_commands);
    document.getElementById('total-downloads').textContent = formatNumber(stats.total_downloads);
    document.getElementById('sessions-24h').textContent = `+${stats.sessions_24h} today`;
    document.getElementById('auth-24h').textContent = `+${stats.auth_attempts_24h} today`;
    document.getElementById('unique-ips').textContent = `${stats.unique_ips} unique IPs`;
    document.getElementById('success-rate').textContent = `${stats.success_auth_rate}% success rate`;
}

function updateTimelineChart(data) {
    const ctx = document.getElementById('timelineChart');
    if (charts.timeline) {
        charts.timeline.destroy();
    }
    
    charts.timeline = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.date),
            datasets: [{
                label: 'Attack Sessions',
                data: data.map(d => d.count),
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                }
            }
        }
    });
}

function updateAttackersChart(data) {
    const ctx = document.getElementById('attackersChart');
    if (charts.attackers) {
        charts.attackers.destroy();
    }
    
    charts.attackers = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.ip),
            datasets: [{
                label: 'Attacks',
                data: data.map(d => d.count),
                backgroundColor: [
                    '#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6',
                    '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                }
            }
        }
    });
}

function updateCommandsChart(data) {
    const ctx = document.getElementById('commandsChart');
    if (charts.commands) {
        charts.commands.destroy();
    }
    
    charts.commands = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.command),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: [
                    '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b',
                    '#10b981', '#06b6d4', '#3b82f6', '#84cc16', '#f97316'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#94a3b8',
                        padding: 15,
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

function updateAuthRateChart(stats) {
    const ctx = document.getElementById('authRateChart');
    if (charts.authRate) {
        charts.authRate.destroy();
    }
    
    const successRate = stats.success_auth_rate;
    const failureRate = 100 - successRate;
    
    charts.authRate = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Failed', 'Success'],
            datasets: [{
                data: [failureRate, successRate],
                backgroundColor: ['#ef4444', '#10b981']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        padding: 20
                    }
                }
            }
        }
    });
}

function updateTopUsernamesTable(data) {
    const tbody = document.querySelector('#top-usernames-table tbody');
    tbody.innerHTML = '';
    
    const max = data[0]?.count || 1;
    
    data.forEach(item => {
        const row = tbody.insertRow();
        const percentage = (item.count / max) * 100;
        row.innerHTML = `
            <td><code>${escapeHtml(item.username)}</code></td>
            <td><strong>${item.count}</strong></td>
            <td>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percentage}%"></div>
                </div>
            </td>
        `;
    });
}

function updateTopPasswordsTable(data) {
    const tbody = document.querySelector('#top-passwords-table tbody');
    tbody.innerHTML = '';
    
    const max = data[0]?.count || 1;
    
    data.forEach(item => {
        const row = tbody.insertRow();
        const percentage = (item.count / max) * 100;
        row.innerHTML = `
            <td><code>${escapeHtml(item.password)}</code></td>
            <td><strong>${item.count}</strong></td>
            <td>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percentage}%"></div>
                </div>
            </td>
        `;
    });
}

function updateSessionsTable(sessions) {
    const tbody = document.querySelector('#sessions-table tbody');
    tbody.innerHTML = '';
    
    sessions.forEach(session => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${formatDateTime(session.timestamp)}</td>
            <td><code>${session.src_ip}</code></td>
            <td>${session.src_port}</td>
            <td><span class="badge badge-info">${session.protocol?.toUpperCase()}</span></td>
            <td><code>${session.session_id?.substring(0, 8)}</code></td>
        `;
    });
}

function updateAuthTable(attempts) {
    const tbody = document.querySelector('#auth-table tbody');
    tbody.innerHTML = '';
    
    attempts.forEach(attempt => {
        const row = tbody.insertRow();
        const statusBadge = attempt.success 
            ? '<span class="badge badge-success">Success</span>'
            : '<span class="badge badge-danger">Failed</span>';
        row.innerHTML = `
            <td>${formatDateTime(attempt.timestamp)}</td>
            <td><code>${attempt.src_ip}</code></td>
            <td><code>${escapeHtml(attempt.username)}</code></td>
            <td><code>${escapeHtml(attempt.password)}</code></td>
            <td>${statusBadge}</td>
        `;
    });
}

function updateCommandsTable(commands) {
    const tbody = document.querySelector('#commands-table tbody');
    tbody.innerHTML = '';
    
    commands.forEach(cmd => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${formatDateTime(cmd.timestamp)}</td>
            <td><code>${cmd.src_ip}</code></td>
            <td><div class="command">${escapeHtml(cmd.input)}</div></td>
            <td><code>${cmd.session_id?.substring(0, 8)}</code></td>
        `;
    });
}

function updateDownloadsTable(downloads) {
    const tbody = document.querySelector('#downloads-table tbody');
    tbody.innerHTML = '';
    
    downloads.forEach(download => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${formatDateTime(download.timestamp)}</td>
            <td><code>${download.src_ip}</code></td>
            <td><a href="${escapeHtml(download.url)}" target="_blank">${escapeHtml(download.url)}</a></td>
            <td><code>${download.shasum?.substring(0, 16)}...</code></td>
        `;
    });
}

// Utility functions
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
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
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

function refreshData() {
    const activePage = document.querySelector('.nav-item.active').dataset.page;
    loadPageData(activePage);
}

function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        const activePage = document.querySelector('.nav-item.active').dataset.page;
        loadPageData(activePage);
    }, 30000); // Refresh every 30 seconds
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}
