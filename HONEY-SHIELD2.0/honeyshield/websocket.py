from flask_socketio import SocketIO, emit
from flask import request
import logging

# Configure SocketIO with ping_timeout and ping_interval to maintain connections
socketio = SocketIO(ping_timeout=60, ping_interval=25, cors_allowed_origins="*")

def broadcast_event(event_data):
    """Broadcast new events to all connected clients"""
    try:
        socketio.emit('new_event', event_data)
    except Exception as e:
        logging.error(f"Error broadcasting event: {str(e)}")

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    try:
        logging.info(f"Client connected: {request.sid}")
        emit('connection_established', {'data': 'Connected to real-time updates'})
    except Exception as e:
        logging.error(f"Error handling connection: {str(e)}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        logging.info(f"Client disconnected: {request.sid}")
    except Exception as e:
        logging.error(f"Error handling disconnection: {str(e)}") 