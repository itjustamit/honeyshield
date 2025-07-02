from datetime import datetime
from honeyshield import db

class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    service_type = db.Column(db.String(10), nullable=False)  # SSH or HTTP
    attack_vector = db.Column(db.String(100))
    credentials_attempted = db.Column(db.String(500))
    payload = db.Column(db.Text)
    status = db.Column(db.String(20))  # Blocked, Logged, etc.

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    attack_id = db.Column(db.Integer, db.ForeignKey('attack.id'))
    alert_type = db.Column(db.String(50))
    message = db.Column(db.Text)
    sent = db.Column(db.Boolean, default=False)

class BlockedIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(200))
    expires_at = db.Column(db.DateTime) 