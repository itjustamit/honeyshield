import os
import sys
from colorama import init, Fore, Back, Style
from honeyshield import app

# Initialize colorama for cross-platform colored output
init(autoreset=True)

def print_banner():
    """Display the HoneyShield startup banner"""
    banner = f"""
{Fore.CYAN}═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
║                                                                              
║ {Fore.YELLOW}████   █████    ███████    ██████   █████ ██████████ █████ █████  █████████  █████   █████ █████ █████       ██████████ {Fore.CYAN}      
║░░{Fore.YELLOW}███   ░░███   ███░░░░░███ ░░██████ ░░███ ░░███░░░░░█░░███ ░░███  ███░░░░░███░░███   ░░███ ░░███ ░░███       ░░███░░░░███ {Fore.CYAN} 
║░ {Fore.YELLOW}███    ░███  ███     ░░███ ░███░███ ░███  ░███  █ ░  ░░███ ███  ░███    ░░░  ░███    ░███  ░███  ░███        ░███   ░░███ {Fore.CYAN}
║░ {Fore.YELLOW}███████████ ░███      ░███ ░███░░███░███  ░██████     ░░█████   ░░█████████  ░███████████  ░███  ░███        ░███    ░███ {Fore.CYAN}
║░ {Fore.YELLOW}███░░░░░███ ░███      ░███ ░███ ░░██████  ░███░░█      ░░███     ░░░░░░░░███ ░███░░░░░███  ░███  ░███        ░███    ░███ {Fore.CYAN}
║ ░{Fore.YELLOW}███    ░███ ░░███     ███  ░███  ░░█████  ░███ ░   █    ░███     ███    ░███ ░███    ░███  ░███  ░███      █ ░███    ███ {Fore.CYAN}
║  {Fore.YELLOW}█████   █████ ░░░███████░   █████  ░░█████ ██████████    █████   ░░█████████  █████   █████ █████ ███████████ ██████████  {Fore.CYAN}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
║    {Fore.GREEN}       __                  __   ___  __           __        ___      __   __  ___     ___  __   __  {Fore.CYAN}   
║    {Fore.GREEN}  /\  |  \ \  /  /\  |\ | /  ` |__  |  \    |__| /  \ |\ | |__  \ / |__) /  \  |     |__  /  \ |__) {Fore.CYAN}  
║    {Fore.GREEN} /~~\ |__/  \/  /~~\ | \| \__, |___ |__/    |  | \__/ | \| |___  |  |    \__/  |     |    \__/ |  \    
║    {Fore.GREEN}  __       __   ___  __     ___       __   ___      ___     __   ___ ___  ___  __  ___    __           
║    {Fore.GREEN} /  ` \ / |__) |__  |__)     |  |__| |__) |__   /\   |     |  \ |__   |  |__  /  `  |  | /  \ |\ |     
║    {Fore.GREEN} \__,  |  |__) |___ |  \     |  |  | |  \ |___ /~~\  |     |__/ |___  |  |___ \__,  |  | \__/ | \|     
║                                                                                                                                                                                                                         
║  {Fore.WHITE}Version: 2.0 | Author: Amit Kumar | Year: 2025{Fore.CYAN}                                                                                 
║  {Fore.WHITE}Brainware University | Bachelor of Science in Advance Networking and Cyber Security{Fore.CYAN}                                            
║                                                                                                                                                        
║  {Fore.MAGENTA} SSH Honeypot: Port 22{Fore.CYAN}                                                                                                     
║  {Fore.MAGENTA} HTTP Honeypot: Port 80{Fore.CYAN}                                                                                                    
║  {Fore.MAGENTA} Web Dashboard: Port 5001{Fore.CYAN}                                                                                                  
║                                                                                                                                                        
║  {Fore.YELLOW}  WARNING: This is a honeypot system for research purposes only{Fore.CYAN}                                                             
║  {Fore.YELLOW}   Do not use in production environments without proper security{Fore.CYAN}                                                              
║                                                                              
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
{Style.RESET_ALL}"""
    
    print(banner)
    print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} HoneyShield honeypot is starting...")
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} Web dashboard will be available at: {Fore.CYAN}http://localhost:5001{Style.RESET_ALL}")
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} SSH honeypot listening on port: {Fore.CYAN}22{Style.RESET_ALL}")
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} HTTP honeypot listening on port: {Fore.CYAN}80{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Press Ctrl+C to stop the honeypot")
    print("-" * 80)

if __name__ == '__main__':
    # Clear screen and print banner
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    # Start the Flask application
    try:
        app.run(host='0.0.0.0', port=5001, debug=False)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[INFO]{Style.RESET_ALL} HoneyShield honeypot stopped by user")
        sys.exit(0) 