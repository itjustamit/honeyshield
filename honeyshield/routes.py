from flask import render_template, jsonify, request, send_file
from honeyshield import app, db
from honeyshield.database import Database
from datetime import datetime, timedelta
from honeyshield.websocket import socketio
from flask_socketio import emit
import json
import csv
from io import StringIO, BytesIO
import os

db = Database()

def broadcast_event(event_data):
    """Broadcast new events to all connected clients"""
    socketio.emit('new_event', event_data)

@app.route('/')
def dashboard():
    # Get recent events
    recent_events = db.get_recent_events(limit=10)
    
    # Get event statistics
    stats = db.get_event_stats()
    
    # Process events for display
    recent_attacks = []
    for event in recent_events:
        # Convert string timestamp to datetime object
        timestamp = datetime.strptime(event[0], '%Y-%m-%d %H:%M:%S.%f') if isinstance(event[0], str) else event[0]
        recent_attacks.append({
            'timestamp': timestamp,
            'ip_address': event[2],
            'service_type': event[1],
            'details': event[3],
            'severity': event[4]
        })
    
    # Get recent alerts (using the same events as alerts for now)
    recent_alerts = []
    for event in recent_events:
        timestamp = datetime.strptime(event[0], '%Y-%m-%d %H:%M:%S.%f') if isinstance(event[0], str) else event[0]
        alert_type = "High Severity Alert" if event[4] == 'high' else "Activity Alert"
        recent_alerts.append({
            'timestamp': timestamp,
            'alert_type': alert_type,
            'message': f"{event[1]} attack detected from {event[2]}: {event[3]}"
        })
    
    return render_template('dashboard.html',
                         recent_attacks=recent_attacks,
                         recent_alerts=recent_alerts,
                         total_attacks=stats['total_events'],
                         ssh_attacks=stats['events_by_type'].get('SSH', 0),
                         http_attacks=stats['events_by_type'].get('HTTP', 0),
                         unique_ips=stats['unique_ips'])

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connection_established', {'data': 'Connected to real-time updates'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@app.route('/api/attacks')
def get_attacks():
    events = db.get_recent_events()
    return jsonify([{
        'timestamp': datetime.strptime(event[0], '%Y-%m-%d %H:%M:%S.%f').isoformat() if isinstance(event[0], str) else event[0].isoformat(),
        'ip_address': event[2],
        'service_type': event[1],
        'details': event[3],
        'severity': event[4]
    } for event in events])

@app.route('/api/stats')
def get_stats():
    return jsonify(db.get_event_stats())

@app.route('/api/alerts')
def get_alerts():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
    return jsonify([{
        'id': alert.id,
        'timestamp': alert.timestamp.isoformat(),
        'type': alert.alert_type,
        'message': alert.message,
        'sent': alert.sent
    } for alert in alerts])

@app.route('/api/block-ip', methods=['POST'])
def block_ip():
    data = request.get_json()
    ip_address = data.get('ip_address')
    reason = data.get('reason')
    duration_hours = data.get('duration', 24)
    expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
    if not ip_address:
        return jsonify({'success': False, 'error': 'IP address is required'}), 400
    try:
        db.block_ip(ip_address, reason, expires_at)
        return jsonify({'success': True, 'message': f'IP {ip_address} blocked successfully for {duration_hours} hours'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to block IP: {str(e)}'}), 500

@app.route('/api/unblock-ip/<ip_address>', methods=['DELETE'])
def unblock_ip(ip_address):
    try:
        db.unblock_ip(ip_address)
        return jsonify({'success': True, 'message': f'IP {ip_address} unblocked successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to unblock IP: {str(e)}'}), 500

@app.route('/api/clear-records', methods=['POST'])
def clear_records():
    try:
        database = Database()
        database.clear_all_records()
        return jsonify({"success": True, "message": "All records cleared successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    try:
        data = request.get_json()
        # Ensure the honeyshield directory exists
        os.makedirs('honeyshield', exist_ok=True)
        with open('honeyshield/config.json', 'w') as f:
            json.dump(data, f)
        return jsonify({"success": True, "message": "Settings updated successfully"})
    except Exception as e:
        print("Settings save error:", e)  # Log the error for debugging
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        # Read settings from the database or config file
        try:
            with open('honeyshield/config.json', 'r') as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {
                "autoBlock": False,
                "failedAttempts": 5,
                "autoDuration": 24,
                "showHistory": False,
                "enableExport": False,
                "exportFormat": "csv"
            }
            
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export')
def export_data():
    try:
        format_type = request.args.get('format', 'csv')
        time_range = request.args.get('range', '24h')
        
        # Calculate time range
        now = datetime.utcnow()
        if time_range == '24h':
            start_time = now - timedelta(hours=24)
        elif time_range == '7d':
            start_time = now - timedelta(days=7)
        elif time_range == '30d':
            start_time = now - timedelta(days=30)
        else:  # all time
            start_time = datetime.min

        # Get events from database
        events = db.get_events_by_time_range(start_time)
        
        if format_type == 'csv':
            # Create CSV
            si = StringIO()
            writer = csv.writer(si)
            writer.writerow(['Timestamp', 'Service', 'IP', 'Details', 'Severity', 'Port'])
            
            for event in events:
                writer.writerow([
                    event['timestamp'],
                    event['service'],
                    event['ip'],
                    event['details'],
                    event['severity'],
                    event['port']
                ])
            
            output = si.getvalue()
            si.close()
            
            # Convert string output to bytes for BytesIO
            bytes_output = output.encode('utf-8')
            bytes_io = BytesIO(bytes_output)
            
            return send_file(
                bytes_io,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'honeyshield-export-{datetime.now().strftime("%Y%m%d")}.csv'
            )
            
        elif format_type == 'json':
            # Create JSON
            output = json.dumps(events, indent=2)
            
            # Convert string output to bytes for BytesIO
            bytes_output = output.encode('utf-8')
            bytes_io = BytesIO(bytes_output)
            
            return send_file(
                bytes_io,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'honeyshield-export-{datetime.now().strftime("%Y%m%d")}.json'
            )
            
        elif format_type == 'raw':
            # Create RAW format (minimal formatting, one event per line)
            output = ""
            for event in events:
                output += f"{event['timestamp']}|{event['service']}|{event['ip']}|{event['port']}|{event['severity']}|{event['details']}\n"
            
            # Convert string output to bytes for BytesIO
            bytes_output = output.encode('utf-8')
            bytes_io = BytesIO(bytes_output)
            
            return send_file(
                bytes_io,
                mimetype='text/plain',
                as_attachment=True,
                download_name=f'honeyshield-export-{datetime.now().strftime("%Y%m%d")}.raw'
            )
            
        else:  # txt
            # Create plain text
            output = ""
            for event in events:
                output += f"Timestamp: {event['timestamp']}\n"
                output += f"Service: {event['service']}\n"
                output += f"IP: {event['ip']}\n"
                output += f"Port: {event['port']}\n"
                output += f"Details: {event['details']}\n"
                output += f"Severity: {event['severity']}\n"
                output += "-------------------\n"
            
            # Convert string output to bytes for BytesIO
            bytes_output = output.encode('utf-8')
            bytes_io = BytesIO(bytes_output)
            
            return send_file(
                bytes_io,
                mimetype='text/plain',
                as_attachment=True,
                download_name=f'honeyshield-export-{datetime.now().strftime("%Y%m%d")}.txt'
            )
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blocked-ips')
def get_blocked_ips():
    try:
        blocked_ips = db.get_blocked_ips()
        return jsonify(blocked_ips)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 