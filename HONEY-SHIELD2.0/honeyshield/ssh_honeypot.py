import paramiko
import threading
import logging
import socket
from datetime import datetime
from honeyshield.database import Database

class SSHServer(paramiko.ServerInterface):
    def __init__(self, db):
        self.event = threading.Event()
        self.db = db
        self.client_address = None

    def check_auth_password(self, username, password):
        # Log the authentication attempt
        if self.client_address:
            self.db.add_event(
                event_type='SSH',
                source_ip=self.client_address[0],
                details=f"Authentication attempt with username: {username}",
                severity='high'
            )
        else:
            logging.error("Client address not set in SSH server")

        # Always return AUTH_FAILED to reject the connection
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return 'password'

class SSH_Honeypot:
    def __init__(self, db, host='0.0.0.0', port=2222):
        self.host = host
        self.port = port
        self.host_key = paramiko.RSAKey.generate(2048)
        self.db = db

    def start(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(5)
            logging.info(f"SSH Honeypot listening on {self.host}:{self.port}")

            while True:
                try:
                    client, addr = sock.accept()
                    logging.info(f"SSH connection from {addr[0]}:{addr[1]}")
                    
                    # Create a new thread for each connection
                    t = threading.Thread(target=self.handle_client, args=(client, addr))
                    t.daemon = True
                    t.start()
                except Exception as e:
                    logging.error(f"Error accepting SSH connection: {str(e)}")
                    continue

        except Exception as e:
            logging.error(f"Error in SSH honeypot: {str(e)}")

    def handle_client(self, client, addr):
        try:
            transport = paramiko.Transport(client)
            transport.add_server_key(self.host_key)
            
            server = SSHServer(self.db)
            server.client_address = addr
            
            transport.start_server(server=server)
            channel = transport.accept(20)
            
            if channel is None:
                logging.error("Failed to get channel")
                return
                
            while transport.is_active():
                transport.join()
                
        except Exception as e:
            logging.error(f"Error handling SSH client: {str(e)}")
        finally:
            transport.close()

def start_ssh_honeypot():
    """Start the SSH honeypot in a separate thread"""
    try:
        db = Database()
        ssh_honeypot = SSH_Honeypot(db)
        ssh_honeypot.start()
    except Exception as e:
        logging.error(f"Error in SSH honeypot: {str(e)}") 