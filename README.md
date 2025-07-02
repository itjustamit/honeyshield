# HoneyShield - Advanced Honeypot for Cyber Threat Detection

HoneyShield is an advanced honeypot system designed to lure, detect, and analyze cyber threats in real-time. It simulates vulnerable services to attract attackers and provides detailed monitoring and alerting capabilities.

## Features

- High-interaction SSH and HTTP honeypots
- Real-time attack monitoring and logging with WebSocket support
- Web-based dashboard with live updates
- Telegram alerts for instant notifications
- IP blocking capabilities
- Detailed attack analytics
- SQLite database for persistent storage
- Real-time event broadcasting
- Connection status monitoring
- Toast notifications for new attacks

## Requirements

- Python 3.8 or higher
- Windows 10/11 or Linux/Unix-based system
- Administrator privileges (for port binding)
- Git (for cloning the repository)
- Minimum 500MB free disk space
- RAM: 512MB minimum, 1GB recommended

## Pre-Installation

### Installing Git

On Windows:
1. Download Git from [Git's official website](https://git-scm.com/download/win)
2. Run the installer
3. Choose default options (or customize if needed)

On Linux/Unix:
```bash
# Debian/Ubuntu
sudo apt-get install git

# RHEL/CentOS
sudo yum install git

# Fedora
sudo dnf install git
```

### Installing Python

1. Install Python 3.8 or higher:
   - Download from [Python's official website](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Open Command Prompt as Administrator

2. Clone the repository:
```bash
git clone https://github.com/yourusername/honeyshield.git
cd honeyshield
```

3. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure Windows Firewall:
   - Open Windows Defender Firewall with Advanced Security
   - Click "Inbound Rules" → "New Rule"
   - Add rules for ports 2222, 8081, and 5001
   - Allow TCP connections for these ports

6. Set up environment variables:
   a. Create a Telegram bot:
      - Open Telegram and search for "@BotFather"
      - Send `/newbot` command
      - Follow the instructions to create your bot
      - Save the bot token provided by BotFather

   b. Get your Telegram chat ID:
      - Send a message to your bot
      - Visit: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
      - Find your chat ID in the response

   c. Create a `.env` file in the project root:
   ```bash
   type nul > .env
   ```

   d. Add your credentials to the `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

## Installation

### Windows Installation

1. Install Python 3.8 or higher:
   - Download from [Python's official website](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Open Command Prompt as Administrator

2. Clone the repository:
```bash
git clone https://github.com/yourusername/honeyshield.git
cd honeyshield
```

3. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure Windows Firewall:
   - Open Windows Defender Firewall with Advanced Security
   - Click "Inbound Rules" → "New Rule"
   - Add rules for ports 2222, 8081, and 5001
   - Allow TCP connections for these ports

6. Set up environment variables:
   a. Create a Telegram bot:
      - Open Telegram and search for "@BotFather"
      - Send `/newbot` command
      - Follow the instructions to create your bot
      - Save the bot token provided by BotFather

   b. Get your Telegram chat ID:
      - Send a message to your bot
      - Visit: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
      - Find your chat ID in the response

   c. Create a `.env` file in the project root:
   ```bash
   type nul > .env
   ```

   d. Add your credentials to the `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

### Linux/Unix Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/honeyshield.git
cd honeyshield
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   a. Create a Telegram bot:
      - Open Telegram and search for "@BotFather"
      - Send `/newbot` command
      - Follow the instructions to create your bot
      - Save the bot token provided by BotFather

   b. Get your Telegram chat ID:
      - Send a message to your bot
      - Visit: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
      - Find your chat ID in the response

   c. Create a `.env` file in the project root:
   ```bash
   touch .env
   ```

   d. Add your credentials to the `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

## Usage

1. Start the honeypot:

Method 1 - Using shortcut files (Recommended):
```bash
# On Windows:
# Double-click run_honeyshield.bat

# On Linux/Unix:
# First time setup:
chmod +x run_honeyshield.sh    # Make the script executable
# Then:
# Double-click run_honeyshield.sh
# OR
./run_honeyshield.sh
```

Method 2 - Using command line:
```bash
# On Windows:
venv\Scripts\activate
python -m honeyshield.main

# On Linux/Unix:
source venv/bin/activate
python -m honeyshield.main
```

2. Access the web dashboard:
Open your browser and navigate to `http://localhost:5001`

3. Monitor attacks:
- View real-time attack statistics
- Check recent attacks and alerts
- Monitor blocked IPs
- Receive Telegram notifications
- See live connection status
- Get instant toast notifications for new attacks

4. Stop the honeypot:
```bash
# If running in terminal:
Press Ctrl + C

# If running in background, find and kill the process:
ps aux | grep honeyshield | grep -v grep  # Find the process ID (PID)
kill <PID>                                # Kill using specific PID

# Or stop all honeypot processes at once:
pkill -f honeyshield
```

## Remote Testing

To test the honeypot from another PC:

1. On the honeypot server:
   ```bash
   # On Windows:
   # Configure Windows Firewall to allow ports 2222, 8081, and 5001
   
   # On Linux:
   sudo ufw allow 2222/tcp  # For SSH honeypot
   sudo ufw allow 8081/tcp  # For HTTP honeypot
   sudo ufw allow 5001/tcp  # For web dashboard
   
   # Get the server's IP address
   # On Windows:
   ipconfig
   
   # On Linux:
   ip addr show
   # or
   hostname -I
   ```

2. From the testing PC:
   ```bash
   # Test SSH honeypot
   ssh -p 2222 test@SERVER_IP
   
   # Test HTTP honeypot
   curl http://SERVER_IP:8081/
   
   # Access web dashboard
   # Open browser and navigate to:
   http://SERVER_IP:5001
   ```

3. For port scanning test:
   ```bash
   # On Windows:
   # Install nmap from https://nmap.org/download.html
   
   # On Linux:
   sudo apt install nmap  # On Debian/Ubuntu
   # or
   sudo yum install nmap  # On RHEL/CentOS
   
   # Scan the honeypot ports
   nmap -p 2222,8081 SERVER_IP
   ```

Note: Replace `SERVER_IP` with the actual IP address of the honeypot server.

## Port Configuration

- SSH Honeypot: Port 2222
- HTTP Honeypot: Port 8081
- Web Dashboard: Port 5001

## Security Considerations

1. Run the honeypot in an isolated environment
2. Use a dedicated machine or virtual machine
3. Monitor system resources
4. Regularly check logs for suspicious activity
5. Keep the system updated with security patches
6. Configure firewall rules appropriately
7. Use strong passwords for server access
8. Consider using a VPN for remote access
9. On Windows, ensure Windows Defender is properly configured
10. Keep Windows Firewall rules up to date

## Logging

Logs are stored in:
- `honeyshield.log`: Main application logs
- SQLite database (`honeyshield.db`): Attack and alert data
  - Events table: Stores all attack attempts with timestamps
  - Includes detailed information about each attack
  - Supports real-time event broadcasting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. Users are responsible for ensuring compliance with local laws and regulations when deploying this honeypot.

## Troubleshooting

Common Issues:

1. Port Already in Use:
```bash
Error: Address already in use
Solution: Stop any services using ports 2222, 8081, or 5001
```

2. Permission Denied:
```bash
Error: Permission denied
Solution: Run with administrator/root privileges
```

3. Module Not Found:
```bash
Error: No module named 'honeyshield'
Solution: Ensure you're in the correct directory and virtual environment is activated
```

4. Database Errors:
```bash
Error: Unable to open database file
Solution: Check file permissions in the honeyshield directory
```

## Backup and Maintenance

1. Database Backup:
```bash
# Copy the database file
cp honeyshield/honeyshield.db honeyshield/honeyshield.db.backup
```

2. Log Rotation:
- The `honeyshield.log` file should be rotated regularly
- Recommended: Set up logrotate or a similar tool
- Example logrotate configuration:
```
/path/to/honeyshield.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
}
```

## Security Best Practices

1. Isolated Environment Setup:
   - Use a dedicated virtual machine
   - Configure network isolation
   - Use a separate user account
   - Regular system updates

2. Network Security:
   - Use a dedicated network interface
   - Configure firewall rules
   - Monitor network traffic
   - Use VPN for remote access

3. Data Security:
   - Regular backups
   - Encrypted storage
   - Secure file permissions
   - Regular log review

### Note about Hidden Files
The `.env` file starts with a dot, making it hidden by default:
- On Linux/Unix: Press Ctrl + H in file manager to show hidden files
- On Windows: Enable "Show hidden files" in File Explorer options

### Optional: Telegram Setup
Telegram integration is optional. If you don't configure the Telegram credentials:
- The honeypot will still work
- You won't receive Telegram notifications
- All events will still be logged to the database and visible in the dashboard 