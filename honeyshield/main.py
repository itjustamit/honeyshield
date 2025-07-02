from honeyshield import app
from honeyshield.websocket import socketio
from honeyshield.ssh_honeypot import start_ssh_honeypot
from honeyshield.http_honeypot import start_http_honeypot
import threading
import logging
import time
from honeyshield.telegram_alert import TelegramAlert
from honeyshield.database import Database
import os
import signal
import sys

# Configure logging
logging.basicConfig(
    filename='honeyshield.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add console handler for better debugging
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Initialize database
db = Database()

# Keep track of running threads
threads = []

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    logging.info("Shutting down HoneyShield...")
    # Cleanup code here if needed
    sys.exit(0)

def start_telegram_alerts():
    try:
        telegram_alert = TelegramAlert(db)
        while True:
            try:
                telegram_alert.process_pending_alerts()
                time.sleep(60)  # Check for new alerts every minute
            except Exception as e:
                logging.error(f"Error processing Telegram alerts: {str(e)}")
                time.sleep(60)  # Wait before retrying
    except Exception as e:
        logging.error(f"Fatal error in Telegram alerts: {str(e)}")

def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logging.info("Starting HoneyShield...")
    
    try:
        # Start SSH honeypot in a separate thread
        ssh_thread = threading.Thread(target=start_ssh_honeypot, daemon=True)
        ssh_thread.start()
        threads.append(ssh_thread)
        logging.info("SSH honeypot started")

        # Start HTTP honeypot in a separate thread
        http_thread = threading.Thread(target=start_http_honeypot, daemon=True)
        http_thread.start()
        threads.append(http_thread)
        logging.info("HTTP honeypot started")

        # Start Telegram alerts in a separate thread
        telegram_thread = threading.Thread(target=start_telegram_alerts, daemon=True)
        telegram_thread.start()
        threads.append(telegram_thread)
        logging.info("Telegram alerts started")

        # Initialize SocketIO with the app
        socketio.init_app(app)
        logging.info("SocketIO initialized")

        # Run the Flask app with SocketIO
        logging.info("Starting web interface on port 5001")
        socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        logging.error(f"Error in main application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 