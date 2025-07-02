from flask import Flask, request, Response
import threading
import logging
from datetime import datetime, timedelta
from honeyshield.database import Database
import time
import os
import hashlib

class HTTP_Honeypot:
    def __init__(self, db, host='0.0.0.0', port=8081):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.db = db
        self.last_events = {}  # key -> last event time (key is a hash of IP + path + method)
        self.rate_limit = 1  # seconds between identical requests (same IP, path, method)
        self.setup_routes()
        
        # Disable Flask's default logging to avoid duplicate logs
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    def setup_routes(self):
        @self.app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'])
        @self.app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'])
        def catch_all(path):
            try:
                # Get request details
                client_ip = request.remote_addr
                method = request.method
                
                # Create a unique key for this request (IP + path + method)
                request_key = f"{client_ip}:{path}:{method}"
                request_hash = hashlib.md5(request_key.encode()).hexdigest()
                
                current_time = time.time()
                
                # Check if this exact request has been made recently
                if request_hash in self.last_events:
                    time_since_last = current_time - self.last_events[request_hash]
                    if time_since_last < self.rate_limit:
                        # Still log the request but don't add to database
                        logging.debug(f"Rate limited request from {client_ip} - {method} {path}")
                        return Response(
                            "Welcome to the server!",
                            status=200,
                            mimetype='text/plain'
                        )
                
                # Update last event time for this request
                self.last_events[request_hash] = current_time
                
                # Clean up old entries in last_events dict (keep it from growing indefinitely)
                self.last_events = {k: v for k, v in self.last_events.items() 
                                   if current_time - v < 3600}  # Remove entries older than 1 hour
                
                # Log the HTTP request
                try:
                    # Truncate details if they're too long to prevent database issues
                    details = f"Method: {method}\nPath: {path}\nHeaders: {dict(request.headers)}"
                    data = request.get_data()
                    if data and len(data) > 1000:
                        details += f"\nData: (truncated) {data[:1000]}..."
                    elif data:
                        details += f"\nData: {data}"
                    
                    # Determine severity based on method and path
                    severity = 'medium'
                    
                    # Higher severity for potentially dangerous methods
                    if method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                        severity = 'high'
                    
                    # Higher severity for suspicious paths
                    suspicious_paths = ['admin', 'login', 'wp-admin', 'phpmyadmin', 'config', 'api', 
                                       'shell', 'cmd', 'exec', 'passwd', 'etc', 'root']
                    if any(sus in path.lower() for sus in suspicious_paths):
                        severity = 'high'
                    
                    # Check for SQL injection attempts
                    sql_injection_patterns = ['select', 'union', 'insert', 'drop', 'update', 'delete from', 
                                             '1=1', 'or 1=1', '--', ';--', '/*', '*/']
                    request_data = str(request.args) + str(data)
                    if any(pattern in request_data.lower() for pattern in sql_injection_patterns):
                        severity = 'critical'
                        
                    self.db.add_event(
                        event_type='HTTP',
                        source_ip=client_ip,
                        details=details,
                        severity=severity
                    )
                    
                    logging.info(f"HTTP {method} request to {path} from {client_ip} (Severity: {severity})")
                except Exception as e:
                    logging.error(f"Error adding event to database: {str(e)}")

                # Return a fake response
                return Response(
                    "Welcome to the server!",
                    status=200,
                    mimetype='text/plain'
                )
            except Exception as e:
                logging.error(f"Exception on {path} [{request.method}]\n{str(e)}")
                return Response("Internal Server Error", status=500)

    def start(self):
        try:
            logging.info(f"HTTP honeypot starting on {self.host}:{self.port}")
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False, threaded=True)
        except Exception as e:
            logging.error(f"Error in HTTP honeypot: {str(e)}")

def start_http_honeypot():
    """Start the HTTP honeypot in a separate thread"""
    try:
        db = Database()
        http_honeypot = HTTP_Honeypot(db)
        http_honeypot.start()
    except Exception as e:
        logging.error(f"Error in HTTP honeypot: {str(e)}")