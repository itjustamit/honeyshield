@echo off
echo Starting HoneyShield Honeypot...
call venv\Scripts\activate
python -m honeyshield.main
pause 