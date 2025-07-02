import sqlite3
from datetime import datetime
import os
from honeyshield.websocket import broadcast_event, socketio
import threading
import time
import logging
import queue

class Database:
    def __init__(self, db_file='instance/honeyshield.db'):
        self.db_file = db_file
        self.lock = threading.Lock()
        self.event_queue = queue.Queue()
        self.running = True  # Initialize running attribute before starting the thread
        self.init_db()
        
        # Start a background thread to process database writes
        self.db_thread = threading.Thread(target=self._process_event_queue, daemon=True)
        self.db_thread.start()

    def get_connection(self):
        """Get a database connection with timeout and retry logic"""
        max_attempts = 5
        attempt = 0
        while attempt < max_attempts:
            try:
                # Set timeout to prevent indefinite waiting
                conn = sqlite3.connect(self.db_file, timeout=20.0)
                # Enable WAL mode for better concurrency
                conn.execute('PRAGMA journal_mode = WAL')
                # Set busy timeout
                conn.execute('PRAGMA busy_timeout = 5000')
                return conn
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    attempt += 1
                    if attempt < max_attempts:
                        logging.warning(f"Database locked, retrying in 1 second (attempt {attempt}/{max_attempts})")
                        time.sleep(1)
                    else:
                        logging.error("Failed to connect to database after multiple attempts: database is locked")
                        raise
                else:
                    logging.error(f"Database connection error: {str(e)}")
                    raise
            except Exception as e:
                logging.error(f"Unexpected database error: {str(e)}")
                raise

    def _process_event_queue(self):
        """Background thread to process database writes"""
        while self.running:
            try:
                # Get an event from the queue with a timeout
                try:
                    event = self.event_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process the event
                try:
                    self._add_event_to_db(event)
                except Exception as e:
                    logging.error(f"Error processing event in queue: {str(e)}")
                finally:
                    self.event_queue.task_done()
            except Exception as e:
                logging.error(f"Error in event queue processing: {str(e)}")
                time.sleep(1)  # Prevent tight loop if there's an error

    def _add_event_to_db(self, event):
        """Actually add the event to the database"""
        try:
            with self.lock:
                conn = self.get_connection()
                c = conn.cursor()
                
                c.execute('''
                    INSERT INTO events (timestamp, event_type, source_ip, details, severity)
                    VALUES (?, ?, ?, ?, ?)
                ''', (event['timestamp'], event['event_type'], event['source_ip'], 
                      event['details'], event['severity']))
                
                conn.commit()
                conn.close()
                
                # Broadcast the new event
                event_data = {
                    'timestamp': event['timestamp'].isoformat(),
                    'service_type': event['event_type'],
                    'ip_address': event['source_ip'],
                    'details': event['details'],
                    'severity': event['severity']
                }
                broadcast_event(event_data)
        except Exception as e:
            logging.error(f"Error adding event to database: {str(e)}")

    def init_db(self):
        try:
            with self.lock:
                conn = self.get_connection()
                c = conn.cursor()
                
                # Create events table
                c.execute('''
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME,
                        event_type TEXT,
                        source_ip TEXT,
                        details TEXT,
                        severity TEXT
                    )
                ''')
                
                # Create alerts table
                c.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id INTEGER,
                        timestamp DATETIME,
                        sent BOOLEAN DEFAULT 0,
                        FOREIGN KEY (event_id) REFERENCES events (id)
                    )
                ''')
                
                # Create blocked_ips table
                c.execute('''
                    CREATE TABLE IF NOT EXISTS blocked_ips (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip_address TEXT NOT NULL,
                        reason TEXT,
                        blocked_until DATETIME,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                conn.close()
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")

    def add_event(self, event_type, source_ip, details, severity='medium'):
        """Queue an event to be added to the database"""
        try:
            timestamp = datetime.now()
            event = {
                'timestamp': timestamp,
                'event_type': event_type,
                'source_ip': source_ip,
                'details': details,
                'severity': severity
            }
            self.event_queue.put(event)
        except Exception as e:
            logging.error(f"Error queuing event: {str(e)}")

    def get_recent_events(self, limit=100):
        try:
            with self.lock:
                conn = self.get_connection()
                c = conn.cursor()
                
                c.execute('''
                    SELECT timestamp, event_type, source_ip, details, severity
                    FROM events
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                events = c.fetchall()
                conn.close()
                return events
        except Exception as e:
            logging.error(f"Error retrieving recent events: {str(e)}")
            return []

    def get_event_stats(self):
        try:
            with self.lock:
                conn = self.get_connection()
                c = conn.cursor()
                
                # Get total events
                c.execute('SELECT COUNT(*) FROM events')
                total_events = c.fetchone()[0]
                
                # Get events by type
                c.execute('''
                    SELECT event_type, COUNT(*) 
                    FROM events 
                    GROUP BY event_type
                ''')
                events_by_type = dict(c.fetchall())
                
                # Get events by severity
                c.execute('''
                    SELECT severity, COUNT(*) 
                    FROM events 
                    GROUP BY severity
                ''')
                events_by_severity = dict(c.fetchall())
                
                # Get unique IPs
                c.execute('SELECT COUNT(DISTINCT source_ip) FROM events')
                unique_ips = c.fetchone()[0]
                
                conn.close()
                
                return {
                    'total_events': total_events,
                    'events_by_type': events_by_type,
                    'events_by_severity': events_by_severity,
                    'unique_ips': unique_ips
                }
        except Exception as e:
            logging.error(f"Error retrieving event stats: {str(e)}")
            return {
                'total_events': 0,
                'events_by_type': {},
                'events_by_severity': {},
                'unique_ips': 0
            }

    def clear_all_records(self):
        """Clear all records from the events table."""
        try:
            with self.lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM events")
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            logging.error(f"Error clearing records: {str(e)}")
            return False

    def get_events_by_time_range(self, start_time):
        """Get events within a specified time range."""
        try:
            with self.lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT timestamp, event_type, source_ip, details, severity
                    FROM events
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (start_time.isoformat(),))
                
                events = []
                for row in cursor.fetchall():
                    events.append({
                        'timestamp': row[0],
                        'service': row[1],
                        'ip': row[2],
                        'details': row[3],
                        'severity': row[4],
                        'port': 'N/A'  # Adding a default port value since it's expected in the export
                    })
                
                conn.close()
                return events
        except Exception as e:
            logging.error(f"Error getting events by time range: {str(e)}")
            return []

    def block_ip(self, ip_address, reason, blocked_until):
        try:
            with self.lock:
                conn = self.get_connection()
                c = conn.cursor()
                c.execute('''
                    INSERT INTO blocked_ips (ip_address, reason, blocked_until)
                    VALUES (?, ?, ?)
                ''', (ip_address, reason, blocked_until))
                conn.commit()
                conn.close()
        except Exception as e:
            logging.error(f"Error blocking IP: {str(e)}")
            raise

    def get_blocked_ips(self):
        try:
            with self.lock:
                conn = self.get_connection()
                c = conn.cursor()
                c.execute('''
                    SELECT ip_address, reason, blocked_until, timestamp
                    FROM blocked_ips
                    ORDER BY blocked_until DESC
                ''')
                rows = c.fetchall()
                conn.close()
                blocked_ips = []
                for row in rows:
                    blocked_ips.append({
                        'ip_address': row[0],
                        'reason': row[1],
                        'blocked_until': row[2],
                        'timestamp': row[3]
                    })
                return blocked_ips
        except Exception as e:
            logging.error(f"Error fetching blocked IPs: {str(e)}")
            return []

    def unblock_ip(self, ip_address):
        try:
            with self.lock:
                conn = self.get_connection()
                c = conn.cursor()
                c.execute('DELETE FROM blocked_ips WHERE ip_address = ?', (ip_address,))
                conn.commit()
                conn.close()
        except Exception as e:
            logging.error(f"Error unblocking IP: {str(e)}")
            raise