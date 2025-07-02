// Connect to WebSocket
const socket = io({
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 20000
});

// Display toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} animate__animated animate__fadeInUp`;
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'danger' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        </div>
        <div class="toast-content">
            <p>${message}</p>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.getElementById('toast-container').appendChild(toast);
    
    // Remove toast after 5 seconds
    setTimeout(() => {
        toast.classList.replace('animate__fadeInUp', 'animate__fadeOutDown');
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}

// Debounce function to limit API calls
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Update counters
function updateCounters() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-attacks').textContent = data.total_events;
            document.getElementById('ssh-attacks').textContent = data.events_by_type.SSH || 0;
            document.getElementById('http-attacks').textContent = data.events_by_type.HTTP || 0;
        })
        .catch(error => console.error('Error fetching stats:', error));
}

// Debounced version of updateCounters
const debouncedUpdateCounters = debounce(updateCounters, 500);

// Set up a controlled polling interval
let statsInterval;

// Handle connection status
socket.on('connect', function() {
    document.getElementById('connection-status').textContent = 'CONNECTED';
    document.getElementById('connection-status').className = 'connection-status connected';
    showToast('Connected to real-time updates', 'success');
    
    // Start polling for stats at a reasonable interval (every 10 seconds)
    if (statsInterval) clearInterval(statsInterval);
    updateCounters(); // Initial update
    statsInterval = setInterval(debouncedUpdateCounters, 10000);
});

socket.on('disconnect', function() {
    document.getElementById('connection-status').textContent = 'DISCONNECTED';
    document.getElementById('connection-status').className = 'connection-status disconnected';
    showToast('Disconnected from real-time updates', 'danger');
    
    // Stop polling when disconnected
    if (statsInterval) clearInterval(statsInterval);
});

socket.on('reconnecting', function(attemptNumber) {
    document.getElementById('connection-status').textContent = 'RECONNECTING...';
    document.getElementById('connection-status').className = 'connection-status warning';
    showToast(`Attempting to reconnect (${attemptNumber}/5)`, 'warning');
});

socket.on('reconnect_failed', function() {
    document.getElementById('connection-status').textContent = 'RECONNECTION FAILED';
    document.getElementById('connection-status').className = 'connection-status disconnected';
    showToast('Failed to reconnect. Please refresh the page.', 'danger');
});

// Handle new event (attack)
socket.on('new_event', function(data) {
    // Update attack counters with debouncing
    debouncedUpdateCounters();
    
    // Add new row to recent attacks table
    const tableBody = document.getElementById('recent-attacks-tbody');
    const newRow = document.createElement('tr');
    newRow.className = 'animate__animated animate__fadeInDown';
    
    const time = new Date(data.timestamp);
    const formattedTime = time.toLocaleTimeString() + ' ' + time.toLocaleDateString();
    
    newRow.innerHTML = `
        <td>${formattedTime}</td>
        <td>${data.ip_address}</td>
        <td>${data.service_type}</td>
        <td>
            <span class="badge badge-${data.severity === 'high' ? 'danger' : data.severity === 'medium' ? 'warning' : 'success'}">
                ${data.severity.toUpperCase()}
            </span>
        </td>
    `;
    
    // Add to the top of the table
    if (tableBody.firstChild) {
        tableBody.insertBefore(newRow, tableBody.firstChild);
    } else {
        tableBody.appendChild(newRow);
    }
    
    // Remove oldest row if more than 10
    if (tableBody.children.length > 10) {
        tableBody.removeChild(tableBody.lastChild);
    }
    
    // Show toast notification
    showToast(`New ${data.service_type} attack detected from ${data.ip_address}`, data.severity === 'high' ? 'danger' : 'warning');
    
    // Check alert rules
    checkAlertRules(data);
});

// Check alert rules for notifications
function checkAlertRules(event) {
    // High Severity Rule
    if (document.getElementById('high-severity-rule').checked && event.severity === 'high') {
        if (document.getElementById('notifications-switch').checked) {
            if (Notification.permission === 'granted') {
                new Notification('High Severity Attack Detected', {
                    body: `${event.service_type} attack from ${event.ip_address}`,
                    icon: '/static/favicon.ico'
                });
            }
        }
    }
    
    // Multiple Attempts Rule implementation would need attack history tracking
    // New IP Rule implementation would need IP history tracking
}

// Modal handling
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    document.body.style.overflow = 'auto';
}

// Export functionality
document.getElementById('export-btn').addEventListener('click', function() {
    openModal('export-modal');
});

document.getElementById('close-export-modal').addEventListener('click', function() {
    closeModal('export-modal');
});

document.getElementById('cancel-export').addEventListener('click', function() {
    closeModal('export-modal');
});

// Export option selection
const exportOptions = document.querySelectorAll('.export-option');
exportOptions.forEach(option => {
    option.addEventListener('click', function() {
        const section = this.closest('.export-section');
        section.querySelectorAll('.export-option').forEach(opt => opt.classList.remove('selected'));
        this.classList.add('selected');
    });
});

// Export confirmation
document.getElementById('confirm-export').addEventListener('click', function() {
    const formatOption = document.querySelector('.export-option[data-format].selected');
    const rangeOption = document.querySelector('.export-option[data-range].selected');
    
    if (!formatOption || !rangeOption) {
        showToast('Please select both a format and time range', 'warning');
        return;
    }
    
    const format = formatOption.dataset.format;
    const range = rangeOption.dataset.range;
    
    // Perform export
    fetch(`/api/export?format=${format}&range=${range}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Export failed');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `honeyshield-export-${new Date().toISOString().split('T')[0]}.${format}`;
            a.click();
            window.URL.revokeObjectURL(url);
            
            closeModal('export-modal');
            showToast('Data exported successfully', 'success');
        })
        .catch(error => {
            console.error('Export error:', error);
            showToast('Failed to export data', 'danger');
        });
});

// Settings functionality
document.getElementById('settings-btn').addEventListener('click', function() {
    loadSettings();
    openModal('settings-modal');
});

document.getElementById('close-settings-modal').addEventListener('click', function() {
    closeModal('settings-modal');
});

document.getElementById('cancel-settings').addEventListener('click', function() {
    closeModal('settings-modal');
});

// Auto block options toggle
document.getElementById('auto-block-switch').addEventListener('change', function() {
    const options = document.getElementById('auto-block-options');
    options.style.display = this.checked ? 'block' : 'none';
});

// Range sliders in settings
document.getElementById('failed-attempts').addEventListener('input', function() {
    document.getElementById('failed-attempts-value').textContent = `${this.value} attempts`;
});

document.getElementById('auto-duration').addEventListener('input', function() {
    document.getElementById('auto-duration-value').textContent = `${this.value} hours`;
});

// Load settings
function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('honeyshieldSettings') || '{}');
    
    // Auto block settings
    document.getElementById('auto-block-switch').checked = settings.autoBlock || false;
    document.getElementById('auto-block-options').style.display = settings.autoBlock ? 'block' : 'none';
    document.getElementById('failed-attempts').value = settings.failedAttempts || 5;
    document.getElementById('failed-attempts-value').textContent = `${settings.failedAttempts || 5} attempts`;
    document.getElementById('auto-duration').value = settings.autoDuration || 24;
    document.getElementById('auto-duration-value').textContent = `${settings.autoDuration || 24} hours`;
    
    // Attack history settings
    document.getElementById('attack-history-switch').checked = settings.showHistory || false;
    
    // Notifications settings
    document.getElementById('notifications-switch').checked = settings.enableNotifications || false;
    
    // Alert rules
    document.getElementById('high-severity-rule').checked = settings.highSeverityRule !== false;
    document.getElementById('multiple-attempts-rule').checked = settings.multipleAttemptsRule !== false;
    document.getElementById('new-ip-rule').checked = settings.newIpRule !== false;
}

// Save settings
document.getElementById('save-settings').addEventListener('click', function() {
    const settings = {
        autoBlock: document.getElementById('auto-block-switch').checked,
        failedAttempts: parseInt(document.getElementById('failed-attempts').value),
        autoDuration: parseInt(document.getElementById('auto-duration').value),
        showHistory: document.getElementById('attack-history-switch').checked,
        enableNotifications: document.getElementById('notifications-switch').checked,
        highSeverityRule: document.getElementById('high-severity-rule').checked,
        multipleAttemptsRule: document.getElementById('multiple-attempts-rule').checked,
        newIpRule: document.getElementById('new-ip-rule').checked
    };
    
    localStorage.setItem('honeyshieldSettings', JSON.stringify(settings));
    
    // Request desktop notification permission if enabled
    if (settings.enableNotifications && Notification.permission !== 'granted') {
        Notification.requestPermission();
    }
    
    // Save settings to server
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Settings saved successfully', 'success');
            closeModal('settings-modal');
        } else {
            showToast('Failed to save settings: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        console.error('Settings error:', error);
        showToast('Failed to save settings', 'danger');
    });
});

// Block IP functionality
document.getElementById('block-ip-btn').addEventListener('click', function() {
    openModal('block-ip-modal');
});

document.getElementById('close-block-ip-modal').addEventListener('click', function() {
    closeModal('block-ip-modal');
});

document.getElementById('cancel-block-ip').addEventListener('click', function() {
    closeModal('block-ip-modal');
});

// Custom reason toggle
document.getElementById('block-reason-modal').addEventListener('change', function() {
    const customReason = document.getElementById('custom-reason');
    customReason.style.display = this.value === 'other' ? 'block' : 'none';
});

// Block duration slider in modal
document.getElementById('block-duration-modal').addEventListener('input', function() {
    document.getElementById('block-duration-modal-value').textContent = `${this.value} hours`;
});

// Confirm block IP
document.getElementById('confirm-block-ip').addEventListener('click', function() {
    const ipAddress = document.getElementById('ip-address-input-modal').value;
    let reason = document.getElementById('block-reason-modal').value;
    const duration = parseInt(document.getElementById('block-duration-modal').value);
    
    // Get custom reason if selected
    if (reason === 'other') {
        const customReason = document.getElementById('custom-reason').value;
        if (customReason.trim()) {
            reason = customReason.trim();
        } else {
            showToast('Please specify a reason', 'warning');
            return;
        }
    }
    
    // Validate IP address
    if (!ipAddress || !ipAddress.match(/^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/)) {
        showToast('Please enter a valid IP address', 'warning');
        return;
    }
    
    // Block IP
    blockIP(ipAddress, reason, duration);
});

// Block IP function
function blockIP(ipAddress, reason, duration) {
    fetch('/api/block-ip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            ip_address: ipAddress,
            reason: reason,
            duration: duration
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(`IP ${ipAddress} blocked successfully`, 'success');
            closeModal('block-ip-modal');
            
            // Reset form fields
            document.getElementById('ip-address-input-modal').value = '';
            document.getElementById('block-reason-modal').value = 'Suspicious Activity';
            document.getElementById('custom-reason').style.display = 'none';
            document.getElementById('custom-reason').value = '';
            document.getElementById('block-duration-modal').value = 24;
            document.getElementById('block-duration-modal-value').textContent = '24 hours';
            
            // Refresh blocked IPs table
            getBlockedIPs();
        } else {
            showToast(`Failed to block IP: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        showToast('Error blocking IP', 'danger');
        console.error('Error:', error);
    });
}

// Get list of blocked IPs
function getBlockedIPs() {
    fetch('/api/blocked-ips')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('blocked-ips-tbody');
            
            if (data.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="4">
                            <div class="no-data">
                                <i class="fas fa-unlock"></i>
                                <h3>No blocked IPs</h3>
                                <p>Use the Block IP button to manually block suspicious IP addresses.</p>
                            </div>
                        </td>
                    </tr>
                `;
                return;
            }
            
            tableBody.innerHTML = '';
            
            data.forEach(ip => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${ip.ip_address}</td>
                    <td>${ip.reason}</td>
                    <td>${new Date(ip.blocked_until).toLocaleString()}</td>
                    <td>
                        <button class="btn btn-sm btn-danger unblock-ip" data-ip="${ip.ip_address}">
                            <i class="fas fa-unlock"></i> Unblock
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
            
            // Add event listeners to unblock buttons
            document.querySelectorAll('.unblock-ip').forEach(button => {
                button.addEventListener('click', function() {
                    const ip = this.getAttribute('data-ip');
                    unblockIP(ip);
                });
            });
        })
        .catch(error => console.error('Error fetching blocked IPs:', error));
}

// Unblock an IP
function unblockIP(ip) {
    fetch(`/api/unblock-ip/${ip}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(`IP ${ip} unblocked successfully`, 'success');
            getBlockedIPs();
        } else {
            showToast(`Failed to unblock IP: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        showToast('Error unblocking IP', 'danger');
        console.error('Error:', error);
    });
}

// Clear all records
document.getElementById('clear-records-btn').addEventListener('click', function() {
    if (confirm('Are you sure you want to clear all records? This action cannot be undone.')) {
        fetch('/api/clear-records', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('All records cleared successfully', 'success');
                // Refresh the page to reflect changes
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showToast(`Failed to clear records: ${data.error}`, 'danger');
            }
        })
        .catch(error => {
            showToast('Error clearing records', 'danger');
            console.error('Error:', error);
        });
    }
});

// Alert Rules
document.getElementById('high-severity-rule').addEventListener('change', function() {
    saveAlertRules();
});

document.getElementById('multiple-attempts-rule').addEventListener('change', function() {
    saveAlertRules();
});

document.getElementById('new-ip-rule').addEventListener('change', function() {
    saveAlertRules();
});

function saveAlertRules() {
    const settings = JSON.parse(localStorage.getItem('honeyshieldSettings') || '{}');
    
    settings.highSeverityRule = document.getElementById('high-severity-rule').checked;
    settings.multipleAttemptsRule = document.getElementById('multiple-attempts-rule').checked;
    settings.newIpRule = document.getElementById('new-ip-rule').checked;
    
    localStorage.setItem('honeyshieldSettings', JSON.stringify(settings));
}

// Theme toggle functionality
document.getElementById('theme-toggle').addEventListener('click', function() {
    const body = document.body;
    body.classList.toggle('day-mode');
    
    // Save preference to localStorage
    const settings = JSON.parse(localStorage.getItem('honeyshieldSettings') || '{}');
    settings.dayMode = body.classList.contains('day-mode');
    localStorage.setItem('honeyshieldSettings', JSON.stringify(settings));
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    updateCounters();
    getBlockedIPs();
    
    // Load settings from localStorage
    const settings = JSON.parse(localStorage.getItem('honeyshieldSettings') || '{}');
    
    // Apply theme setting
    if (settings.dayMode) {
        document.body.classList.add('day-mode');
    }
    
    // Set alert rules from saved settings
    document.getElementById('high-severity-rule').checked = settings.highSeverityRule !== false;
    document.getElementById('multiple-attempts-rule').checked = settings.multipleAttemptsRule !== false;
    document.getElementById('new-ip-rule').checked = settings.newIpRule !== false;
    
    // Request notification permission if enabled
    if (settings.enableNotifications && Notification.permission !== 'granted') {
        Notification.requestPermission();
    }
});