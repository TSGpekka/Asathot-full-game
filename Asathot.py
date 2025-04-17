#!/usr/bin/env python3
"""
Asathot - A realistic terminal-based hacking simulation game set in the Mr. Robot universe.
Players earn cryptocurrency through hacking missions, battle against E Corp and the Dark Army,
and upgrade their systems to become elite hackers within the fsociety movement.
"""

import os
import sys
import time
import random
import datetime
import re
import json
import shutil
from typing import Dict, List, Tuple, Optional, Union, Any
from collections import defaultdict
import threading
import math

try:
    import colorama
    from colorama import Fore, Back, Style
    import pyfiglet
    from simple_term_menu import TerminalMenu
except ImportError:
    print("Required packages not found. Installing dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama", "pyfiglet", "simple-term-menu"])
    import colorama
    from colorama import Fore, Back, Style
    import pyfiglet
    from simple_term_menu import TerminalMenu

# Initialize colorama
colorama.init(autoreset=True)

# Global constants
SAVE_FILE = "asathot_data.json"
VERSION = "1.0.0"
DEFAULT_BTC_VALUE = 45000  # USD per BTC
DEFAULT_ECOIN_VALUE = 1    # USD per E-Coin
MIN_TERMINAL_WIDTH = 80
MIN_TERMINAL_HEIGHT = 24

# Mr. Robot universe constants
FSOCIETY_REP_THRESHOLD = 50  # Reputation needed to join fsociety
DARK_ARMY_REP_THRESHOLD = 75  # Reputation needed to be noticed by Dark Army
ECORP_SECURITY_LEVEL = 9     # E Corp security level (very high)

# Game state
class GameState:
    def __init__(self):
        self.current_dir = "~"
        self.file_system = {
            "~": {
                "type": "dir",
                "content": {
                    "documents": {
                        "type": "dir",
                        "content": {
                            "readme.txt": {
                                "type": "file",
                                "content": "Welcome to Asathot!\n\nThis terminal is your gateway to joining fsociety and taking down E Corp. Start by connecting to the darknet using the 'connect' command. Be careful, the Dark Army is watching.\n\n\"Hello, friend. Hello, friend? That's lame. Maybe I should give you a name.\" - Elliot Alderson"
                            },
                            "manifesto.txt": {
                                "type": "file",
                                "content": "FSOCIETY MANIFESTO\n\nThe world is a dangerous place, not because of those who do evil, but because of those who look on and do nothing.\n\nWe are fsociety. We are free. We are one. We are legion. Join us."
                            },
                            "about_e_corp.txt": {
                                "type": "file",
                                "content": "E Corp (also known as Evil Corp) is the world's largest conglomerate. They've monopolized every industry and now own 70% of the global consumer credit industry.\n\nTheir E-Coin cryptocurrency is quickly becoming the new standard, while ordinary people fall into deeper debt.\n\nA major vulnerability may exist in their systems, if only someone could find it..."
                            }
                        }
                    },
                    "downloads": {
                        "type": "dir",
                        "content": {}
                    },
                    "tools": {
                        "type": "dir",
                        "content": {
                            "network_scanner.py": {
                                "type": "file",
                                "content": "# Basic network scanner\n# Usage: run network_scanner.py <target_ip>\n\n# Scans for open ports and running services, identifies OS version\n# Written in Python to evade common IDS signatures"
                            },
                            "bruteforce.py": {
                                "type": "file",
                                "content": "# Password brute force tool\n# Usage: run bruteforce.py <target_ip> <service>\n\n# Cycles through wordlists and common password combinations\n# Utilizes intelligent throttling to avoid lockouts\n# Caution: Use only on authorized targets"
                            },
                            "rootkit_gen.py": {
                                "type": "file",
                                "content": "# Rootkit generator with cloaking features\n# Usage: run rootkit_gen.py <target_ip>\n\n# Creates a hidden backdoor to maintain access\n# Requires significant skill to use effectively\n# Requires root access to install"
                            },
                            "data_exfiltrator.py": {
                                "type": "file",
                                "content": "# Advanced data exfiltration tool\n# Usage: run data_exfiltrator.py <target_ip> <path>\n\n# Extracts specified files or databases securely\n# Uses encrypted channels to avoid detection\n# Required for fsociety operations"
                            }
                        }
                    },
                    "fsociety": {
                        "type": "dir",
                        "content": {
                            "locked.txt": {
                                "type": "file", 
                                "content": "This directory requires more reputation to access. Join the revolution."
                            }
                        }
                    }
                }
            }
        }
        
        # Player stats
        self.player = {
            "bitcoin": 0.001,  # Starting BTC
            "ecoin": 0.0,      # E-Coin (E Corp cryptocurrency)
            "reputation": 0,    # Hacker reputation
            "fsociety_member": False,  # Whether player has joined fsociety
            "dark_army_contact": False,  # Whether player has been contacted by Dark Army
            "skills": {
                "network": 1,   # Network hacking abilities
                "crypto": 1,    # Cryptography skills
                "malware": 1,   # Malware development skills
                "social": 1     # Social engineering skills
            },
            "completed_missions": [],
            "current_mission": None,
            "discovered_ips": []
        }
        
        # Virtual PC stats
        self.pc = {
            "cpu": {
                "name": "Pentium II",
                "cores": 1,
                "speed": 1.0,  # GHz
                "level": 1
            },
            "ram": {
                "name": "DDR1",
                "size": 512,   # MB
                "level": 1
            },
            "storage": {
                "name": "HDD",
                "size": 20,    # GB
                "level": 1
            },
            "network": {
                "name": "56K Modem",
                "speed": 0.056, # Mbps
                "level": 1
            },
            "security": {
                "name": "Basic Firewall",
                "level": 1
            }
        }
        
        # Available missions
        self.missions = [
            {
                "id": "m001",
                "title": "First Steps",
                "description": "Scan a local network for vulnerabilities.",
                "difficulty": 1,
                "target": "192.168.1.1",
                "reward": 0.0005,
                "rep_reward": 5,
                "completed": False,
                "steps": ["scan", "exploit vulnerability", "download data"],
                "current_step": 0
            },
            {
                "id": "m002",
                "title": "Password Recovery",
                "description": "Help a 'friend' recover their password from a website.",
                "difficulty": 1,
                "target": "103.42.81.12",
                "reward": 0.001,
                "rep_reward": 10,
                "completed": False,
                "steps": ["scan", "bruteforce login", "recover password"],
                "current_step": 0
            },
            {
                "id": "m003",
                "title": "Allsafe Insider",
                "description": "Access Allsafe Cybersecurity's systems with help from an insider contact.",
                "difficulty": 3,
                "target": "69.172.201.153",
                "reward": 0.003,
                "rep_reward": 15,
                "completed": False,
                "steps": ["scan", "use insider credentials", "escalate privileges", "access client list"],
                "current_step": 0,
                "fsociety_related": True
            },
            {
                "id": "m004",
                "title": "Steel Mountain HVAC",
                "description": "Infiltrate Steel Mountain's data center by exploiting their HVAC system.",
                "difficulty": 4,
                "target": "13.57.137.205",
                "reward": 0.01,
                "rep_reward": 30,
                "completed": False,
                "steps": ["scan", "identify HVAC system", "exploit control systems", "plant backdoor", "cover tracks"],
                "current_step": 0,
                "fsociety_related": True,
                "requires_rep": 20
            },
            {
                "id": "m005",
                "title": "E Corp Reconnaissance",
                "description": "Perform initial reconnaissance on E Corp's banking infrastructure.",
                "difficulty": 5,
                "target": "104.128.115.74",
                "reward": 0.02,
                "rep_reward": 40,
                "completed": False,
                "steps": ["scan", "map network", "identify vulnerabilities", "document findings", "exit without trace"],
                "current_step": 0,
                "fsociety_required": True,
                "requires_rep": 45
            }
        ]
        
        # Championship tasks
        self.championships = [
            {
                "id": "c001",
                "title": "Newbie Challenge",
                "description": "A basic challenge for beginners to prove their skills.",
                "difficulty": 2,
                "target": "195.78.33.24",
                "reward": 0.01,
                "rep_reward": 25,
                "required_rep": 20,
                "completed": False,
                "tasks": ["network scan", "infiltration", "data extraction", "cover tracks"],
                "current_task": 0
            },
            {
                "id": "c002",
                "title": "Five/Nine Prep",
                "description": "Fsociety championship to prepare for a major E Corp attack.",
                "difficulty": 5,
                "target": "104.128.115.74",
                "reward": 0.05,
                "rep_reward": 50,
                "required_rep": FSOCIETY_REP_THRESHOLD,
                "completed": False,
                "tasks": ["bypass firewall", "access loan database", "plant encryption prep", "establish persistence", "avoid detection"],
                "current_task": 0,
                "fsociety_required": True
            },
            {
                "id": "c003",
                "title": "Dark Army Infiltration",
                "description": "Prove your worth to the Dark Army by infiltrating a secure government server.",
                "difficulty": 8,
                "target": "192.251.68.242",
                "reward": 0.2,
                "rep_reward": 100,
                "required_rep": DARK_ARMY_REP_THRESHOLD,
                "completed": False,
                "tasks": ["identify entry point", "evade monitoring systems", "obtain encryption keys", "retrieve target data", "delete logs", "exit through covert channel"],
                "current_task": 0,
                "dark_army_required": True
            }
        ]

        # Network targets
        self.network_targets = [
            {
                "ip": "192.168.1.1",
                "name": "Small Business Server",
                "security_level": 1,
                "services": ["http", "ssh", "ftp"],
                "vulnerabilities": ["outdated_ssh", "weak_password"],
                "discovered": False
            },
            {
                "ip": "103.42.81.12",
                "name": "Social Media Website",
                "security_level": 2,
                "services": ["http", "https", "mysql"],
                "vulnerabilities": ["sql_injection", "xss"],
                "discovered": False
            },
            {
                "ip": "195.78.33.24",
                "name": "Corporate Network",
                "security_level": 3,
                "services": ["http", "https", "ssh", "smtp"],
                "vulnerabilities": ["outdated_apache", "weak_admin_password"],
                "discovered": False
            },
            {
                "ip": "69.172.201.153",
                "name": "Allsafe Cybersecurity",
                "security_level": 4,
                "services": ["http", "https", "ssh", "vpn", "mail"],
                "vulnerabilities": ["insider_access", "default_credentials"],
                "discovered": False,
                "description": "Cybersecurity firm with potential insider help"
            },
            {
                "ip": "104.128.115.74",
                "name": "E Corp Banking System",
                "security_level": 7,
                "services": ["https", "sql", "radius", "proprietary"],
                "vulnerabilities": ["custom_vulnerability", "outdated_middleware"],
                "discovered": False,
                "description": "High-security E Corp banking infrastructure"
            },
            {
                "ip": "13.57.137.205",
                "name": "Steel Mountain Data Center",
                "security_level": 5,
                "services": ["https", "hvac", "proprietary_scada", "building_management"],
                "vulnerabilities": ["hvac_exploitable", "physical_access_controls"],
                "discovered": False,
                "description": "Corporate data storage facility with HVAC systems"
            },
            {
                "ip": "192.251.68.242",
                "name": "Dark Army Communication Server",
                "security_level": 8,
                "services": ["unknown", "custom_protocol", "encrypted"],
                "vulnerabilities": ["hidden_backdoor", "disguised_entry_point"],
                "discovered": False,
                "description": "Encrypted server with potential Dark Army connections"
            }
        ]

        # Available upgrades
        self.upgrades = {
            "cpu": [
                {"name": "Pentium II", "cores": 1, "speed": 1.0, "cost": 0.0, "level": 1},
                {"name": "Pentium III", "cores": 1, "speed": 1.5, "cost": 0.005, "level": 2},
                {"name": "Pentium 4", "cores": 2, "speed": 2.0, "cost": 0.01, "level": 3},
                {"name": "Core 2 Duo", "cores": 2, "speed": 2.5, "cost": 0.02, "level": 4},
                {"name": "Core i5", "cores": 4, "speed": 3.0, "cost": 0.05, "level": 5},
                {"name": "Core i7", "cores": 8, "speed": 3.5, "cost": 0.1, "level": 6},
                {"name": "Core i9", "cores": 12, "speed": 4.0, "cost": 0.2, "level": 7},
                {"name": "ThreadRipper", "cores": 16, "speed": 4.5, "cost": 0.4, "level": 8}
            ],
            "ram": [
                {"name": "DDR1", "size": 512, "cost": 0.0, "level": 1},
                {"name": "DDR2", "size": 1024, "cost": 0.003, "level": 2},
                {"name": "DDR3", "size": 2048, "cost": 0.007, "level": 3},
                {"name": "DDR3 Dual", "size": 4096, "cost": 0.015, "level": 4},
                {"name": "DDR4", "size": 8192, "cost": 0.03, "level": 5},
                {"name": "DDR4 Dual", "size": 16384, "cost": 0.06, "level": 6},
                {"name": "DDR5", "size": 32768, "cost": 0.12, "level": 7},
                {"name": "DDR5 Dual", "size": 65536, "cost": 0.25, "level": 8}
            ],
            "storage": [
                {"name": "HDD", "size": 20, "cost": 0.0, "level": 1},
                {"name": "HDD 7200RPM", "size": 100, "cost": 0.002, "level": 2},
                {"name": "HDD RAID", "size": 500, "cost": 0.006, "level": 3},
                {"name": "SSD", "size": 250, "cost": 0.012, "level": 4},
                {"name": "SSD", "size": 500, "cost": 0.025, "level": 5},
                {"name": "SSD RAID", "size": 1000, "cost": 0.05, "level": 6},
                {"name": "NVMe", "size": 2000, "cost": 0.1, "level": 7},
                {"name": "NVMe RAID", "size": 4000, "cost": 0.2, "level": 8}
            ],
            "network": [
                {"name": "56K Modem", "speed": 0.056, "cost": 0.0, "level": 1},
                {"name": "ADSL", "speed": 1, "cost": 0.004, "level": 2},
                {"name": "Cable", "speed": 10, "cost": 0.008, "level": 3},
                {"name": "Fiber 50", "speed": 50, "cost": 0.018, "level": 4},
                {"name": "Fiber 100", "speed": 100, "cost": 0.035, "level": 5},
                {"name": "Fiber 500", "speed": 500, "cost": 0.07, "level": 6},
                {"name": "Fiber 1G", "speed": 1000, "cost": 0.15, "level": 7},
                {"name": "Fiber 10G", "speed": 10000, "cost": 0.3, "level": 8}
            ],
            "security": [
                {"name": "Basic Firewall", "cost": 0.0, "level": 1},
                {"name": "Advanced Firewall", "cost": 0.005, "level": 2},
                {"name": "Intrusion Detection", "cost": 0.01, "level": 3},
                {"name": "Intrusion Prevention", "cost": 0.02, "level": 4},
                {"name": "VPN Tunnel", "cost": 0.04, "level": 5},
                {"name": "Encrypted Storage", "cost": 0.08, "level": 6},
                {"name": "Military-grade Security", "cost": 0.16, "level": 7},
                {"name": "Quantum Encryption", "cost": 0.35, "level": 8}
            ]
        }

        # Darkweb sites
        self.connected_to_darkweb = False
        self.current_site = None  # Current site domain (string)
        
        # Game history (for terminal output)
        self.history = []
        
        # Stats tracking
        self.stats = {
            "commands_executed": 0,
            "successful_hacks": 0,
            "failed_hacks": 0,
            "bitcoin_earned": 0.0,
            "bitcoin_spent": 0.0,
            "reputation_earned": 0,
            "missions_completed": 0,
            "championships_won": 0,
            "time_played": 0
        }
        
        # Game start time
        self.start_time = time.time()
        self.last_save_time = self.start_time

# Initialize game state
game_state = GameState()

# Utility functions
def format_btc(amount: float) -> str:
    """Format a Bitcoin amount with proper prefix (BTC, mBTC, μBTC, satoshi)"""
    if amount >= 1.0:
        return f"{amount:.4f} BTC"
    elif amount >= 0.001:
        return f"{amount * 1000:.4f} mBTC"
    elif amount >= 0.000001:
        return f"{amount * 1000000:.4f} μBTC"
    else:
        return f"{amount * 100000000:.0f} satoshi"

def get_btc_usd_value(btc_amount: float) -> float:
    """Get the USD value of a Bitcoin amount"""
    return btc_amount * DEFAULT_BTC_VALUE

def print_header():
    """Print the game header/banner"""
    header = pyfiglet.figlet_format("ASATHOT", font="slant")
    term_width = shutil.get_terminal_size().columns
    
    print(Fore.RED + header)
    print(Fore.RED + "=" * term_width)
    
    # Show join status based on reputation
    fsociety_status = ""
    if game_state.player["dark_army_contact"]:
        fsociety_status = f"{Fore.RED}[Dark Army]"
    elif game_state.player["fsociety_member"]:
        fsociety_status = f"{Fore.RED}[fsociety]"
    elif game_state.player["reputation"] >= DARK_ARMY_REP_THRESHOLD:
        fsociety_status = f"{Fore.RED}[Dark Army watching]"
    elif game_state.player["reputation"] >= FSOCIETY_REP_THRESHOLD:
        fsociety_status = f"{Fore.RED}[fsociety candidate]"
    
    # E-Coin display if applicable
    ecoin_display = ""
    if game_state.player["ecoin"] > 0:
        ecoin_display = f"{Fore.GREEN}E-Coin: {game_state.player['ecoin']:.2f}" + " " * 3
    
    print(Fore.WHITE + f"Version: {VERSION}" + " " * 3 + 
          Fore.YELLOW + f"BTC: {format_btc(game_state.player['bitcoin'])}" + " " * 3 + 
          ecoin_display +
          Fore.MAGENTA + f"Rep: {game_state.player['reputation']}" + " " * 3 +
          fsociety_status)
    
    print(Fore.RED + "=" * term_width)
    print()

def save_game():
    """Save the game state to a file"""
    # Update time played before saving
    current_time = time.time()
    game_state.stats["time_played"] += current_time - game_state.last_save_time
    game_state.last_save_time = current_time
    
    data = {
        "player": game_state.player,
        "pc": game_state.pc,
        "missions": game_state.missions,
        "championships": game_state.championships,
        "network_targets": game_state.network_targets,
        "stats": game_state.stats,
        "file_system": game_state.file_system,
        "current_dir": game_state.current_dir,
    }
    
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)
        print(Fore.GREEN + "Game saved successfully!")
    except Exception as e:
        print(Fore.RED + f"Error saving game: {e}")

def load_game() -> bool:
    """Load the game state from a file"""
    if not os.path.exists(SAVE_FILE):
        return False
    
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        
        game_state.player = data.get("player", game_state.player)
        game_state.pc = data.get("pc", game_state.pc)
        game_state.missions = data.get("missions", game_state.missions)
        game_state.championships = data.get("championships", game_state.championships)
        game_state.network_targets = data.get("network_targets", game_state.network_targets)
        game_state.stats = data.get("stats", game_state.stats)
        game_state.file_system = data.get("file_system", game_state.file_system)
        game_state.current_dir = data.get("current_dir", game_state.current_dir)
        
        # Reset connection status on load
        game_state.connected_to_darkweb = False
        game_state.current_site = None
        
        # Update last save time
        game_state.last_save_time = time.time()
        
        print(Fore.GREEN + "Game loaded successfully!")
        return True
    except Exception as e:
        print(Fore.RED + f"Error loading game: {e}")
        return False

def add_to_history(message: str, color: str = Fore.WHITE):
    """Add a message to the command history"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    game_state.history.append({"timestamp": timestamp, "message": message, "color": color})
    
    # Keep history at a reasonable size
    if len(game_state.history) > 100:
        game_state.history.pop(0)

def display_history(count: int = 10):
    """Display the recent command history"""
    if not game_state.history:
        print(Fore.YELLOW + "No command history available.")
        return
    
    start = max(0, len(game_state.history) - count)
    for i in range(start, len(game_state.history)):
        entry = game_state.history[i]
        print(f"{Fore.BLUE}[{entry['timestamp']}] {entry['color']}{entry['message']}")

def get_pc_power_level() -> float:
    """Calculate the current PC's power level"""
    cpu_power = game_state.pc["cpu"]["speed"] * game_state.pc["cpu"]["cores"]
    ram_power = game_state.pc["ram"]["size"] / 1024  # Convert to GB
    storage_factor = math.log10(game_state.pc["storage"]["size"] + 1)
    network_factor = math.log10(game_state.pc["network"]["speed"] * 10 + 1)
    security_level = game_state.pc["security"]["level"]
    
    return (cpu_power * 2 + ram_power + storage_factor + network_factor + security_level) / 6

def get_difficulty_level(target: Dict) -> float:
    """Calculate the difficulty level of a target"""
    return target["security_level"] * (0.5 + random.random())

def calculate_hack_success_chance(difficulty: float) -> float:
    """Calculate the chance of successful hacking based on PC power and target difficulty"""
    pc_power = get_pc_power_level()
    skill_factor = sum(game_state.player["skills"].values()) / 10
    
    # Base chance formula
    chance = (pc_power * skill_factor) / difficulty
    
    # Normalize to 0-1 range with some randomness
    chance = min(0.95, max(0.05, chance))
    
    return chance

def generate_random_ip() -> str:
    """Generate a random IP address"""
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def get_target_by_ip(ip: str) -> Optional[Dict]:
    """Get a network target by IP address"""
    for target in game_state.network_targets:
        if target["ip"] == ip:
            return target
    return None

def discover_ip(ip: str) -> bool:
    """Mark an IP as discovered and return True if it's new"""
    if ip not in game_state.player["discovered_ips"]:
        game_state.player["discovered_ips"].append(ip)
        return True
    return False

def get_mission_by_id(mission_id: str) -> Optional[Dict]:
    """Get a mission by its ID"""
    for mission in game_state.missions:
        if mission["id"] == mission_id:
            return mission
    return None

def get_championship_by_id(championship_id: str) -> Optional[Dict]:
    """Get a championship by its ID"""
    for championship in game_state.championships:
        if championship["id"] == championship_id:
            return championship
    return None

def upgrade_component(component: str, level: int) -> bool:
    """Upgrade a PC component to the specified level"""
    if component not in game_state.upgrades:
        print(Fore.RED + f"Unknown component: {component}")
        return False
    
    current_level = game_state.pc[component]["level"]
    if level <= current_level:
        print(Fore.YELLOW + f"You already have a level {current_level} {component}.")
        return False
    
    if level > len(game_state.upgrades[component]):
        print(Fore.RED + f"Maximum level for {component} is {len(game_state.upgrades[component])}")
        return False
    
    upgrade = game_state.upgrades[component][level-1]
    cost = upgrade["cost"]
    
    if game_state.player["bitcoin"] < cost:
        print(Fore.RED + f"Not enough Bitcoin! You need {format_btc(cost)}.")
        return False
    
    # Apply the upgrade
    game_state.player["bitcoin"] -= cost
    game_state.stats["bitcoin_spent"] += cost
    
    # Update the component
    for key, value in upgrade.items():
        if key != "cost":
            game_state.pc[component][key] = value
    
    print(Fore.GREEN + f"Successfully upgraded {component} to {upgrade['name']} (Level {level})!")
    return True

def format_time(seconds: int) -> str:
    """Format seconds into a human-readable time string"""
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    
    if days > 0:
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

def display_skills():
    """Display player skills"""
    print(Fore.CYAN + "===== HACKER SKILLS =====")
    for skill, level in game_state.player["skills"].items():
        print(f"{Fore.YELLOW}{skill.capitalize()}: {Fore.GREEN}{level}/10 {'[' + '■' * level + '□' * (10-level) + ']'}")
    print()

def display_pc_stats():
    """Display PC stats"""
    print(Fore.CYAN + "===== PC SPECIFICATIONS =====")
    print(f"{Fore.YELLOW}CPU: {Fore.GREEN}{game_state.pc['cpu']['name']} " +
          f"({game_state.pc['cpu']['cores']} cores @ {game_state.pc['cpu']['speed']} GHz) - Level {game_state.pc['cpu']['level']}")
    
    print(f"{Fore.YELLOW}RAM: {Fore.GREEN}{game_state.pc['ram']['name']} " +
          f"({game_state.pc['ram']['size']} MB) - Level {game_state.pc['ram']['level']}")
    
    print(f"{Fore.YELLOW}Storage: {Fore.GREEN}{game_state.pc['storage']['name']} " +
          f"({game_state.pc['storage']['size']} GB) - Level {game_state.pc['storage']['level']}")
    
    print(f"{Fore.YELLOW}Network: {Fore.GREEN}{game_state.pc['network']['name']} " +
          f"({game_state.pc['network']['speed']} Mbps) - Level {game_state.pc['network']['level']}")
    
    print(f"{Fore.YELLOW}Security: {Fore.GREEN}{game_state.pc['security']['name']} " +
          f"- Level {game_state.pc['security']['level']}")
    
    pc_power = get_pc_power_level()
    print(f"{Fore.YELLOW}Overall Power: {Fore.GREEN}{pc_power:.2f}")
    print()

def display_player_stats():
    """Display player statistics"""
    print(Fore.CYAN + "===== HACKER STATISTICS =====")
    print(f"{Fore.YELLOW}Bitcoin: {Fore.GREEN}{format_btc(game_state.player['bitcoin'])} " +
          f"(${get_btc_usd_value(game_state.player['bitcoin']):.2f})")
    print(f"{Fore.YELLOW}Reputation: {Fore.GREEN}{game_state.player['reputation']}")
    print(f"{Fore.YELLOW}Commands executed: {Fore.GREEN}{game_state.stats['commands_executed']}")
    print(f"{Fore.YELLOW}Successful hacks: {Fore.GREEN}{game_state.stats['successful_hacks']}")
    print(f"{Fore.YELLOW}Failed hacks: {Fore.GREEN}{game_state.stats['failed_hacks']}")
    print(f"{Fore.YELLOW}Bitcoin earned: {Fore.GREEN}{format_btc(game_state.stats['bitcoin_earned'])}")
    print(f"{Fore.YELLOW}Bitcoin spent: {Fore.GREEN}{format_btc(game_state.stats['bitcoin_spent'])}")
    print(f"{Fore.YELLOW}Missions completed: {Fore.GREEN}{game_state.stats['missions_completed']}")
    print(f"{Fore.YELLOW}Championships won: {Fore.GREEN}{game_state.stats['championships_won']}")
    
    # Calculate total time played
    current_time = time.time()
    total_time_played = game_state.stats["time_played"] + (current_time - game_state.last_save_time)
    print(f"{Fore.YELLOW}Time played: {Fore.GREEN}{format_time(total_time_played)}")
    print()

def skill_level_up_check(skill: str, increment: float = 0.1) -> bool:
    """Check if a skill should level up and apply the increment"""
    if skill not in game_state.player["skills"]:
        return False
    
    current_level = game_state.player["skills"][skill]
    if current_level >= 10:  # Max level
        return False
    
    # Random chance to level up, harder as levels increase
    chance = 0.1 / current_level
    if random.random() < chance:
        # Calculate how much to increase (partial levels)
        new_level_float = current_level + increment
        if new_level_float >= int(current_level) + 1:
            game_state.player["skills"][skill] = int(new_level_float)
            print(Fore.GREEN + f"Skill level up! Your {skill} skill is now level {int(new_level_float)}!")
            return True
        else:
            game_state.player["skills"][skill] = new_level_float
    
    return False

def get_time_for_hack(target_difficulty: float) -> float:
    """Calculate the time needed for a hack based on PC specs and difficulty"""
    pc_power = get_pc_power_level()
    network_speed_factor = math.log10(game_state.pc["network"]["speed"] + 1) / 3
    cpu_factor = game_state.pc["cpu"]["speed"] * game_state.pc["cpu"]["cores"] / 10
    
    # Base time (5-30 seconds)
    base_time = 5 + (target_difficulty * 5)
    
    # Adjust based on PC specs
    adjusted_time = base_time / (pc_power * network_speed_factor * cpu_factor)
    
    # Ensure reasonable range (2-60 seconds)
    return max(2, min(60, adjusted_time))

def perform_hack(target_ip: str, hack_type: str) -> bool:
    """Perform a hacking attempt on a target"""
    target = get_target_by_ip(target_ip)
    if not target:
        print(Fore.RED + f"Target {target_ip} not found in the network.")
        return False
    
    if not target["discovered"]:
        print(Fore.RED + f"You need to scan {target_ip} first to discover it.")
        return False
    
    # Determine difficulty and success chance
    difficulty = get_difficulty_level(target)
    success_chance = calculate_hack_success_chance(difficulty)
    
    # Display hacking animation and process
    print(Fore.CYAN + f"Attempting to {hack_type} {target_ip} ({target['name']})...")
    print(Fore.YELLOW + f"Target security level: {target['security_level']}")
    print(Fore.YELLOW + f"Success chance: {success_chance*100:.1f}%")
    
    # Calculate how long the hack should take
    hack_time = get_time_for_hack(difficulty)
    
    # Perform the hack with animation
    start_time = time.time()
    successful = random.random() < success_chance
    
    # Animation
    progress = 0
    while time.time() - start_time < hack_time:
        progress = (time.time() - start_time) / hack_time
        bar_length = 40
        completed_length = int(bar_length * progress)
        
        if successful:
            color = Fore.GREEN
        else:
            # If it's going to fail, show red near the end
            color = Fore.GREEN if progress < 0.8 else Fore.RED
            
        progress_bar = f"[{color}{'█' * completed_length}{'░' * (bar_length - completed_length)}{Style.RESET_ALL}]"
        percentage = int(progress * 100)
        
        sys.stdout.write(f"\r{progress_bar} {percentage}% ")
        sys.stdout.flush()
        time.sleep(0.1)
    
    print()  # Newline after progress bar
    
    # Skill improvement chance
    skills_to_improve = []
    if hack_type == "scan":
        skills_to_improve.append("network")
    elif hack_type == "exploit":
        skills_to_improve.extend(["network", "malware"])
    elif hack_type == "bruteforce":
        skills_to_improve.extend(["crypto", "network"])
    elif hack_type == "social":
        skills_to_improve.append("social")
    
    for skill in skills_to_improve:
        skill_level_up_check(skill)
    
    # Update stats
    if successful:
        game_state.stats["successful_hacks"] += 1
        print(Fore.GREEN + f"Hack successful! You have compromised {target_ip}.")
        
        if hack_type == "scan":
            print(Fore.GREEN + "Target information:")
            print(Fore.YELLOW + f"Name: {target['name']}")
            print(Fore.YELLOW + f"Security Level: {target['security_level']}")
            print(Fore.YELLOW + f"Services: {', '.join(target['services'])}")
            if random.random() < 0.7:  # 70% chance to detect vulnerabilities
                print(Fore.GREEN + f"Vulnerabilities detected: {', '.join(target['vulnerabilities'])}")
        
        # Check for mission/championship progress
        update_mission_progress(target_ip, hack_type)
    else:
        game_state.stats["failed_hacks"] += 1
        print(Fore.RED + f"Hack failed! The security systems on {target_ip} rejected your attempt.")
        
        # Small chance of reputation loss on failure
        if random.random() < 0.2:  # 20% chance
            rep_loss = random.randint(1, 3)
            game_state.player["reputation"] = max(0, game_state.player["reputation"] - rep_loss)
            print(Fore.RED + f"Your reputation decreased by {rep_loss} points due to the failed hack.")
    
    return successful

def update_mission_progress(target_ip: str, hack_type: str) -> None:
    """Update the progress of the current mission if applicable"""
    if not game_state.player["current_mission"]:
        return
    
    mission_id = game_state.player["current_mission"]
    mission = get_mission_by_id(mission_id)
    
    if not mission:
        game_state.player["current_mission"] = None
        return
    
    if mission["target"] != target_ip:
        return
    
    current_step = mission["current_step"]
    if current_step >= len(mission["steps"]):
        return
    
    # Map hack types to mission steps
    step_to_hack = {
        "scan": ["scan", "reconnaissance", "discovery"],
        "exploit": ["exploit", "exploit vulnerability", "infiltrate", "infiltration"],
        "bruteforce": ["bruteforce", "bruteforce login", "crack password"],
        "download": ["download", "download data", "data extraction", "extract data"],
        "social": ["social engineering", "phishing"]
    }
    
    current_mission_step = mission["steps"][current_step].lower()
    
    # Check if the current hack type matches the mission step
    matched = False
    for hack, steps in step_to_hack.items():
        if hack_type == hack and any(step in current_mission_step for step in steps):
            matched = True
            break
    
    if matched:
        mission["current_step"] += 1
        print(Fore.GREEN + f"Mission progress: Step {current_step + 1}/{len(mission['steps'])} completed!")
        
        # Check if mission is complete
        if mission["current_step"] >= len(mission["steps"]):
            complete_mission(mission_id)

def complete_mission(mission_id: str) -> None:
    """Complete a mission and award rewards"""
    mission = get_mission_by_id(mission_id)
    if not mission:
        return
    
    if mission["completed"]:
        return
    
    # Award rewards
    bitcoin_reward = mission["reward"]
    rep_reward = mission["rep_reward"]
    
    game_state.player["bitcoin"] += bitcoin_reward
    game_state.stats["bitcoin_earned"] += bitcoin_reward
    game_state.player["reputation"] += rep_reward
    game_state.stats["missions_completed"] += 1
    
    # Mark mission as completed
    mission["completed"] = True
    game_state.player["completed_missions"].append(mission_id)
    game_state.player["current_mission"] = None
    
    print(Fore.GREEN + f"Mission '{mission['title']}' completed!")
    print(Fore.GREEN + f"Reward: {format_btc(bitcoin_reward)} and {rep_reward} reputation points!")
    
    # Generate new mission
    generate_new_mission()

def complete_championship(championship_id: str) -> None:
    """Complete a championship and award rewards"""
    championship = get_championship_by_id(championship_id)
    if not championship:
        return
    
    if championship["completed"]:
        return
    
    # Award rewards
    bitcoin_reward = championship["reward"]
    rep_reward = championship["rep_reward"]
    
    game_state.player["bitcoin"] += bitcoin_reward
    game_state.stats["bitcoin_earned"] += bitcoin_reward
    game_state.player["reputation"] += rep_reward
    game_state.stats["championships_won"] += 1
    
    # Mark championship as completed
    championship["completed"] = True
    
    print(Fore.GREEN + f"Championship '{championship['title']}' completed!")
    print(Fore.GREEN + f"Reward: {format_btc(bitcoin_reward)} and {rep_reward} reputation points!")
    
    # Generate new championship
    generate_new_championship()

def generate_new_mission() -> Dict:
    """Generate a new mission for the player"""
    # Use existing targets first, or generate new ones
    available_targets = [t for t in game_state.network_targets if not any(m["target"] == t["ip"] for m in game_state.missions if not m["completed"])]
    
    if not available_targets:
        # Generate a new target
        new_target = {
            "ip": generate_random_ip(),
            "name": random.choice([
                "Small Company Server", 
                "Personal Blog", 
                "E-commerce Site",
                "University Database",
                "Local Government Portal",
                "Corporate Intranet",
                "Cloud Storage Provider",
                "Streaming Service Backend"
            ]),
            "security_level": random.randint(1, 5),
            "services": random.sample(["http", "https", "ftp", "ssh", "telnet", "smtp", "mysql", "dns"], 
                                     random.randint(2, 5)),
            "vulnerabilities": random.sample([
                "outdated_software", "weak_password", "sql_injection", "xss", 
                "csrf", "directory_traversal", "rce", "default_credentials"
            ], random.randint(1, 3)),
            "discovered": False
        }
        game_state.network_targets.append(new_target)
        target = new_target
    else:
        target = random.choice(available_targets)
    
    # Calculate difficulty based on player skills and previous missions
    avg_skill = sum(game_state.player["skills"].values()) / len(game_state.player["skills"])
    base_difficulty = max(1, min(5, round(avg_skill * random.uniform(0.8, 1.2))))
    
    # Prepare mission steps
    steps = ["scan"]
    # Add 1-3 more steps based on difficulty
    possible_steps = ["exploit vulnerability", "bruteforce login", "download data", "social engineering", "cover tracks"]
    steps.extend(random.sample(possible_steps, min(base_difficulty, len(possible_steps))))
    
    # Calculate rewards
    base_reward = 0.001 * base_difficulty * random.uniform(0.8, 1.2)
    rep_reward = 5 * base_difficulty
    
    # Create new mission
    mission_id = f"m{random.randint(100, 999)}"
    mission = {
        "id": mission_id,
        "title": random.choice([
            "Data Infiltration",
            "Password Compromise",
            "Server Breach",
            "Database Extraction",
            "Network Penetration",
            "API Exploit",
            "System Compromise"
        ]),
        "description": f"Infiltrate {target['name']} and extract sensitive data.",
        "difficulty": base_difficulty,
        "target": target["ip"],
        "reward": base_reward,
        "rep_reward": rep_reward,
        "completed": False,
        "steps": steps,
        "current_step": 0
    }
    
    game_state.missions.append(mission)
    return mission

def generate_new_championship() -> Dict:
    """Generate a new championship challenge"""
    # Calculate difficulty based on player skills and reputation
    avg_skill = sum(game_state.player["skills"].values()) / len(game_state.player["skills"])
    rep_factor = game_state.player["reputation"] / 50  # Scale reputation to a smaller factor
    base_difficulty = max(2, min(8, round((avg_skill + rep_factor) * random.uniform(0.9, 1.3))))
    
    # Generate a new target with higher security
    new_target = {
        "ip": generate_random_ip(),
        "name": random.choice([
            "Government Contractor", 
            "Financial Institution", 
            "Tech Giant Intranet",
            "Military Contractor",
            "Intelligence Agency Database",
            "Major Bank Network",
            "Critical Infrastructure",
            "Cryptocurrency Exchange"
        ]),
        "security_level": base_difficulty,
        "services": random.sample(["http", "https", "ftp", "ssh", "telnet", "smtp", "mysql", "dns"], 
                                 random.randint(3, 6)),
        "vulnerabilities": random.sample([
            "outdated_software", "weak_password", "sql_injection", "xss", 
            "csrf", "directory_traversal", "rce", "default_credentials"
        ], random.randint(1, 2)),
        "discovered": False
    }
    game_state.network_targets.append(new_target)
    
    # Prepare championship tasks (more complex than regular missions)
    tasks = ["network scan", "infiltration"]
    # Add 2-4 more tasks based on difficulty
    possible_tasks = [
        "data extraction", "cover tracks", "plant backdoor", 
        "bypass firewall", "exploit zero-day", "credential theft",
        "privilege escalation", "lateral movement"
    ]
    tasks.extend(random.sample(possible_tasks, min(base_difficulty, len(possible_tasks))))
    
    # Calculate rewards (higher than regular missions)
    base_reward = 0.005 * base_difficulty * random.uniform(0.9, 1.3)
    rep_reward = 15 * base_difficulty
    
    # Required reputation to participate
    required_rep = base_difficulty * 10
    
    # Create new championship
    championship_id = f"c{random.randint(100, 999)}"
    championship = {
        "id": championship_id,
        "title": random.choice([
            "Elite Hacker Tournament",
            "Black Hat Challenge",
            "Dark Web Competition",
            "Cyber Warfare Simulation",
            "Hacker Olympics",
            "Digital Fortress Breach",
            "Cryptowar Challenge"
        ]),
        "description": f"A challenging hacking competition targeting {new_target['name']}.",
        "difficulty": base_difficulty,
        "target": new_target["ip"],
        "reward": base_reward,
        "rep_reward": rep_reward,
        "required_rep": required_rep,
        "completed": False,
        "tasks": tasks,
        "current_task": 0
    }
    
    game_state.championships.append(championship)
    return championship

# Terminal command parsing and execution
def execute_command(command_str: str) -> None:
    """Parse and execute a terminal command"""
    game_state.stats["commands_executed"] += 1
    
    if not command_str.strip():
        return
    
    # Split the command and arguments
    parts = command_str.strip().split(None, 1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    # Log the command
    add_to_history(f"$ {command_str}", Fore.BLUE)
    
    # Execute based on command
    if command == "exit" or command == "quit":
        confirm = input(Fore.YELLOW + "Save game before exiting? (y/n): ").lower()
        if confirm == "y" or confirm == "yes":
            save_game()
        print(Fore.GREEN + "Exiting HackOS. Goodbye!")
        sys.exit(0)
    
    elif command == "help":
        show_help(args)
    
    elif command == "clear" or command == "cls":
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header()
    
    elif command == "save":
        save_game()
    
    elif command == "load":
        load_game()
        print_header()
    
    elif command == "stats":
        display_player_stats()
    
    elif command == "pc":
        display_pc_stats()
    
    elif command == "skills":
        display_skills()
    
    elif command == "history":
        count = 10
        if args and args.isdigit():
            count = int(args)
        display_history(count)
    
    # File system commands
    elif command == "ls":
        cmd_ls(args)
    
    elif command == "cd":
        cmd_cd(args)
    
    elif command == "pwd":
        cmd_pwd()
    
    elif command == "cat":
        cmd_cat(args)
    
    elif command == "mkdir":
        cmd_mkdir(args)
    
    elif command == "touch":
        cmd_touch(args)
    
    elif command == "rm":
        cmd_rm(args)
    
    elif command == "rmdir":
        cmd_rmdir(args)
    
    elif command == "echo":
        cmd_echo(args)
    
    # Game-specific commands
    elif command == "connect":
        cmd_connect(args)
    
    elif command == "disconnect":
        cmd_disconnect()
    
    elif command == "scan":
        cmd_scan(args)
    
    elif command == "hack" or command == "exploit":
        cmd_hack(args)
    
    elif command == "bruteforce":
        cmd_bruteforce(args)
    
    elif command == "mission":
        cmd_mission(args)
    
    elif command == "shop" or command == "upgrade":
        cmd_shop(args)
    
    elif command == "btc" or command == "bitcoin":
        cmd_bitcoin()
    
    elif command == "run":
        cmd_run(args)
    
    else:
        print(Fore.RED + f"Command not found: {command}")
        print(Fore.YELLOW + "Type 'help' to see available commands.")

def show_help(args: str) -> None:
    """Display help information"""
    if not args:
        print(Fore.CYAN + "===== HELP =====")
        print(Fore.YELLOW + "Core Commands:")
        print(Fore.GREEN + "  help [topic]      - Show help (general or specific topic)")
        print(Fore.GREEN + "  exit, quit        - Exit the game")
        print(Fore.GREEN + "  save              - Save the game")
        print(Fore.GREEN + "  load              - Load a saved game")
        print(Fore.GREEN + "  clear, cls        - Clear the screen")
        print(Fore.GREEN + "  history [count]   - Show command history")
        
        print(Fore.YELLOW + "\nFile System Commands:")
        print(Fore.GREEN + "  ls [path]         - List directory contents")
        print(Fore.GREEN + "  cd [path]         - Change directory")
        print(Fore.GREEN + "  pwd               - Print working directory")
        print(Fore.GREEN + "  cat <file>        - Display file contents")
        print(Fore.GREEN + "  mkdir <dir>       - Create a directory")
        print(Fore.GREEN + "  touch <file>      - Create a file")
        print(Fore.GREEN + "  rm <file>         - Remove a file")
        print(Fore.GREEN + "  rmdir <dir>       - Remove a directory")
        print(Fore.GREEN + "  echo <text>       - Display text")
        
        print(Fore.YELLOW + "\nGame Commands:")
        print(Fore.GREEN + "  connect <site>    - Connect to a darkweb site")
        print(Fore.GREEN + "  disconnect        - Disconnect from current site")
        print(Fore.GREEN + "  scan <ip>         - Scan an IP address")
        print(Fore.GREEN + "  hack <ip>         - Hack/exploit a target")
        print(Fore.GREEN + "  bruteforce <ip>   - Bruteforce attack a target")
        print(Fore.GREEN + "  mission [id]      - View or accept missions")
        print(Fore.GREEN + "  shop, upgrade     - Access upgrade shop")
        print(Fore.GREEN + "  btc, bitcoin      - Check Bitcoin balance")
        print(Fore.GREEN + "  run <tool>        - Run a tool")
        print(Fore.GREEN + "  stats             - Display player statistics")
        print(Fore.GREEN + "  pc                - Display PC specifications")
        print(Fore.GREEN + "  skills            - Display hacker skills")
        
        print(Fore.YELLOW + "\nFor more detailed help on a specific command, type 'help <command>'")
    else:
        topic = args.strip().lower()
        
        # Help topics
        help_topics = {
            "connect": "Connect to darkweb sites:\n" +
                       "  connect bitcoinhub.onion - Check your Bitcoin balance\n" +
                       "  connect globalch.onion   - Access hacking missions\n" +
                       "  connect champions.onion  - Participate in hacking championships",
                       
            "scan": "Scan an IP address to gather information about the target:\n" +
                   "  scan <ip> - Scan the specified IP address\n" +
                   "Example: scan 192.168.1.1",
                   
            "hack": "Hack/exploit a target system:\n" +
                   "  hack <ip> - Attempt to exploit a vulnerability in the target\n" +
                   "Example: hack 192.168.1.1",
                   
            "bruteforce": "Bruteforce attack on a target:\n" +
                         "  bruteforce <ip> [service] - Attempt to crack passwords\n" +
                         "Example: bruteforce 192.168.1.1 ssh",
                         
            "mission": "View or manage missions:\n" +
                      "  mission           - View available missions\n" +
                      "  mission list      - List all missions\n" +
                      "  mission info <id> - Show details about a mission\n" +
                      "  mission accept <id> - Accept a mission",
                      
            "shop": "Access the upgrade shop to improve your PC:\n" +
                   "  shop               - View available upgrades\n" +
                   "  shop <component>   - View upgrades for a specific component\n" +
                   "  upgrade <component> <level> - Purchase an upgrade\n" +
                   "Example: upgrade cpu 2",
        }
        
        if topic in help_topics:
            print(Fore.CYAN + f"===== HELP: {topic.upper()} =====")
            print(Fore.GREEN + help_topics[topic])
        else:
            print(Fore.YELLOW + f"No help available for '{topic}'. Type 'help' for a list of commands.")

# File system command implementations
def cmd_ls(args: str) -> None:
    """List directory contents"""
    path = args.strip() if args else "."
    target_path = resolve_path(path)
    
    if target_path is None:
        print(Fore.RED + f"Path not found: {path}")
        return
    
    # Navigate to the target directory
    current = game_state.file_system
    path_parts = target_path.split('/') if target_path else []
    
    for part in [p for p in path_parts if p]:
        if part not in current or current[part]["type"] != "dir":
            print(Fore.RED + f"Not a directory: {part}")
            return
        current = current[part]["content"]
    
    # Display the directory contents
    dirs = []
    files = []
    
    for name, item in current.items():
        if item["type"] == "dir":
            dirs.append(name)
        else:
            files.append(name)
    
    # Sort alphabetically
    dirs.sort()
    files.sort()
    
    # Print directories first
    for d in dirs:
        print(Fore.BLUE + d + "/")
    
    # Then files
    for f in files:
        print(Fore.WHITE + f)

def cmd_cd(args: str) -> None:
    """Change directory"""
    path = args.strip() if args else "~"
    target_path = resolve_path(path)
    
    if target_path is None:
        print(Fore.RED + f"Path not found: {path}")
        return
    
    # Check if the target is a directory
    current = game_state.file_system
    path_parts = target_path.split('/') if target_path else []
    
    for part in [p for p in path_parts if p]:
        if part not in current or current[part]["type"] != "dir":
            print(Fore.RED + f"Not a directory: {part}")
            return
        current = current[part]["content"]
    
    game_state.current_dir = target_path

def cmd_pwd() -> None:
    """Print working directory"""
    print(game_state.current_dir)

def cmd_cat(args: str) -> None:
    """Display file contents"""
    if not args:
        print(Fore.RED + "Usage: cat <file>")
        return
    
    path = args.strip()
    file_path, file_name = os.path.split(path)
    
    # Resolve directory path
    dir_path = resolve_path(file_path) if file_path else resolve_path(".")
    
    if dir_path is None:
        print(Fore.RED + f"Path not found: {file_path}")
        return
    
    # Navigate to the directory
    current = game_state.file_system
    path_parts = dir_path.split('/') if dir_path else []
    
    for part in [p for p in path_parts if p]:
        if part not in current or current[part]["type"] != "dir":
            print(Fore.RED + f"Not a directory: {part}")
            return
        current = current[part]["content"]
    
    # Check if the file exists
    if file_name not in current or current[file_name]["type"] != "file":
        print(Fore.RED + f"No such file: {file_name}")
        return
    
    # Display file contents
    print(current[file_name]["content"])

def cmd_mkdir(args: str) -> None:
    """Create a directory"""
    if not args:
        print(Fore.RED + "Usage: mkdir <directory>")
        return
    
    path = args.strip()
    dir_path, dir_name = os.path.split(path)
    
    if not dir_name:
        print(Fore.RED + "Invalid directory name")
        return
    
    # Resolve parent directory path
    parent_path = resolve_path(dir_path) if dir_path else resolve_path(".")
    
    if parent_path is None:
        print(Fore.RED + f"Path not found: {dir_path}")
        return
    
    # Navigate to the parent directory
    current = game_state.file_system
    path_parts = parent_path.split('/') if parent_path else []
    
    for part in [p for p in path_parts if p]:
        if part not in current or current[part]["type"] != "dir":
            print(Fore.RED + f"Not a directory: {part}")
            return
        current = current[part]["content"]
    
    # Check if the directory already exists
    if dir_name in current:
        print(Fore.RED + f"Directory already exists: {dir_name}")
        return
    
    # Create the directory
    current[dir_name] = {
        "type": "dir",
        "content": {}
    }
    
    print(Fore.GREEN + f"Directory created: {dir_name}")

def cmd_touch(args: str) -> None:
    """Create a file"""
    if not args:
        print(Fore.RED + "Usage: touch <file>")
        return
    
    path = args.strip()
    file_path, file_name = os.path.split(path)
    
    if not file_name:
        print(Fore.RED + "Invalid file name")
        return
    
    # Resolve directory path
    dir_path = resolve_path(file_path) if file_path else resolve_path(".")
    
    if dir_path is None:
        print(Fore.RED + f"Path not found: {file_path}")
        return
    
    # Navigate to the directory
    current = game_state.file_system
    path_parts = dir_path.split('/') if dir_path else []
    
    for part in [p for p in path_parts if p]:
        if part not in current or current[part]["type"] != "dir":
            print(Fore.RED + f"Not a directory: {part}")
            return
        current = current[part]["content"]
    
    # Check if the file already exists
    if file_name in current and current[file_name]["type"] == "file":
        # Just update the timestamp (not actually implemented)
        print(Fore.YELLOW + f"File exists, timestamp updated: {file_name}")
        return
    
    # Create the file
    current[file_name] = {
        "type": "file",
        "content": ""
    }
    
    print(Fore.GREEN + f"File created: {file_name}")

def cmd_rm(args: str) -> None:
    """Remove a file"""
    if not args:
        print(Fore.RED + "Usage: rm <file>")
        return
    
    path = args.strip()
    file_path, file_name = os.path.split(path)
    
    # Resolve directory path
    dir_path = resolve_path(file_path) if file_path else resolve_path(".")
    
    if dir_path is None:
        print(Fore.RED + f"Path not found: {file_path}")
        return
    
    # Navigate to the directory
    current = game_state.file_system
    path_parts = dir_path.split('/') if dir_path else []
    
    for part in [p for p in path_parts if p]:
        if part not in current or current[part]["type"] != "dir":
            print(Fore.RED + f"Not a directory: {part}")
            return
        current = current[part]["content"]
    
    # Check if the file exists
    if file_name not in current or current[file_name]["type"] != "file":
        print(Fore.RED + f"No such file: {file_name}")
        return
    
    # Remove the file
    del current[file_name]
    print(Fore.GREEN + f"File removed: {file_name}")

def cmd_rmdir(args: str) -> None:
    """Remove a directory"""
    if not args:
        print(Fore.RED + "Usage: rmdir <directory>")
        return
    
    path = args.strip()
    dir_path, dir_name = os.path.split(path)
    
    # Resolve parent directory path
    parent_path = resolve_path(dir_path) if dir_path else resolve_path(".")
    
    if parent_path is None:
        print(Fore.RED + f"Path not found: {dir_path}")
        return
    
    # Navigate to the parent directory
    current = game_state.file_system
    path_parts = parent_path.split('/') if parent_path else []
    
    for part in [p for p in path_parts if p]:
        if part not in current or current[part]["type"] != "dir":
            print(Fore.RED + f"Not a directory: {part}")
            return
        current = current[part]["content"]
    
    # Check if the directory exists
    if dir_name not in current or current[dir_name]["type"] != "dir":
        print(Fore.RED + f"No such directory: {dir_name}")
        return
    
    # Check if the directory is empty
    if current[dir_name]["content"]:
        print(Fore.RED + f"Directory not empty: {dir_name}")
        return
    
    # Remove the directory
    del current[dir_name]
    print(Fore.GREEN + f"Directory removed: {dir_name}")

def cmd_echo(args: str) -> None:
    """Echo text to the terminal"""
    print(args)

def resolve_path(path: str) -> Optional[str]:
    """Resolve a file system path"""
    if not path:
        return game_state.current_dir
    
    # Handle absolute paths
    if path.startswith("~") or path.startswith("/"):
        return path.replace("/", "~", 1) if path.startswith("/") else path
    
    # Handle relative paths
    if path == ".":
        return game_state.current_dir
    
    if path == "..":
        if game_state.current_dir == "~":
            return "~"
        return os.path.dirname(game_state.current_dir)
    
    # General case
    return os.path.normpath(os.path.join(game_state.current_dir, path))

# Game-specific command implementations
def cmd_connect(args: str) -> None:
    """Connect to a darkweb site"""
    if not args:
        print(Fore.RED + "Usage: connect <site>")
        print(Fore.YELLOW + "Available sites: bitcoinhub.onion, globalch.onion, champions.onion")
        
        # Show additional sites if reputation is high enough
        if game_state.player["fsociety_member"]:
            print(Fore.YELLOW + "Fsociety sites: fsociety.onion, ecorp-internal.onion")
        elif game_state.player["reputation"] >= FSOCIETY_REP_THRESHOLD:
            print(Fore.YELLOW + "Additional sites: fsociety.onion (requires membership)")
        
        if game_state.player["dark_army_contact"]:
            print(Fore.RED + "Dark Army sites: dark-army.onion")
        elif game_state.player["reputation"] >= DARK_ARMY_REP_THRESHOLD:
            print(Fore.RED + "Additional sites: dark-army.onion (requires contact)")
        
        return
    
    site = args.strip().lower()
    
    available_sites = ["bitcoinhub.onion", "globalch.onion", "champions.onion"]
    fsociety_sites = ["fsociety.onion", "ecorp-internal.onion"]
    dark_army_sites = ["dark-army.onion"]
    
    # Check if site is available
    if site in available_sites:
        # Standard sites anyone can access
        pass
    elif site in fsociety_sites and not game_state.player["fsociety_member"]:
        # Only fsociety members can access
        if game_state.player["reputation"] >= FSOCIETY_REP_THRESHOLD:
            print(Fore.YELLOW + "This site requires fsociety membership. Complete more fsociety-related missions first.")
        else:
            print(Fore.RED + f"Site {site} not found or unavailable.")
        return
    elif site in dark_army_sites and not game_state.player["dark_army_contact"]:
        # Only Dark Army contacts can access
        if game_state.player["reputation"] >= DARK_ARMY_REP_THRESHOLD:
            print(Fore.YELLOW + "This site requires Dark Army contact. Complete more advanced missions first.")
        else:
            print(Fore.RED + f"Site {site} not found or unavailable.")
        return
    elif site not in available_sites + fsociety_sites + dark_army_sites:
        print(Fore.RED + f"Unknown site: {site}")
        print(Fore.YELLOW + "Available sites: bitcoinhub.onion, globalch.onion, champions.onion")
        return
    
    print(Fore.CYAN + f"Connecting to {site} via encrypted Tor channel...")
    
    # Randomize connection time for realism
    connecting_time = random.uniform(0.8, 2.0)
    time.sleep(connecting_time)
    
    # Random chance of connection failure - higher for secure sites
    failure_chance = 0.05  # 5% base chance
    
    # Modify chance based on PC security level and network
    security_factor = game_state.pc["security"]["level"] / 20  # Up to 0.4 reduction
    network_factor = game_state.pc["network"]["level"] / 20   # Up to 0.4 reduction
    
    adjusted_failure = max(0.01, failure_chance - security_factor - network_factor)
    
    # Increase failure chance for restricted sites
    if site in fsociety_sites + dark_army_sites:
        adjusted_failure *= 2
    
    if random.random() < adjusted_failure:
        print(Fore.RED + "Connection failed. The site might be down or monitored.")
        return
    
    game_state.connected_to_darkweb = True
    game_state.current_site = site
    
    print(Fore.GREEN + f"Connected to {site}")
    
    # Display site content
    if site == "bitcoinhub.onion":
        display_bitcoinhub()
    elif site == "globalch.onion":
        display_globalch()
    elif site == "champions.onion":
        display_champions()
    elif site == "fsociety.onion":
        display_fsociety()
    elif site == "ecorp-internal.onion":
        display_ecorp_internal()
    elif site == "dark-army.onion":
        display_dark_army()

def cmd_disconnect() -> None:
    """Disconnect from the current darkweb site"""
    if not game_state.connected_to_darkweb:
        print(Fore.YELLOW + "Not connected to any site.")
        return
    
    site = game_state.current_site
    print(Fore.CYAN + f"Disconnecting from {site}...")
    time.sleep(0.5)  # Simulate disconnection time
    
    game_state.connected_to_darkweb = False
    game_state.current_site = None
    
    print(Fore.GREEN + f"Disconnected from {site}")

def display_bitcoinhub() -> None:
    """Display the BitcoinHub site"""
    print(Fore.CYAN + "===== BITCOINHUB.ONION =====")
    print(Fore.YELLOW + "Current Bitcoin Price: " + Fore.GREEN + f"${DEFAULT_BTC_VALUE:,.2f} USD")
    print(Fore.YELLOW + "Your Balance: " + Fore.GREEN + f"{format_btc(game_state.player['bitcoin'])}")
    print(Fore.YELLOW + "USD Value: " + Fore.GREEN + f"${get_btc_usd_value(game_state.player['bitcoin']):,.2f}")
    
    print("\n" + Fore.CYAN + "===== TRANSACTION HISTORY =====")
    print(Fore.YELLOW + "Total Earned: " + Fore.GREEN + f"{format_btc(game_state.stats['bitcoin_earned'])}")
    print(Fore.YELLOW + "Total Spent: " + Fore.GREEN + f"{format_btc(game_state.stats['bitcoin_spent'])}")
    
    print("\n" + Fore.YELLOW + "Type 'disconnect' to return to the terminal.")

def display_globalch() -> None:
    """Display the Global Hacker Chat site"""
    print(Fore.CYAN + "===== GLOBALCH.ONION =====")
    print(Fore.YELLOW + "Welcome to the Global Hacker Chat")
    print(Fore.GREEN + "Current Users Online: " + str(random.randint(20, 100)))
    
    print("\n" + Fore.CYAN + "===== AVAILABLE MISSIONS =====")
    
    available_missions = [m for m in game_state.missions if not m["completed"]]
    if not available_missions:
        print(Fore.YELLOW + "No missions available. Check back later.")
        # Generate a new mission
        new_mission = generate_new_mission()
        print(Fore.GREEN + f"New mission received: {new_mission['title']} (ID: {new_mission['id']})")
    else:
        for i, mission in enumerate(available_missions):
            print(f"{Fore.GREEN}[{mission['id']}] {Fore.YELLOW}{mission['title']} - " + 
                  f"Difficulty: {mission['difficulty']}, " + 
                  f"Reward: {format_btc(mission['reward'])}")
    
    print("\n" + Fore.YELLOW + "Commands:")
    print(Fore.GREEN + "  mission list      - List all missions")
    print(Fore.GREEN + "  mission info <id> - Show mission details")
    print(Fore.GREEN + "  mission accept <id> - Accept a mission")
    print(Fore.GREEN + "  disconnect       - Return to terminal")

def display_champions() -> None:
    """Display the Hacker Championships site"""
    print(Fore.CYAN + "===== CHAMPIONS.ONION =====")
    print(Fore.YELLOW + "Welcome to the Elite Hacker Championships")
    print(Fore.GREEN + f"Your Reputation: {game_state.player['reputation']}")
    
    print("\n" + Fore.CYAN + "===== AVAILABLE CHAMPIONSHIPS =====")
    
    available_championships = []
    for championship in game_state.championships:
        if not championship["completed"] and game_state.player["reputation"] >= championship["required_rep"]:
            # Skip fsociety/dark army restricted championships if not a member
            if championship.get("fsociety_required", False) and not game_state.player["fsociety_member"]:
                continue
            if championship.get("dark_army_required", False) and not game_state.player["dark_army_contact"]:
                continue
            available_championships.append(championship)
    
    if not available_championships:
        if game_state.player["reputation"] < 20:
            print(Fore.YELLOW + "You need at least 20 reputation points to participate in championships.")
        else:
            print(Fore.YELLOW + "No championships available. Check back later.")
            # Generate a new championship if the player has enough reputation
            new_championship = generate_new_championship()
            print(Fore.GREEN + f"New championship announced: {new_championship['title']} (ID: {new_championship['id']})")
    else:
        for i, championship in enumerate(available_championships):
            # Display fsociety/dark army tags
            special_tag = ""
            if championship.get("fsociety_required", False):
                special_tag = f"{Fore.RED}[fsociety] "
            elif championship.get("dark_army_required", False):
                special_tag = f"{Fore.RED}[Dark Army] "
                
            print(f"{Fore.GREEN}[{championship['id']}] {special_tag}{Fore.YELLOW}{championship['title']} - " + 
                  f"Difficulty: {championship['difficulty']}, " + 
                  f"Reward: {format_btc(championship['reward'])}")
    
    print("\n" + Fore.YELLOW + "Commands:")
    print(Fore.GREEN + "  championship list      - List all championships")
    print(Fore.GREEN + "  championship info <id> - Show championship details")
    print(Fore.GREEN + "  championship join <id> - Join a championship")
    print(Fore.GREEN + "  disconnect            - Return to terminal")

def display_fsociety() -> None:
    """Display the fsociety site"""
    print(Fore.RED + "===== FSOCIETY.ONION =====")
    print(Fore.WHITE + "Welcome, comrade. The revolution needs you.")
    
    # Promote to member if not already
    if not game_state.player["fsociety_member"]:
        game_state.player["fsociety_member"] = True
        print(Fore.GREEN + "CONGRATULATIONS! You are now officially a member of fsociety.")
        print(Fore.GREEN + "Your home directory now has access to additional fsociety tools.")
        
        # Add fsociety folder content
        fs_tools = game_state.file_system["~"]["content"]["fsociety"]["content"]
        fs_tools.clear()  # Remove the locked.txt
        fs_tools.update({
            "stage1.txt": {
                "type": "file",
                "content": "FIVE/NINE ATTACK PLAN\n\nStage 1: Reconnaissance of E Corp systems\nStage 2: Develop encryption malware\nStage 3: Plant backdoors in critical systems\nStage 4: Synchronize attack across all systems\nStage 5: Destroy encryption keys\n\nCurrent Status: Planning Phase"
            },
            "mr_robot.py": {
                "type": "file",
                "content": "# Advanced data destruction tool\n# Usage: run mr_robot.py <target_ip>\n\n# WARNING: This will permanently and irrecoverably encrypt all data\n# Use only as directed by fsociety leadership\n# Current status: DEVELOPMENT MODE - Will not execute actual encryption"
            }
        })
    
    print(Fore.YELLOW + "\n===== FSOCIETY OPERATIONS =====")
    print(Fore.WHITE + "Current mission: Five/Nine Attack on E Corp")
    print(Fore.WHITE + "Status: Preparing")
    
    # Count fsociety-related missions completed
    fsociety_missions_completed = 0
    for mission in game_state.missions:
        if mission.get("fsociety_related", False) and mission["completed"]:
            fsociety_missions_completed += 1
    
    print(Fore.WHITE + f"Mission progress: {fsociety_missions_completed}/3 preparatory missions completed")
    
    if fsociety_missions_completed >= 2:
        print(Fore.GREEN + "\nYou're making excellent progress. The E Corp attack will soon be ready.")
        print(Fore.GREEN + "Check for new high-level missions and championships.")
    else:
        print(Fore.YELLOW + "\nYou need to complete more preparatory missions before the main attack.")
        print(Fore.YELLOW + "Look for missions marked with [fsociety] tags.")
    
    print("\n" + Fore.WHITE + "Commands:")
    print(Fore.GREEN + "  disconnect - Return to terminal")

def display_ecorp_internal() -> None:
    """Display the E Corp internal site"""
    print(Fore.BLUE + "===== ECORP-INTERNAL.ONION =====")
    print(Fore.WHITE + "E Corp Employee Portal")
    print(Fore.RED + "[UNAUTHORIZED ACCESS DETECTED]")
    
    print(Fore.YELLOW + "\n===== SYSTEM INFORMATION =====")
    print(Fore.WHITE + "Server: E Corp Global Financial Database")
    print(Fore.WHITE + "Access Level: Restricted")
    print(Fore.WHITE + "Systems Available: Loan Management, Credit Processing, E-Coin Transaction Verification")
    
    print(Fore.RED + "\nWARNING: This access is being logged and monitored.")
    print(Fore.RED + "Multiple access attempts may trigger security protocols.")
    
    # Give the player some E-Coins as a reward for accessing
    if game_state.player["ecoin"] == 0:
        ecoin_reward = 25.0
        game_state.player["ecoin"] = ecoin_reward
        print(Fore.GREEN + f"\nAccessed E-Coin test account. {ecoin_reward} E-Coins have been transferred to your wallet.")
    
    print("\n" + Fore.WHITE + "Commands:")
    print(Fore.GREEN + "  disconnect - Return to terminal (RECOMMENDED)")

def display_dark_army() -> None:
    """Display the Dark Army site"""
    print(Fore.RED + "===== DARK-ARMY.ONION =====")
    print(Fore.WHITE + "你好, welcome. 白玫瑰 is watching.")  # "Hello" and "White Rose" in Chinese
    
    # Promote to Dark Army contact if not already
    if not game_state.player["dark_army_contact"]:
        game_state.player["dark_army_contact"] = True
        print(Fore.RED + "Your skills have been noticed. The Dark Army is now in contact with you.")
        print(Fore.RED + "New missions and resources will become available.")
        
        # Add reputation bonus for making Dark Army contact
        reputation_bonus = 25
        game_state.player["reputation"] += reputation_bonus
        game_state.stats["reputation_earned"] += reputation_bonus
        print(Fore.GREEN + f"Reputation increased by {reputation_bonus} points.")
    
    print(Fore.RED + "\n===== CURRENT DIRECTIVES =====")
    print(Fore.WHITE + "1. Monitor fsociety activities")
    print(Fore.WHITE + "2. Prepare alternative encryption channels")
    print(Fore.WHITE + "3. Stand ready for Stage 2")
    
    print(Fore.RED + "\nRemember: We are always watching. Loyalty is expected.")
    
    print("\n" + Fore.WHITE + "Commands:")
    print(Fore.GREEN + "  disconnect - Return to terminal")

def cmd_scan(args: str) -> None:
    """Scan an IP address"""
    if not args:
        print(Fore.RED + "Usage: scan <ip>")
        return
    
    target_ip = args.strip()
    
    # Validate IP format
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target_ip):
        print(Fore.RED + f"Invalid IP address format: {target_ip}")
        return
    
    # Check if the IP exists in our targets
    target = get_target_by_ip(target_ip)
    
    if not target:
        # Generate a random target with this IP
        security_level = random.randint(1, 5)
        target = {
            "ip": target_ip,
            "name": random.choice([
                "Unknown Server", 
                "Private Host", 
                "Network Device",
                "Cloud Instance",
                "Web Server",
                "Database Server"
            ]),
            "security_level": security_level,
            "services": random.sample(["http", "https", "ftp", "ssh", "telnet", "smtp", "mysql"], 
                                     random.randint(1, 4)),
            "vulnerabilities": random.sample([
                "outdated_software", "weak_password", "sql_injection", "xss", 
                "csrf", "directory_traversal", "rce", "default_credentials"
            ], random.randint(0, 2)),
            "discovered": False
        }
        game_state.network_targets.append(target)
    
    # Perform the scan
    print(Fore.CYAN + f"Scanning {target_ip}...")
    
    # Calculate time based on network speed
    scan_time = 5.0 / (game_state.pc["network"]["speed"] / 10 + 0.1)  # 0.5 to 5 seconds
    scan_time = max(0.5, min(5, scan_time))
    
    # Scan animation
    for i in range(10):
        progress = i / 10
        bar_length = 40
        completed_length = int(bar_length * progress)
        
        progress_bar = f"[{Fore.GREEN}{'█' * completed_length}{'░' * (bar_length - completed_length)}{Style.RESET_ALL}]"
        percentage = int(progress * 100)
        
        sys.stdout.write(f"\r{progress_bar} {percentage}% ")
        sys.stdout.flush()
        time.sleep(scan_time / 10)
    
    print()  # Newline after progress bar
    
    # Mark as discovered
    target["discovered"] = True
    new_discovery = discover_ip(target_ip)
    
    # Check for skill improvement
    skill_level_up_check("network")
    
    # Display scan results
    print(Fore.GREEN + "Scan completed!")
    if new_discovery:
        print(Fore.GREEN + "New target discovered!")
    
    print(Fore.YELLOW + "Target Information:")
    print(Fore.GREEN + f"IP: {target['ip']}")
    print(Fore.GREEN + f"Host: {target['name']}")
    print(Fore.GREEN + f"Security Level: {target['security_level']}/5")
    print(Fore.GREEN + f"Open Services: {', '.join(target['services'])}")
    
    # Show vulnerabilities with a chance based on PC power and skills
    detection_chance = (get_pc_power_level() * game_state.player["skills"]["network"]) / 20
    if random.random() < detection_chance and target["vulnerabilities"]:
        print(Fore.GREEN + f"Vulnerabilities Detected: {', '.join(target['vulnerabilities'])}")
    else:
        print(Fore.YELLOW + "No vulnerabilities detected. Consider upgrading your scanning tools.")
    
    # Check for mission/championship progress
    if game_state.player["current_mission"]:
        update_mission_progress(target_ip, "scan")

def cmd_hack(args: str) -> None:
    """Hack a target system"""
    if not args:
        print(Fore.RED + "Usage: hack <ip>")
        return
    
    target_ip = args.strip()
    
    # Validate IP format
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target_ip):
        print(Fore.RED + f"Invalid IP address format: {target_ip}")
        return
    
    # Attempt to hack
    perform_hack(target_ip, "exploit")

def cmd_bruteforce(args: str) -> None:
    """Bruteforce attack on a target"""
    if not args:
        print(Fore.RED + "Usage: bruteforce <ip> [service]")
        return
    
    parts = args.strip().split()
    target_ip = parts[0]
    service = parts[1] if len(parts) > 1 else "ssh"  # Default to SSH
    
    # Validate IP format
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target_ip):
        print(Fore.RED + f"Invalid IP address format: {target_ip}")
        return
    
    # Check if the service exists on the target
    target = get_target_by_ip(target_ip)
    if target and target["discovered"] and service not in target["services"]:
        print(Fore.RED + f"Service {service} not available on {target_ip}")
        return
    
    # Attempt to bruteforce
    print(Fore.CYAN + f"Bruteforcing {service} on {target_ip}...")
    perform_hack(target_ip, "bruteforce")

def cmd_mission(args: str) -> None:
    """Manage missions"""
    if not game_state.connected_to_darkweb or game_state.current_site != "globalch.onion":
        print(Fore.RED + "You need to connect to globalch.onion to access missions.")
        return
    
    if not args:
        # Show available missions
        available_missions = [m for m in game_state.missions if not m["completed"]]
        print(Fore.CYAN + "===== AVAILABLE MISSIONS =====")
        
        if not available_missions:
            print(Fore.YELLOW + "No missions available. Check back later.")
        else:
            for mission in available_missions:
                print(f"{Fore.GREEN}[{mission['id']}] {Fore.YELLOW}{mission['title']} - " + 
                      f"Difficulty: {mission['difficulty']}, " + 
                      f"Reward: {format_btc(mission['reward'])}")
        return
    
    # Parse command
    parts = args.strip().split(None, 1)
    subcommand = parts[0].lower()
    
    if subcommand == "list":
        # List all missions (including completed)
        print(Fore.CYAN + "===== ALL MISSIONS =====")
        if not game_state.missions:
            print(Fore.YELLOW + "No missions available.")
        else:
            for mission in game_state.missions:
                status = Fore.GREEN + "COMPLETED" if mission["completed"] else Fore.YELLOW + "AVAILABLE"
                print(f"{Fore.CYAN}[{mission['id']}] {Fore.YELLOW}{mission['title']} - {status}")
    
    elif subcommand == "info":
        # Show details about a specific mission
        if len(parts) < 2:
            print(Fore.RED + "Usage: mission info <id>")
            return
        
        mission_id = parts[1].strip()
        mission = get_mission_by_id(mission_id)
        
        if not mission:
            print(Fore.RED + f"Mission {mission_id} not found.")
            return
        
        print(Fore.CYAN + f"===== MISSION: {mission['title']} =====")
        print(Fore.YELLOW + f"ID: {Fore.GREEN}{mission['id']}")
        print(Fore.YELLOW + f"Description: {Fore.GREEN}{mission['description']}")
        print(Fore.YELLOW + f"Difficulty: {Fore.GREEN}{mission['difficulty']}/5")
        print(Fore.YELLOW + f"Target: {Fore.GREEN}{mission['target']}")
        print(Fore.YELLOW + f"Reward: {Fore.GREEN}{format_btc(mission['reward'])} and {mission['rep_reward']} reputation")
        
        if mission["completed"]:
            print(Fore.GREEN + "Status: COMPLETED")
        else:
            print(Fore.YELLOW + f"Status: {mission['current_step']}/{len(mission['steps'])} steps completed")
            print(Fore.YELLOW + f"Steps: {Fore.GREEN}{' → '.join(mission['steps'])}")
    
    elif subcommand == "accept":
        # Accept a mission
        if len(parts) < 2:
            print(Fore.RED + "Usage: mission accept <id>")
            return
        
        mission_id = parts[1].strip()
        mission = get_mission_by_id(mission_id)
        
        if not mission:
            print(Fore.RED + f"Mission {mission_id} not found.")
            return
        
        if mission["completed"]:
            print(Fore.YELLOW + f"Mission {mission_id} has already been completed.")
            return
        
        if game_state.player["current_mission"]:
            current = get_mission_by_id(game_state.player["current_mission"])
            print(Fore.YELLOW + f"You already have an active mission: {current['title']}")
            confirm = input(Fore.YELLOW + "Abandon current mission? (y/n): ").lower()
            if confirm != "y" and confirm != "yes":
                return
        
        game_state.player["current_mission"] = mission_id
        print(Fore.GREEN + f"Mission accepted: {mission['title']}")
        print(Fore.YELLOW + f"Target: {mission['target']}")
        print(Fore.YELLOW + f"First step: {mission['steps'][0]}")
    
    else:
        print(Fore.RED + f"Unknown mission command: {subcommand}")
        print(Fore.YELLOW + "Available commands: list, info <id>, accept <id>")

def cmd_shop(args: str) -> None:
    """Access the upgrade shop"""
    if not args:
        # Show all components
        print(Fore.CYAN + "===== UPGRADE SHOP =====")
        print(Fore.YELLOW + f"Your Bitcoin: {format_btc(game_state.player['bitcoin'])}")
        print()
        
        print(Fore.CYAN + "Available components for upgrade:")
        print(Fore.GREEN + "  cpu     - Processor upgrades")
        print(Fore.GREEN + "  ram     - Memory upgrades")
        print(Fore.GREEN + "  storage - Storage upgrades")
        print(Fore.GREEN + "  network - Network connection upgrades")
        print(Fore.GREEN + "  security - Security system upgrades")
        
        print()
        print(Fore.YELLOW + "Usage:")
        print(Fore.GREEN + "  shop <component>          - View upgrades for a component")
        print(Fore.GREEN + "  upgrade <component> <level> - Purchase an upgrade")
        return
    
    # Show upgrades for a specific component
    component = args.strip().lower()
    
    if component not in game_state.upgrades:
        print(Fore.RED + f"Unknown component: {component}")
        print(Fore.YELLOW + "Available components: cpu, ram, storage, network, security")
        return
    
    print(Fore.CYAN + f"===== {component.upper()} UPGRADES =====")
    print(Fore.YELLOW + f"Your Bitcoin: {format_btc(game_state.player['bitcoin'])}")
    print(Fore.YELLOW + f"Current level: {game_state.pc[component]['level']}")
    print()
    
    for i, upgrade in enumerate(game_state.upgrades[component]):
        level = i + 1
        current = "CURRENT" if level == game_state.pc[component]["level"] else ""
        available = game_state.player["bitcoin"] >= upgrade["cost"] and level > game_state.pc[component]["level"]
        
        status_color = Fore.GREEN if available else Fore.RED
        if current:
            status_color = Fore.BLUE
        
        print(f"{status_color}Level {level}: {upgrade['name']} - Cost: {format_btc(upgrade['cost'])} {current}")
        
        # Show details based on component type
        if component == "cpu":
            print(f"{status_color}  Cores: {upgrade['cores']}, Speed: {upgrade['speed']} GHz")
        elif component == "ram":
            print(f"{status_color}  Size: {upgrade['size']} MB")
        elif component == "storage":
            print(f"{status_color}  Size: {upgrade['size']} GB")
        elif component == "network":
            print(f"{status_color}  Speed: {upgrade['speed']} Mbps")
        
        print()
    
    print(Fore.YELLOW + "To purchase an upgrade: upgrade <component> <level>")
    print(Fore.YELLOW + "Example: upgrade cpu 2")

def cmd_upgrade(args: str) -> None:
    """Purchase an upgrade"""
    if not args:
        print(Fore.RED + "Usage: upgrade <component> <level>")
        return
    
    parts = args.strip().split()
    if len(parts) < 2:
        print(Fore.RED + "Usage: upgrade <component> <level>")
        return
    
    component = parts[0].lower()
    
    if not parts[1].isdigit():
        print(Fore.RED + "Level must be a number")
        return
    
    level = int(parts[1])
    
    if component not in game_state.upgrades:
        print(Fore.RED + f"Unknown component: {component}")
        print(Fore.YELLOW + "Available components: cpu, ram, storage, network, security")
        return
    
    upgrade_component(component, level)

def cmd_bitcoin() -> None:
    """Check Bitcoin balance"""
    print(Fore.CYAN + "===== BITCOIN WALLET =====")
    print(Fore.YELLOW + f"Balance: {Fore.GREEN}{format_btc(game_state.player['bitcoin'])}")
    print(Fore.YELLOW + f"USD Value: {Fore.GREEN}${get_btc_usd_value(game_state.player['bitcoin']):,.2f}")
    
    print()
    print(Fore.YELLOW + "To check more details, connect to bitcoinhub.onion")

def cmd_run(args: str) -> None:
    """Run a tool or script"""
    if not args:
        print(Fore.RED + "Usage: run <tool> [args]")
        return
    
    parts = args.strip().split(None, 1)
    tool = parts[0]
    tool_args = parts[1] if len(parts) > 1 else ""
    
    # Check if we're in the tools directory
    if (game_state.current_dir != "~/tools" and 
        not os.path.exists(os.path.join(game_state.current_dir, tool))):
        print(Fore.RED + f"Tool not found: {tool}")
        print(Fore.YELLOW + "Make sure you're in the tools directory or specify the full path.")
        return
    
    # Check if the tool exists
    if game_state.current_dir == "~/tools":
        current = game_state.file_system["~"]["content"]["tools"]["content"]
        if tool not in current or current[tool]["type"] != "file":
            print(Fore.RED + f"Tool not found: {tool}")
            return
    
    # Run specific tools
    if tool == "network_scanner.py":
        if not tool_args:
            print(Fore.RED + "Usage: run network_scanner.py <target_ip>")
            return
        
        target_ip = tool_args.strip()
        cmd_scan(target_ip)
    
    elif tool == "bruteforce.py":
        if not tool_args:
            print(Fore.RED + "Usage: run bruteforce.py <target_ip> [service]")
            return
        
        cmd_bruteforce(tool_args)
    
    else:
        print(Fore.YELLOW + f"Running {tool}...")
        time.sleep(1)
        print(Fore.RED + "Error: Unknown or unsupported tool.")

def main():
    """Main function to run the hacker terminal game"""
    # Check terminal size
    term_width, term_height = shutil.get_terminal_size()
    if term_width < MIN_TERMINAL_WIDTH or term_height < MIN_TERMINAL_HEIGHT:
        print(f"Warning: Terminal window too small. Recommended size: {MIN_TERMINAL_WIDTH}x{MIN_TERMINAL_HEIGHT}")
    
    # Try to load saved game
    if os.path.exists(SAVE_FILE):
        load_confirmation = input("Save file found. Load game? (y/n): ").lower()
        if load_confirmation == 'y' or load_confirmation == 'yes':
            load_game()
    
    # Display header
    print_header()
    
    # Display welcome message
    print(Fore.RED + "Welcome to ASATHOT - A Mr. Robot-inspired hacking simulation!")
    print(Fore.YELLOW + "Type 'help' to see available commands.")
    print()
    
    # Main loop
    while True:
        try:
            # Show prompt
            current_dir_display = game_state.current_dir
            if game_state.connected_to_darkweb:
                prompt = f"{Fore.RED}[{game_state.current_site}]{Fore.GREEN} $ "
            else:
                # Customize prompt based on player status
                prompt_user = "elliot"
                prompt_host = "fsociety" if game_state.player["fsociety_member"] else "asathot"
                
                # Add special Dark Army marker if player is part of Dark Army
                if game_state.player["dark_army_contact"]:
                    prompt_user = "whiterose"
                    prompt_host = "darkArmy"
                    
                prompt = f"{Fore.GREEN}{prompt_user}@{prompt_host}:{Fore.BLUE}{current_dir_display}{Fore.GREEN} $ "
            
            command = input(prompt)
            print(Style.RESET_ALL, end="")  # Reset style after input
            
            # Process command
            execute_command(command)
            
            # Auto-save every 10 commands
            if game_state.stats["commands_executed"] % 10 == 0:
                save_game()
            
        except KeyboardInterrupt:
            print("\n" + Fore.YELLOW + "Use 'exit' to quit properly.")
        except Exception as e:
            print(Fore.RED + f"Error: {e}")

if __name__ == "__main__":
    main()
