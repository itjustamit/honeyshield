import os
from telegram import Bot
import logging
from datetime import datetime
import asyncio
from flask import current_app

class TelegramAlert:
    def __init__(self, db):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.db = db
        if not self.token or not self.chat_id:
            logging.error("Telegram credentials not found in environment variables")
            return
        self.bot = Bot(token=self.token)

    async def send_alert(self, message):
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            logging.error(f"Error sending Telegram alert: {str(e)}")
            return False

    def process_pending_alerts(self):
        try:
            # Get recent events that haven't been sent as alerts
            events = self.db.get_recent_events(limit=10)
            for event in events:
                timestamp, event_type, source_ip, details, severity = event
                
                message = (
                    f"🚨 <b>Security Alert</b>\n\n"
                    f"Type: {event_type}\n"
                    f"Time: {timestamp}\n"
                    f"IP: {source_ip}\n"
                    f"Severity: {severity}\n"
                    f"Details: {details}"
                )
                
                # Run the async send_alert function
                asyncio.run(self.send_alert(message))
        except Exception as e:
            logging.error(f"Error processing alerts: {str(e)}") 