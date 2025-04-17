#!/usr/bin/env python3
"""
Asathot - A realistic terminal-based hacking simulation game set in the Mr. Robot universe.
Players earn cryptocurrency through hacking missions, battle against E Corp and the Dark Army,
and upgrade their systems to become elite hackers within the fsociety movement.
Windows-compatible version
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
except ImportError:
    print("Required packages not found. Installing dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama", "pyfiglet"])
    import colorama
    from colorama import Fore, Back, Style
    import pyfiglet

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
                {"name": "HDD+", "size": 50, "cost": 0.002, "level": 2},
                {"name": "HDD RAID", "size": 100, "cost": 0.006, "level": 3},
                {"name": "SSD", "size": 250, "cost": 0.012, "level": 4},
                {"name": "SSD+", "size": 500, "cost": 0.025, "level": 5},
                {"name": "SSD RAID", "size": 1000, "cost": 0.05, "level": 6},
                {"name": "NVMe", "size": 2000, "cost": 0.1, "level": 7},
                {"name": "NVMe RAID", "size": 4000, "cost": 0.2, "level": 8}
            ],
            "network": [
                {"name": "56K Modem", "speed": 0.056, "cost": 0.0, "level": 1},
                {"name": "ADSL", "speed": 1.0, "cost": 0.005, "level": 2},
                {"name": "Cable", "speed": 10.0, "cost": 0.01, "level": 3},
                {"name": "Fiber Basic", "speed": 100.0, "cost": 0.02, "level": 4},
                {"name": "Fiber Pro", "speed": 500.0, "cost": 0.04, "level": 5},
                {"name": "Dedicated Fiber", "speed": 1000.0, "cost": 0.08, "level": 6},
                {"name": "Data Center", "speed": 10000.0, "cost": 0.15, "level": 7},
                {"name": "Quantum Link", "speed": 100000.0, "cost": 0.3, "level": 8}
            ],
            "security": [
                {"name": "Basic Firewall", "cost": 0.0, "level": 1},
                {"name": "Advanced Firewall", "cost": 0.004, "level": 2},
                {"name": "Intrusion Detection", "cost": 0.008, "level": 3},
                {"name": "VPN", "cost": 0.015, "level": 4},
                {"name": "Onion Routing", "cost": 0.03, "level": 5},
                {"name": "Military Grade Encryption", "cost": 0.06, "level": 6},
                {"name": "Quantum Encryption", "cost": 0.12, "level": 7},
                {"name": "Dark Army Security", "cost": 0.25, "level": 8}
            ]
        }
        
        # Game statistics
        self.stats = {
            "game_started": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hacks_attempted": 0,
            "hacks_successful": 0,
            "targets_discovered": 0,
            "missions_completed": 0,
            "bitcoins_earned": 0.0,
            "upgrades_purchased": 0,
            "commands_executed": 0
        }
        
        # Command history
        self.history = []
        
        # Darkweb connection status
        self.connected_to_darkweb = False
        self.current_site = None
        
        # In-game time acceleration factor (1 = real time, >1 = faster)
        self.time_acceleration = 5
        
        # Game directory and file path tracking
        self.previous_dir = "~"

# Initialize the global game state
game_state = GameState()

# Helper functions
def format_btc(amount: float) -> str:
    """Format a Bitcoin amount with proper prefix (BTC, mBTC, μBTC, satoshi)"""
    if amount >= 1.0:
        return f"{amount:.4f} BTC"
    elif amount >= 0.001:
        return f"{amount * 1000:.4f} mBTC"
    elif amount >= 0.000001:
        return f"{amount * 1000000:.4f} μBTC"
    else:
        return f"{int(amount * 100000000)} satoshi"

def get_btc_usd_value(btc_amount: float) -> float:
    """Get the USD value of a Bitcoin amount"""
    return btc_amount * DEFAULT_BTC_VALUE

def print_header():
    """Print the game header/banner"""
    terminal_width = shutil.get_terminal_size().columns
    banner_text = pyfiglet.figlet_format("ASATHOT", font="slant")
    print(Fore.CYAN + banner_text)
    print(Fore.BLUE + "=" * min(80, terminal_width))
    print(f"Version: {VERSION}   BTC: {format_btc(game_state.player['bitcoin'])}   Rep: {game_state.player['reputation']}   ")
    print(Fore.BLUE + "=" * min(80, terminal_width))

def save_game():
    """Save the game state to a file"""
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump({
                "player": game_state.player,
                "pc": game_state.pc,
                "file_system": game_state.file_system,
                "stats": game_state.stats,
                "missions": game_state.missions,
                "championships": game_state.championships,
                "network_targets": game_state.network_targets,
                "current_dir": game_state.current_dir
            }, f)
        return True
    except Exception as e:
        print(Fore.RED + f"Error saving game: {e}")
        return False

def load_game() -> bool:
    """Load the game state from a file"""
    if not os.path.exists(SAVE_FILE):
        return False
        
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
            game_state.player = data.get("player", game_state.player)
            game_state.pc = data.get("pc", game_state.pc)
            game_state.file_system = data.get("file_system", game_state.file_system)
            game_state.stats = data.get("stats", game_state.stats)
            game_state.missions = data.get("missions", game_state.missions)
            game_state.championships = data.get("championships", game_state.championships)
            game_state.network_targets = data.get("network_targets", game_state.network_targets)
            game_state.current_dir = data.get("current_dir", "~")
        return True
    except Exception as e:
        print(Fore.RED + f"Error loading game: {e}")
        return False

def add_to_history(message: str, color: str = Fore.WHITE):
    """Add a message to the command history"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    game_state.history.append({
        "timestamp": timestamp,
        "message": message,
        "color": color
    })

def display_history(count: int = 10):
    """Display the recent command history"""
    if not game_state.history:
        print("No command history available.")
        return
        
    print("\nRecent command history:")
    for entry in game_state.history[-count:]:
        timestamp = entry["timestamp"]
        message = entry["message"]
        color = entry["color"]
        print(f"{Fore.YELLOW}[{timestamp}]{color} {message}")

def get_pc_power_level() -> float:
    """Calculate the current PC's power level"""
    cpu_power = game_state.pc["cpu"]["cores"] * game_state.pc["cpu"]["speed"]
    ram_power = math.log2(game_state.pc["ram"]["size"]) / 2
    storage_power = math.log2(game_state.pc["storage"]["size"]) / 3
    network_power = math.log10(game_state.pc["network"]["speed"] + 1) * 2
    security_level = game_state.pc["security"]["level"]
    
    return (cpu_power + ram_power + storage_power + network_power) * (1 + security_level / 10)

def get_difficulty_level(target: Dict) -> float:
    """Calculate the difficulty level of a target"""
    security_level = target["security_level"]
    service_count = len(target["services"])
    vuln_count = len(target.get("vulnerabilities", []))
    
    # Higher security with fewer vulnerabilities = higher difficulty
    difficulty = security_level * (1 + service_count / 10) / math.sqrt(vuln_count + 1)
    
    # Special case for E Corp and Dark Army targets
    if "E Corp" in target.get("name", ""):
        difficulty *= 1.5
    if "Dark Army" in target.get("name", ""):
        difficulty *= 2.0
        
    return difficulty

def calculate_hack_success_chance(difficulty: float) -> float:
    """Calculate the chance of successful hacking based on PC power and target difficulty"""
    pc_power = get_pc_power_level()
    skill_multiplier = 1 + sum(game_state.player["skills"].values()) / 20
    
    success_chance = min(0.95, (pc_power * skill_multiplier) / (difficulty * 2))
    
    # Minimum chance is 5%, maximum is 95%
    return max(0.05, success_chance)

def generate_random_ip() -> str:
    """Generate a random IP address"""
    octets = [str(random.randint(1, 254)) for _ in range(4)]
    return ".".join(octets)

def get_target_by_ip(ip: str) -> Optional[Dict]:
    """Get a network target by IP address"""
    for target in game_state.network_targets:
        if target["ip"] == ip:
            return target
    return None

def discover_ip(ip: str) -> bool:
    """Mark an IP as discovered and return True if it's new"""
    target = get_target_by_ip(ip)
    if target and not target["discovered"]:
        target["discovered"] = True
        if ip not in game_state.player["discovered_ips"]:
            game_state.player["discovered_ips"].append(ip)
            game_state.stats["targets_discovered"] += 1
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
        return False
        
    # Check if we're trying to upgrade to a higher level
    current_level = game_state.pc[component]["level"]
    if level <= current_level:
        return False
        
    # Get the upgrade details
    for upgrade in game_state.upgrades[component]:
        if upgrade["level"] == level:
            # Check if player can afford it
            if game_state.player["bitcoin"] < upgrade["cost"]:
                return False
                
            # Apply the upgrade
            game_state.player["bitcoin"] -= upgrade["cost"]
            game_state.pc[component].update(upgrade)
            game_state.stats["upgrades_purchased"] += 1
            
            return True
            
    return False

def format_time(seconds: int) -> str:
    """Format seconds into a human-readable time string"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remainder = seconds % 60
        return f"{minutes}m {remainder}s"
    else:
        hours = seconds // 3600
        remainder = seconds % 3600
        minutes = remainder // 60
        seconds = remainder % 60
        return f"{hours}h {minutes}m {seconds}s"

def display_skills():
    """Display player skills"""
    skills = game_state.player["skills"]
    print("\nHacking Skills:")
    print(f"  Network Hacking:   {Fore.CYAN}{'█' * skills['network']}{Fore.BLACK}{'█' * (10 - skills['network'])} {skills['network']}/10")
    print(f"  Cryptography:      {Fore.CYAN}{'█' * skills['crypto']}{Fore.BLACK}{'█' * (10 - skills['crypto'])} {skills['crypto']}/10")
    print(f"  Malware Dev:       {Fore.CYAN}{'█' * skills['malware']}{Fore.BLACK}{'█' * (10 - skills['malware'])} {skills['malware']}/10")
    print(f"  Social Eng:        {Fore.CYAN}{'█' * skills['social']}{Fore.BLACK}{'█' * (10 - skills['social'])} {skills['social']}/10")

def display_pc_stats():
    """Display PC stats"""
    print("\nPC Specifications:")
    print(f"  CPU: {Fore.CYAN}{game_state.pc['cpu']['name']} {game_state.pc['cpu']['speed']} GHz ({game_state.pc['cpu']['cores']} cores)")
    print(f"  RAM: {Fore.CYAN}{game_state.pc['ram']['name']} {game_state.pc['ram']['size']} MB")
    print(f"  Storage: {Fore.CYAN}{game_state.pc['storage']['name']} {game_state.pc['storage']['size']} GB")
    print(f"  Network: {Fore.CYAN}{game_state.pc['network']['name']} {game_state.pc['network']['speed']} Mbps")
    print(f"  Security: {Fore.CYAN}{game_state.pc['security']['name']} (Level {game_state.pc['security']['level']})")
    print(f"\nOverall Power Level: {Fore.GREEN}{get_pc_power_level():.2f}")

def display_player_stats():
    """Display player statistics"""
    print("\nGame Statistics:")
    print(f"  Game started: {Fore.CYAN}{game_state.stats['game_started']}")
    print(f"  Hack attempts: {Fore.CYAN}{game_state.stats['hacks_attempted']}")
    print(f"  Successful hacks: {Fore.CYAN}{game_state.stats['hacks_successful']}")
    print(f"  Targets discovered: {Fore.CYAN}{game_state.stats['targets_discovered']}")
    print(f"  Missions completed: {Fore.CYAN}{game_state.stats['missions_completed']}")
    print(f"  Bitcoin earned: {Fore.CYAN}{format_btc(game_state.stats['bitcoins_earned'])}")
    print(f"  Upgrades purchased: {Fore.CYAN}{game_state.stats['upgrades_purchased']}")
    print(f"  Commands executed: {Fore.CYAN}{game_state.stats['commands_executed']}")
    
    # Display affiliations
    print("\nAffiliations:")
    if game_state.player["fsociety_member"]:
        print(f"  {Fore.RED}FSociety Member{Style.RESET_ALL}")
    else:
        rep_needed = FSOCIETY_REP_THRESHOLD - game_state.player["reputation"]
        if rep_needed > 0:
            print(f"  FSociety Membership: {Fore.YELLOW}Need {rep_needed} more reputation")
        else:
            print(f"  FSociety Membership: {Fore.GREEN}Available! Type 'connect fsociety.onion'")
    
    if game_state.player["dark_army_contact"]:
        print(f"  {Fore.MAGENTA}Dark Army Contact{Style.RESET_ALL}")
    else:
        rep_needed = DARK_ARMY_REP_THRESHOLD - game_state.player["reputation"]
        if rep_needed > 0:
            print(f"  Dark Army Contact: {Fore.YELLOW}Need {rep_needed} more reputation")

def skill_level_up_check(skill: str, increment: float = 0.1) -> bool:
    """Check if a skill should level up and apply the increment"""
    if skill not in game_state.player["skills"]:
        return False
        
    current_level = game_state.player["skills"][skill]
    if current_level >= 10:  # Max level is 10
        return False
        
    # Randomly apply increment based on current level (harder to level up at higher levels)
    chance = random.random() * (11 - current_level) / 10
    if chance > 0.5:
        # We apply a partial increment, simulating skill experience
        game_state.player["skills"][skill] = min(10, current_level + increment)
        
        # Check if we've reached a new integer level
        new_level = int(game_state.player["skills"][skill])
        if new_level > int(current_level):
            return True
            
    return False

def get_time_for_hack(target_difficulty: float) -> float:
    """Calculate the time needed for a hack based on PC specs and difficulty"""
    pc_power = get_pc_power_level()
    network_speed = game_state.pc["network"]["speed"]
    
    # Base time in seconds
    base_time = target_difficulty * 5
    
    # Adjust for PC power and network speed
    time_factor = base_time / (pc_power * math.log10(network_speed + 1))
    
    # Apply time acceleration
    return max(2, time_factor / game_state.time_acceleration)

def perform_hack(target_ip: str, hack_type: str) -> bool:
    """Perform a hacking attempt on a target"""
    target = get_target_by_ip(target_ip)
    if not target:
        print(Fore.RED + f"Error: IP {target_ip} not found in database.")
        return False
        
    # Make sure the target has been discovered
    if not target["discovered"]:
        discover_ip(target_ip)
    
    # Calculate difficulty and success chance
    difficulty = get_difficulty_level(target)
    success_chance = calculate_hack_success_chance(difficulty)
    
    # Determine which skill to use for this hack type
    skill_map = {
        "scan": "network",
        "bruteforce": "crypto",
        "exploit": "malware",
        "social": "social"
    }
    
    skill_used = skill_map.get(hack_type.lower(), "network")
    
    # Get the time required for this hack
    hack_time = get_time_for_hack(difficulty)
    
    # Update stats
    game_state.stats["hacks_attempted"] += 1
    
    # Simulate the hack
    print(f"\n{Fore.YELLOW}Attempting {hack_type} on {target['name']} ({target_ip})...")
    print(f"Estimated time: {format_time(int(hack_time))}")
    print(f"Success probability: {success_chance*100:.1f}%")
    
    # Progress bar
    steps = min(20, int(hack_time))
    for i in range(steps):
        time.sleep(hack_time / steps)
        progress = int((i + 1) / steps * 20)
        print(f"\r[{'█' * progress}{' ' * (20 - progress)}] {(i+1)/steps*100:.1f}%", end="")
    print()
    
    # Determine success
    success = random.random() < success_chance
    
    if success:
        print(Fore.GREEN + f"\nSuccess! {hack_type.title()} operation completed on {target['name']}.")
        add_to_history(f"Successful {hack_type} on {target_ip}", Fore.GREEN)
        game_state.stats["hacks_successful"] += 1
        
        # Check for skill improvement
        if skill_level_up_check(skill_used):
            new_level = int(game_state.player["skills"][skill_used])
            print(Fore.CYAN + f"\nSkill level up! Your {skill_used} skills improved to level {new_level}!")
            
        # Update mission progress if applicable
        update_mission_progress(target_ip, hack_type)
        
        return True
    else:
        print(Fore.RED + f"\nFailed! {hack_type.title()} operation unsuccessful on {target['name']}.")
        add_to_history(f"Failed {hack_type} on {target_ip}", Fore.RED)
        
        # Still a small chance of skill improvement on failure
        if random.random() < 0.2:
            skill_level_up_check(skill_used, 0.05)
            
        return False

def update_mission_progress(target_ip: str, hack_type: str) -> None:
    """Update the progress of the current mission if applicable"""
    if not game_state.player["current_mission"]:
        return
        
    mission_id = game_state.player["current_mission"]
    mission = get_mission_by_id(mission_id)
    
    if not mission:
        return
        
    # Check if this hack is for the mission target
    if mission["target"] != target_ip:
        return
        
    # Check if this hack type matches the current mission step
    current_step = mission["current_step"]
    if current_step >= len(mission["steps"]):
        return  # Mission already completed all steps
        
    current_step_type = mission["steps"][current_step].lower()
    
    # Check if the hack type matches (partial match is fine)
    if hack_type.lower() in current_step_type or current_step_type in hack_type.lower():
        mission["current_step"] += 1
        print(Fore.CYAN + f"\nMission '{mission['title']}' progress updated!")
        
        # Check if mission is now complete
        if mission["current_step"] >= len(mission["steps"]):
            complete_mission(mission_id)

def complete_mission(mission_id: str) -> None:
    """Complete a mission and award rewards"""
    mission = get_mission_by_id(mission_id)
    if not mission:
        return
        
    # Award Bitcoin
    reward = mission["reward"]
    game_state.player["bitcoin"] += reward
    game_state.stats["bitcoins_earned"] += reward
    
    # Award reputation
    rep_reward = mission["rep_reward"]
    game_state.player["reputation"] += rep_reward
    
    # Mark as completed
    mission["completed"] = True
    if mission_id not in game_state.player["completed_missions"]:
        game_state.player["completed_missions"].append(mission_id)
        
    # Reset current mission
    game_state.player["current_mission"] = None
    
    # Update stats
    game_state.stats["missions_completed"] += 1
    
    # Display completion message
    print(Fore.GREEN + f"\nMission '{mission['title']}' completed!")
    print(f"Rewards: {format_btc(reward)} and {rep_reward} reputation points.")
    add_to_history(f"Completed mission '{mission['title']}'", Fore.GREEN)
    
    # Check for special conditions after mission completion
    if game_state.player["reputation"] >= FSOCIETY_REP_THRESHOLD and not game_state.player["fsociety_member"]:
        print(Fore.CYAN + "\nYou now have enough reputation to join fsociety!")
        print("Connect to fsociety.onion to learn more.")
        
    if game_state.player["reputation"] >= DARK_ARMY_REP_THRESHOLD and not game_state.player["dark_army_contact"]:
        print(Fore.MAGENTA + "\nYou've gained the attention of the Dark Army...")
        print("Expect contact soon.")

def complete_championship(championship_id: str) -> None:
    """Complete a championship and award rewards"""
    championship = get_championship_by_id(championship_id)
    if not championship:
        return
        
    # Award Bitcoin
    reward = championship["reward"]
    game_state.player["bitcoin"] += reward
    game_state.stats["bitcoins_earned"] += reward
    
    # Award reputation
    rep_reward = championship["rep_reward"]
    game_state.player["reputation"] += rep_reward
    
    # Mark as completed
    championship["completed"] = True
    
    # Display completion message
    print(Fore.GREEN + f"\nChampionship '{championship['title']}' completed!")
    print(f"Rewards: {format_btc(reward)} and {rep_reward} reputation points.")
    add_to_history(f"Completed championship '{championship['title']}'", Fore.GREEN)
    
    # Special reward for Five/Nine Prep
    if championship_id == "c002":
        print(Fore.RED + "\nYou are now recognized as a key member of fsociety!")
        print("You've gained privileged access to fsociety systems.")
        
    # Special reward for Dark Army Infiltration
    if championship_id == "c003":
        print(Fore.MAGENTA + "\nThe Dark Army acknowledges your skills.")
        print("You now have full access to Dark Army resources.")
        game_state.player["dark_army_contact"] = True

def generate_new_mission() -> Dict:
    """Generate a new mission for the player"""
    # Create mission ID
    mission_count = len(game_state.missions)
    mission_id = f"m{mission_count+1:03d}"
    
    # Randomly select a target
    available_targets = [t for t in game_state.network_targets 
                        if t["security_level"] <= int(get_pc_power_level() / 2) + 3]
    
    if not available_targets:
        available_targets = [random.choice(game_state.network_targets)]
        
    target = random.choice(available_targets)
    
    # Generate mission properties
    difficulty = target["security_level"]
    reward = 0.001 * difficulty * (1 + random.random())
    rep_reward = 5 * difficulty
    
    # Generate mission steps
    step_count = random.randint(2, 4)
    possible_steps = ["scan network", "identify vulnerability", "exploit vulnerability", 
                    "bypass firewall", "gain access", "escalate privileges", 
                    "download data", "plant backdoor", "erase tracks"]
    
    steps = ["scan"]  # Always start with scan
    for _ in range(step_count - 1):
        step = random.choice(possible_steps)
        if step not in steps:
            steps.append(step)
    
    # Generate mission title and description
    titles = [
        "Data Breach", "Corporate Espionage", "Financial Hack",
        "System Infiltration", "Security Bypass", "Ghost Protocol"
    ]
    
    title = random.choice(titles)
    description = f"Infiltrate {target['name']} and {steps[-1].lower()} to complete the mission."
    
    # Create the mission
    mission = {
        "id": mission_id,
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "target": target["ip"],
        "reward": reward,
        "rep_reward": rep_reward,
        "completed": False,
        "steps": steps,
        "current_step": 0
    }
    
    # Add mission to the list
    game_state.missions.append(mission)
    
    return mission

def generate_new_championship() -> Dict:
    """Generate a new championship challenge"""
    # Create championship ID
    championship_count = len(game_state.championships)
    championship_id = f"c{championship_count+1:03d}"
    
    # Select a high-difficulty target
    available_targets = [t for t in game_state.network_targets if t["security_level"] >= 5]
    if not available_targets:
        available_targets = [t for t in game_state.network_targets if t["security_level"] >= 3]
    
    target = random.choice(available_targets)
    
    # Generate championship properties
    difficulty = target["security_level"] + random.randint(1, 3)
    reward = 0.01 * difficulty * (1 + random.random())
    rep_reward = 10 * difficulty
    required_rep = max(20, difficulty * 10)
    
    # Generate championship tasks
    task_count = random.randint(4, 6)
    possible_tasks = ["network scan", "vulnerability analysis", "firewall bypass", 
                     "system infiltration", "privilege escalation", "data extraction",
                     "backdoor installation", "log manipulation", "cover tracks",
                     "communication interception", "encryption breaking"]
    
    tasks = []
    for _ in range(task_count):
        task = random.choice(possible_tasks)
        if task not in tasks:
            tasks.append(task)
    
    # Generate championship title and description
    titles = [
        "Hacker Elite", "Digital Phantom", "Shadow Infiltrator",
        "Code Breaker", "Network Ghost", "System Overlord"
    ]
    
    title = random.choice(titles)
    description = f"A challenging series of hacks against {target['name']} to prove your elite status."
    
    # Create the championship
    championship = {
        "id": championship_id,
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "target": target["ip"],
        "reward": reward,
        "rep_reward": rep_reward,
        "required_rep": required_rep,
        "completed": False,
        "tasks": tasks,
        "current_task": 0
    }
    
    # Add championship to the list
    game_state.championships.append(championship)
    
    return championship

# Windows-friendly menu implementation (replacing simple_term_menu)
def show_menu(title: str, options: List[str]) -> Optional[int]:
    """Display a menu and get the user's selection"""
    print(f"\n{Fore.CYAN}{title}{Style.RESET_ALL}")
    for i, option in enumerate(options, 1):
        print(f"{Fore.YELLOW}{i}. {Fore.WHITE}{option}")
    print(f"{Fore.YELLOW}q. {Fore.WHITE}Back/Exit")
    
    while True:
        choice = input(f"\n{Fore.CYAN}Enter your choice: {Fore.WHITE}")
        if choice.lower() == 'q':
            return None
        try:
            index = int(choice) - 1
            if 0 <= index < len(options):
                return index
            else:
                print(f"{Fore.RED}Invalid choice. Try again.")
        except ValueError:
            print(f"{Fore.RED}Please enter a number or 'q' to exit.")

def execute_command(command_str: str) -> None:
    """Parse and execute a terminal command"""
    # Handle empty commands
    if not command_str.strip():
        return
        
    # Update command counter
    game_state.stats["commands_executed"] += 1
    
    # Parse the command and arguments
    parts = command_str.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    # Command dictionary
    commands = {
        "help": show_help,
        "ls": cmd_ls,
        "dir": cmd_ls,  # Windows equivalent
        "cd": cmd_cd,
        "pwd": cmd_pwd,
        "cat": cmd_cat,
        "type": cmd_cat,  # Windows equivalent
        "mkdir": cmd_mkdir,
        "md": cmd_mkdir,  # Windows equivalent
        "touch": cmd_touch,
        "echo": cmd_echo,
        "rm": cmd_rm,
        "del": cmd_rm,  # Windows equivalent
        "rmdir": cmd_rmdir,
        "rd": cmd_rmdir,  # Windows equivalent
        "scan": cmd_scan,
        "hack": cmd_hack,
        "bruteforce": cmd_bruteforce,
        "mission": cmd_mission,
        "shop": cmd_shop,
        "upgrade": cmd_upgrade,
        "bitcoin": cmd_bitcoin,
        "btc": cmd_bitcoin,
        "stats": display_player_stats,
        "pc": display_pc_stats,
        "skills": display_skills,
        "history": display_history,
        "connect": cmd_connect,
        "disconnect": cmd_disconnect,
        "run": cmd_run,
        "clear": lambda _: os.system('cls' if os.name == 'nt' else 'clear'),
        "cls": lambda _: os.system('cls' if os.name == 'nt' else 'clear'),
        "save": lambda _: print(Fore.GREEN + "Game saved successfully!" if save_game() else Fore.RED + "Failed to save game."),
        "exit": lambda _: print(Fore.YELLOW + "Exiting Asathot... Game saved.") or save_game() or sys.exit(0)
    }
    
    # Execute the command if it exists
    if command in commands:
        try:
            if command in ["help", "scan", "hack", "bruteforce", "mission", "shop", 
                       "upgrade", "connect", "run", "ls", "dir", "cd", "cat", "type", 
                       "mkdir", "md", "touch", "echo", "rm", "del", "rmdir", "rd"]:
                commands[command](args)
            else:
                commands[command]()
        except Exception as e:
            print(Fore.RED + f"Error executing command: {e}")
    else:
        print(Fore.RED + f"Unknown command: {command}")
        print("Type 'help' to see available commands.")

def show_help(args: str) -> None:
    """Display help information"""
    if args:
        # Show help for specific command
        cmd = args.lower()
        if cmd == "ls" or cmd == "dir":
            print("\nls / dir - List directory contents")
            print("Usage: ls [path]")
            print("Example: ls tools")
        elif cmd == "cd":
            print("\ncd - Change directory")
            print("Usage: cd <path>")
            print("Example: cd documents")
            print("Use 'cd ..' to go up one directory")
        elif cmd == "pwd":
            print("\npwd - Print working directory")
            print("Usage: pwd")
        elif cmd == "cat" or cmd == "type":
            print("\ncat / type - Display file contents")
            print("Usage: cat <filename>")
            print("Example: cat readme.txt")
        elif cmd == "mkdir" or cmd == "md":
            print("\nmkdir / md - Create a directory")
            print("Usage: mkdir <dirname>")
            print("Example: mkdir new_folder")
        elif cmd == "touch":
            print("\ntouch - Create a file")
            print("Usage: touch <filename>")
            print("Example: touch notes.txt")
        elif cmd == "rm" or cmd == "del":
            print("\nrm / del - Remove a file")
            print("Usage: rm <filename>")
            print("Example: rm notes.txt")
        elif cmd == "rmdir" or cmd == "rd":
            print("\nrmdir / rd - Remove a directory")
            print("Usage: rmdir <dirname>")
            print("Example: rmdir old_folder")
        elif cmd == "echo":
            print("\necho - Echo text to the terminal")
            print("Usage: echo <text>")
            print("Example: echo Hello, world!")
        elif cmd == "connect":
            print("\nconnect - Connect to a darkweb site")
            print("Usage: connect <site>")
            print("Example: connect bitcoinhub.onion")
            print("\nAvailable sites:")
            print("  bitcoinhub.onion - Bitcoin exchange and market")
            print("  globalch.onion - Global hacker chat forum")
            print("  champions.onion - Hacker championship challenges")
            print("  fsociety.onion - FSociety darknet site (requires reputation)")
        elif cmd == "disconnect":
            print("\ndisconnect - Disconnect from the current darkweb site")
            print("Usage: disconnect")
        elif cmd == "scan":
            print("\nscan - Scan an IP address for vulnerabilities")
            print("Usage: scan <ip>")
            print("Example: scan 192.168.1.1")
        elif cmd == "hack":
            print("\nhack - Attempt to hack a target system")
            print("Usage: hack <ip>")
            print("Example: hack 192.168.1.1")
        elif cmd == "bruteforce":
            print("\nbruteforce - Perform a bruteforce attack on a target")
            print("Usage: bruteforce <ip>")
            print("Example: bruteforce 192.168.1.1")
        elif cmd == "mission":
            print("\nmission - Manage missions")
            print("Usage: mission [list|info|accept|current]")
            print("Example: mission list")
            print("Example: mission accept m001")
            print("Example: mission current")
        elif cmd == "shop":
            print("\nshop - Access the upgrade shop")
            print("Usage: shop [category]")
            print("Example: shop cpu")
            print("Available categories: cpu, ram, storage, network, security")
        elif cmd == "upgrade":
            print("\nupgrade - Purchase a PC upgrade")
            print("Usage: upgrade <component> <level>")
            print("Example: upgrade cpu 2")
        elif cmd == "bitcoin" or cmd == "btc":
            print("\nbitcoin / btc - Check Bitcoin balance")
            print("Usage: bitcoin")
        elif cmd == "run":
            print("\nrun - Run a tool or script")
            print("Usage: run <tool> [args]")
            print("Example: run network_scanner.py 192.168.1.1")
        elif cmd == "stats":
            print("\nstats - Display player statistics")
            print("Usage: stats")
        elif cmd == "pc":
            print("\npc - Display PC specifications")
            print("Usage: pc")
        elif cmd == "skills":
            print("\nskills - Display hacking skills")
            print("Usage: skills")
        elif cmd == "history":
            print("\nhistory - Display command history")
            print("Usage: history [count]")
            print("Example: history 20")
        elif cmd == "clear" or cmd == "cls":
            print("\nclear / cls - Clear the terminal screen")
            print("Usage: clear")
        elif cmd == "save":
            print("\nsave - Save the game")
            print("Usage: save")
        elif cmd == "exit":
            print("\nexit - Exit the game (automatically saves)")
            print("Usage: exit")
        else:
            print(f"No help available for command: {args}")
    else:
        # Show general help
        print("\nAvailable commands:")
        print("\nFile System Navigation:")
        print("  ls / dir - List directory contents")
        print("  cd - Change directory")
        print("  pwd - Print working directory")
        print("  cat / type - Display file contents")
        print("  mkdir / md - Create a directory")
        print("  touch - Create a file")
        print("  rm / del - Remove a file")
        print("  rmdir / rd - Remove a directory")
        print("  echo - Echo text to the terminal")
        
        print("\nHacking Operations:")
        print("  scan - Scan an IP address for vulnerabilities")
        print("  hack - Attempt to hack a target system")
        print("  bruteforce - Perform a bruteforce attack on a target")
        print("  run - Run a tool or script")
        
        print("\nMission & Progress:")
        print("  mission - Manage missions")
        print("  shop - Access the upgrade shop")
        print("  upgrade - Purchase a PC upgrade")
        print("  bitcoin / btc - Check Bitcoin balance")
        
        print("\nDarkweb Navigation:")
        print("  connect - Connect to a darkweb site")
        print("  disconnect - Disconnect from the current darkweb site")
        
        print("\nInformation & Utilities:")
        print("  stats - Display player statistics")
        print("  pc - Display PC specifications")
        print("  skills - Display hacking skills")
        print("  history - Display command history")
        print("  clear / cls - Clear the terminal screen")
        print("  save - Save the game")
        print("  exit - Exit the game (automatically saves)")
        print("  help - Show this help message")
        print("  help <command> - Show help for a specific command")

def cmd_ls(args: str) -> None:
    """List directory contents"""
    # Determine the target directory
    target_path = args.strip() if args.strip() else game_state.current_dir
    resolved_path = resolve_path(target_path)
    
    if not resolved_path:
        print(Fore.RED + f"Error: directory not found: {target_path}")
        return
    
    # Navigate to the directory
    current = game_state.file_system
    for component in resolved_path.split('/'):
        if not component or component == '.':
            continue
        if component not in current:
            print(Fore.RED + f"Error: {component} not found")
            return
        current = current[component]["content"]
    
    # List the contents
    if not current:
        print("(empty directory)")
        return
        
    # Sort by type (directories first, then files)
    dirs = []
    files = []
    
    for name, item in current.items():
        if item["type"] == "dir":
            dirs.append(name)
        else:
            files.append(name)
            
    # Display directories
    for name in sorted(dirs):
        print(Fore.BLUE + f"{name}/")
        
    # Display files
    for name in sorted(files):
        print(name)

def cmd_cd(args: str) -> None:
    """Change directory"""
    path = args.strip()
    
    if not path:
        # No path provided, stay in current directory
        return
        
    # Save the previous directory
    game_state.previous_dir = game_state.current_dir
    
    # Handle special cases
    if path == "..":
        # Go up one directory
        if game_state.current_dir == "~":
            return  # Already at the root
            
        # Split the path and remove the last component
        components = game_state.current_dir.split('/')
        if components[-1] == '':
            components.pop()  # Handle trailing slash
            
        components.pop()  # Remove last component
        
        if not components or (len(components) == 1 and components[0] == ''):
            game_state.current_dir = "~"
        else:
            game_state.current_dir = '/'.join(components)
        return
    elif path == "-":
        # Go to the previous directory
        game_state.current_dir, game_state.previous_dir = game_state.previous_dir, game_state.current_dir
        return
    elif path == "~" or path == "/":
        # Go to home directory
        game_state.current_dir = "~"
        return
        
    # Resolve the path
    resolved_path = resolve_path(path)
    if not resolved_path:
        print(Fore.RED + f"Error: directory not found: {path}")
        return
        
    # Check if the resolved path is a directory
    current = game_state.file_system
    for component in resolved_path.split('/'):
        if not component or component == '.':
            continue
            
        if component not in current:
            print(Fore.RED + f"Error: {component} not found")
            return
            
        if current[component]["type"] != "dir":
            print(Fore.RED + f"Error: {component} is not a directory")
            return
            
        current = current[component]["content"]
        
    # Set the current directory
    game_state.current_dir = resolved_path

def cmd_pwd() -> None:
    """Print working directory"""
    print(game_state.current_dir)

def cmd_cat(args: str) -> None:
    """Display file contents"""
    filename = args.strip()
    if not filename:
        print(Fore.RED + "Error: no filename provided")
        return
        
    # Resolve the file path
    resolved_path = resolve_path(filename)
    if not resolved_path:
        print(Fore.RED + f"Error: file not found: {filename}")
        return
        
    # Navigate to the file
    current = game_state.file_system
    components = resolved_path.split('/')
    file_name = components[-1]
    dir_path = '/'.join(components[:-1])
    
    # Navigate to the directory containing the file
    for component in dir_path.split('/'):
        if not component or component == '.':
            continue
            
        if component not in current:
            print(Fore.RED + f"Error: {component} not found")
            return
            
        current = current[component]["content"]
    
    # Check if the file exists
    if file_name not in current:
        print(Fore.RED + f"Error: file not found: {file_name}")
        return
        
    # Check if it's a file
    if current[file_name]["type"] != "file":
        print(Fore.RED + f"Error: {file_name} is not a file")
        return
        
    # Display the file contents
    print(current[file_name]["content"])

def cmd_mkdir(args: str) -> None:
    """Create a directory"""
    dirname = args.strip()
    if not dirname:
        print(Fore.RED + "Error: no directory name provided")
        return
        
    # Get the current directory
    current_path = game_state.current_dir
    current = game_state.file_system
    
    # Navigate to the current directory
    for component in current_path.split('/'):
        if not component or component == '.' or component == '~':
            continue
            
        current = current[component]["content"]
    
    # Check if the directory already exists
    if dirname in current:
        print(Fore.RED + f"Error: {dirname} already exists")
        return
        
    # Create the directory
    current[dirname] = {
        "type": "dir",
        "content": {}
    }
    
    print(Fore.GREEN + f"Directory {dirname} created")

def cmd_touch(args: str) -> None:
    """Create a file"""
    filename = args.strip()
    if not filename:
        print(Fore.RED + "Error: no filename provided")
        return
        
    # Get the current directory
    current_path = game_state.current_dir
    current = game_state.file_system
    
    # Navigate to the current directory
    for component in current_path.split('/'):
        if not component or component == '.' or component == '~':
            continue
            
        current = current[component]["content"]
    
    # Check if the file already exists
    if filename in current:
        print(Fore.YELLOW + f"File {filename} already exists. Modified timestamp updated.")
        return
        
    # Create the file
    current[filename] = {
        "type": "file",
        "content": ""
    }
    
    print(Fore.GREEN + f"File {filename} created")

def cmd_rm(args: str) -> None:
    """Remove a file"""
    filename = args.strip()
    if not filename:
        print(Fore.RED + "Error: no filename provided")
        return
        
    # Get the current directory
    current_path = game_state.current_dir
    current = game_state.file_system
    
    # Navigate to the current directory
    for component in current_path.split('/'):
        if not component or component == '.' or component == '~':
            continue
            
        current = current[component]["content"]
    
    # Check if the file exists
    if filename not in current:
        print(Fore.RED + f"Error: file not found: {filename}")
        return
        
    # Check if it's a file
    if current[filename]["type"] != "file":
        print(Fore.RED + f"Error: {filename} is not a file")
        return
        
    # Remove the file
    del current[filename]
    print(Fore.GREEN + f"File {filename} deleted")

def cmd_rmdir(args: str) -> None:
    """Remove a directory"""
    dirname = args.strip()
    if not dirname:
        print(Fore.RED + "Error: no directory name provided")
        return
        
    # Get the current directory
    current_path = game_state.current_dir
    current = game_state.file_system
    
    # Navigate to the current directory
    for component in current_path.split('/'):
        if not component or component == '.' or component == '~':
            continue
            
        current = current[component]["content"]
    
    # Check if the directory exists
    if dirname not in current:
        print(Fore.RED + f"Error: directory not found: {dirname}")
        return
        
    # Check if it's a directory
    if current[dirname]["type"] != "dir":
        print(Fore.RED + f"Error: {dirname} is not a directory")
        return
        
    # Check if the directory is empty
    if current[dirname]["content"]:
        print(Fore.RED + f"Error: directory {dirname} is not empty")
        return
        
    # Remove the directory
    del current[dirname]
    print(Fore.GREEN + f"Directory {dirname} deleted")

def cmd_echo(args: str) -> None:
    """Echo text to the terminal"""
    if not args:
        print()
        return
        
    print(args)

def resolve_path(path: str) -> Optional[str]:
    """Resolve a file system path"""
    if not path:
        return game_state.current_dir
        
    # Handle absolute paths
    if path.startswith("/") or path.startswith("~"):
        resolved = path
    else:
        # Handle relative paths
        if game_state.current_dir == "~":
            resolved = f"~/{path}"
        else:
            resolved = f"{game_state.current_dir}/{path}"
    
    # Normalize the path
    components = []
    for component in resolved.split('/'):
        if not component or component == '.':
            continue
        elif component == '..':
            if components:
                components.pop()
        else:
            components.append(component)
    
    if not components:
        return "~"
    else:
        result = '/'.join(components)
        if result.startswith('~'):
            return result
        else:
            return f"~/{result}"

def cmd_connect(args: str) -> None:
    """Connect to a darkweb site"""
    site = args.strip().lower()
    if not site:
        print(Fore.RED + "Error: no site specified")
        print("Usage: connect <site>")
        print("Type 'help connect' for more information")
        return
    
    # Add .onion if not present
    if not site.endswith(".onion"):
        site += ".onion"
    
    # Available sites
    sites = {
        "bitcoinhub.onion": display_bitcoinhub,
        "globalch.onion": display_globalch,
        "champions.onion": display_champions,
        "fsociety.onion": display_fsociety,
        "ecorp.onion": display_ecorp_internal,
        "darkArmy.onion": display_dark_army
    }
    
    if site not in sites:
        print(Fore.RED + f"Error: site {site} not found or unreachable")
        return
    
    # Check for restricted sites
    if site == "fsociety.onion" and not game_state.player["fsociety_member"]:
        if game_state.player["reputation"] < FSOCIETY_REP_THRESHOLD:
            print(Fore.RED + "Access denied! You need more reputation to access this site.")
            print(f"Required reputation: {FSOCIETY_REP_THRESHOLD}")
            print(f"Your reputation: {game_state.player['reputation']}")
            return
        else:
            # Player has enough rep but isn't a member yet
            print(Fore.GREEN + "Welcome to FSociety. Your reputation precedes you.")
            print("You have been granted membership to our organization.")
            game_state.player["fsociety_member"] = True
            
            # Add fsociety files to the fsociety directory
            fsociety_dir = game_state.file_system["~"]["content"]["fsociety"]["content"]
            fsociety_dir.clear()  # Remove the locked file
            fsociety_dir.update({
                "five_nine_plan.txt": {
                    "type": "file",
                    "content": "Operation Five/Nine\n\nTarget: E Corp data centers\nObjective: Encrypt all financial data\nEffect: Reset consumer debt\n\nNote: This document is for internal fsociety members only. Destroy after reading."
                },
                "members.txt": {
                    "type": "file",
                    "content": "FSociety Members:\n\n- Elliot Alderson (Technical Lead)\n- Darlene Alderson (Operations)\n- Leslie Romero (Hardware)\n- Sunil Markesh (Infiltration)\n- Trenton (Security Research)\n- Mobley (Infrastructure)\n\n...and now you."
                },
                "locations.txt": {
                    "type": "file",
                    "content": "Meeting Locations:\n\nPrimary: Coney Island Arcade (Fun Society)\nBackup 1: End of the World Party Bar, 5th and Main\nBackup 2: Internet cafe, 23rd Street\n\nDO NOT share these locations with anyone."
                }
            })
    
    if site == "darkArmy.onion" and not game_state.player["dark_army_contact"]:
        if game_state.player["reputation"] < DARK_ARMY_REP_THRESHOLD:
            print(Fore.RED + "This site cannot be found. Connection terminated.")
            return
        else:
            # Player has enough rep but hasn't been contacted yet
            print(Fore.MAGENTA + "We've been watching you. Your skills are... interesting.")
            print("The Dark Army appreciates talent. We will be in touch.")
            game_state.player["dark_army_contact"] = True
    
    # Connect to the site
    print(Fore.YELLOW + f"Connecting to {site}...")
    time.sleep(1)
    print(Fore.GREEN + "Connected!")
    
    # Display the site
    game_state.connected_to_darkweb = True
    game_state.current_site = site
    sites[site]()

def cmd_disconnect() -> None:
    """Disconnect from the current darkweb site"""
    if not game_state.connected_to_darkweb:
        print(Fore.YELLOW + "You are not connected to any darkweb site.")
        return
        
    site = game_state.current_site
    print(Fore.YELLOW + f"Disconnecting from {site}...")
    time.sleep(0.5)
    print(Fore.GREEN + "Disconnected.")
    
    game_state.connected_to_darkweb = False
    game_state.current_site = None

def display_bitcoinhub() -> None:
    """Display the BitcoinHub site"""
    print(Fore.YELLOW + """
===================================================
          ₿ITCOIN HUB - Cryptocurrency Exchange
===================================================
    """)
    
    print(Fore.WHITE + f"""
Your Balance: {format_btc(game_state.player['bitcoin'])} (${get_btc_usd_value(game_state.player['bitcoin']):.2f})
Current BTC Value: ${DEFAULT_BTC_VALUE:.2f}

Options:
1. Exchange rates
2. Market trends
3. Trading (coming soon)
4. Mining pools (coming soon)
    """)
    
    choice = input(Fore.CYAN + "Enter option (or 'back' to return): " + Fore.WHITE)
    
    if choice == "1":
        print(Fore.WHITE + """
Exchange Rates:
1 BTC = $45,000 USD
1 BTC = €41,000 EUR
1 BTC = £35,000 GBP
1 BTC = ¥5,200,000 JPY

1 E-Coin = $1.00 USD (E Corp pegged rate)
        """)
    elif choice == "2":
        print(Fore.WHITE + """
Market Trends:
Bitcoin: ↑ +3.2% (Last 24h)
Ethereum: ↑ +1.7% (Last 24h)
E-Coin: → 0.0% (Stable, pegged to USD)

Analyst Notes:
"With recent cyber attacks on financial systems, cryptocurrency 
adoption continues to rise. E-Coin's stability is maintained
by E Corp's massive reserves, though some question for how long."
        """)
    elif choice == "3" or choice == "4":
        print(Fore.YELLOW + "This feature is not yet available.")
    elif choice.lower() == "back":
        return
    else:
        print(Fore.RED + "Invalid option.")
    
    # Remain on the page
    display_bitcoinhub()

def display_globalch() -> None:
    """Display the Global Hacker Chat site"""
    print(Fore.GREEN + """
===================================================
          GLOBAL HACKER CHAT - Latest Threads
===================================================
    """)
    
    threads = [
        ["AnonymouS", "E Corp vulnerabilities", "12h ago", 24],
        ["darkPulse", "New zero-day in Windows", "3h ago", 87],
        ["FSociety", "Operation planning", "6h ago", 31],
        ["CyberPhantom", "Steel Mountain bypass methods", "2d ago", 45],
        ["Whiterose", "Time sensitive matters", "1h ago", 17],
        ["NetHunter", "Network traffic analysis tools", "8h ago", 29]
    ]
    
    print(Fore.WHITE + "\nActive Threads:")
    for i, (user, title, time, replies) in enumerate(threads, 1):
        print(f"{i}. {Fore.CYAN}[{user}]{Fore.WHITE} {title} {Fore.YELLOW}({time}, {replies} replies)")
    
    choice = input(Fore.CYAN + "\nEnter thread number (or 'back' to return): " + Fore.WHITE)
    
    if choice.isdigit() and 1 <= int(choice) <= len(threads):
        thread_idx = int(choice) - 1
        user, title, _, _ = threads[thread_idx]
        
        print(Fore.YELLOW + f"\n=== Thread: {title} by {user} ===\n")
        
        # Generate some fake chat messages based on the thread
        if "E Corp" in title:
            messages = [
                ["AnonymouS", "Found a potential SQL injection in their customer portal."],
                ["ShadowByte", "Old news. They patched that last month."],
                ["RedTeamer", "The real vulnerability is in their API gateway."],
                ["FSociety", "We have more effective plans for E Corp..."],
                ["l33tHax", "Anyone tried attacking their SWIFT terminals?"],
                ["AnonymouS", "Their security team is expanding. Be careful."]
            ]
        elif "zero-day" in title:
            messages = [
                ["darkPulse", "This affects all Windows systems with SMB enabled."],
                ["WinHacker", "Proof of concept: github.com/darkpulse/smb-exploit"],
                ["SecureOS", "Microsoft is aware but hasn't released a patch yet."],
                ["Elliot", "Already weaponized. Use with extreme caution."],
                ["BugHunter", "I've reported it to MSRC, bounty rejected."],
                ["darkPulse", "Typical corporation ignoring real threats."]
            ]
        elif "FSociety" in title:
            messages = [
                ["FSociety", "Next phase begins tomorrow. Check secure channels."],
                ["MrRobot", "All members confirm readiness."],
                ["Darlene", "Hardware is prepared and distributed."],
                ["Trenton", "Network reconnaissance complete. Sending data via usual method."],
                ["Mobley", "Infrastructure is ready. Waiting for the signal."],
                ["FSociety", "Remember: We are fsociety, we are finally free, we are finally awake!"]
            ]
        elif "Steel Mountain" in title:
            messages = [
                ["CyberPhantom", "Their HVAC systems run on an isolated network, but there's a bridge."],
                ["NetRunner", "Old Raspberry Pi trick still works if you can get physical access."],
                ["IceBreaker", "Better to social engineer your way in as HVAC technician."],
                ["0xDEADBEEF", "Don't bother. They've implemented RFID entry badges with biometrics."],
                ["CyberPhantom", "RFID can be cloned if you get close enough to an employee."],
                ["Elliot", "The real vulnerability is in their climate monitoring software."]
            ]
        elif "Time sensitive" in title:
            messages = [
                ["Whiterose", "Everything happens exactly when it is supposed to happen."],
                ["DarkArmy", "Instructions received. Teams deployed."],
                ["Cipher", "Washington Township facility is ready."],
                ["Whiterose", "The project must remain on schedule. Delays are unacceptable."],
                ["Phantom", "Surveillance of target continues as directed."],
                ["Whiterose", "Remember, every person has a purpose, whether they know it or not."]
            ]
        else:
            messages = [
                ["NetHunter", "Wireshark still the best for most analysis needs."],
                ["PacketWiz", "Try Zeek (formerly Bro) for large-scale monitoring."],
                ["tcpdumpGod", "Don't sleep on tcpdump with custom filters."],
                ["NetMonster", "Anyone tried Arkime (formerly Moloch)?"],
                ["DataSnoop", "For encrypted traffic analysis, look at JA3 fingerprinting."],
                ["NetHunter", "Good point. Tool chain matters less than your methodology."]
            ]
        
        for user, message in messages:
            print(f"{Fore.CYAN}{user}: {Fore.WHITE}{message}")
        
        input(Fore.YELLOW + "\nPress Enter to return to thread list...")
        display_globalch()
    elif choice.lower() == "back":
        return
    else:
        print(Fore.RED + "Invalid option.")
        display_globalch()

def display_champions() -> None:
    """Display the Hacker Championships site"""
    print(Fore.RED + """
===================================================
          HACKER CHAMPIONSHIPS - Elite Challenges
===================================================
    """)
    
    # Filter championships by reputation requirement
    available_championships = [c for c in game_state.championships 
                             if c["required_rep"] <= game_state.player["reputation"]]
    
    if not available_championships:
        print(Fore.YELLOW + "\nNo championships available at your current reputation level.")
        print(f"Your reputation: {game_state.player['reputation']}")
        print("Check back after building more reputation.")
        
        input(Fore.CYAN + "\nPress Enter to return...")
        return
    
    print(Fore.WHITE + "\nAvailable Championships:")
    for i, championship in enumerate(available_championships, 1):
        status = f"{Fore.GREEN}[COMPLETED]" if championship["completed"] else ""
        print(f"{i}. {Fore.CYAN}{championship['title']}{Fore.WHITE} (Difficulty: {championship['difficulty']}) {status}")
        print(f"   {championship['description']}")
        print(f"   Reward: {format_btc(championship['reward'])} + {championship['rep_reward']} rep")
    
    choice = input(Fore.CYAN + "\nEnter championship number for details (or 'back'): " + Fore.WHITE)
    
    if choice.isdigit() and 1 <= int(choice) <= len(available_championships):
        champ_idx = int(choice) - 1
        championship = available_championships[champ_idx]
        
        print(Fore.YELLOW + f"\n=== Championship: {championship['title']} ===\n")
        print(Fore.WHITE + f"Description: {championship['description']}")
        print(f"Target: {championship['target']}")
        print(f"Difficulty: {championship['difficulty']}/10")
        print(f"Reward: {format_btc(championship['reward'])} + {championship['rep_reward']} reputation")
        
        print("\nRequired Tasks:")
        for i, task in enumerate(championship["tasks"], 1):
            if i <= championship["current_task"]:
                print(f"{i}. {Fore.GREEN}[DONE] {task}")
            else:
                print(f"{i}. {Fore.YELLOW}{task}")
        
        # Show special requirements
        if championship.get("fsociety_required") and not game_state.player["fsociety_member"]:
            print(Fore.RED + "\nRequires FSociety membership!")
            
        if championship.get("dark_army_required") and not game_state.player["dark_army_contact"]:
            print(Fore.RED + "\nRequires Dark Army contact!")
        
        print("\nTo attempt this championship, use the following commands:")
        print(f"1. scan {championship['target']}")
        print(f"2. hack {championship['target']}")
        print(f"(Advanced hacking commands may be required based on tasks)")
        
        input(Fore.CYAN + "\nPress Enter to return to championship list...")
        display_champions()
    elif choice.lower() == "back":
        return
    else:
        print(Fore.RED + "Invalid option.")
        display_champions()

def display_fsociety() -> None:
    """Display the fsociety site"""
    print(Fore.RED + """
███████╗███████╗ ██████╗  ██████╗██╗███████╗████████╗██╗   ██╗
██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
█████╗  ███████╗██║   ██║██║     ██║█████╗     ██║    ╚████╔╝ 
██╔══╝  ╚════██║██║   ██║██║     ██║██╔══╝     ██║     ╚██╔╝  
██║     ███████║╚██████╔╝╚██████╗██║███████╗   ██║      ██║   
╚═╝     ╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
===================================================================
            "Democracy has been hacked"
===================================================================
    """)
    
    print(Fore.GREEN + f"Welcome, {Fore.YELLOW}member{Fore.GREEN}. Our revolution continues.")
    
    menu_options = [
        "Active Missions",
        "Five/Nine Planning",
        "Member Communications",
        "E Corp Intelligence"
    ]
    
    print(Fore.WHITE + "\nFSociety Terminal:")
    for i, option in enumerate(menu_options, 1):
        print(f"{i}. {option}")
    
    choice = input(Fore.CYAN + "\nSelect option (or 'back'): " + Fore.WHITE)
    
    if choice == "1":
        # Display available fsociety missions
        fsociety_missions = [m for m in game_state.missions 
                           if m.get("fsociety_related") and not m["completed"]]
        
        if not fsociety_missions:
            print(Fore.YELLOW + "\nNo active fsociety missions available.")
            print("Check back later or complete the Five/Nine preparation.")
        else:
            print(Fore.WHITE + "\nFSociety Missions:")
            for i, mission in enumerate(fsociety_missions, 1):
                print(f"{i}. {Fore.CYAN}{mission['title']}{Fore.WHITE}")
                print(f"   {mission['description']}")
                print(f"   Target: {mission['target']}")
            
            mission_choice = input(Fore.CYAN + "\nAccept mission (number) or 'back': " + Fore.WHITE)
            if mission_choice.isdigit() and 1 <= int(mission_choice) <= len(fsociety_missions):
                mission = fsociety_missions[int(mission_choice) - 1]
                game_state.player["current_mission"] = mission["id"]
                print(Fore.GREEN + f"\nMission accepted: {mission['title']}")
    
    elif choice == "2":
        print(Fore.WHITE + """
Five/Nine Attack Plan:

Phase 1: [COMPLETE] Infiltrate Steel Mountain (E Corp's backup facility)
Phase 2: [ACTIVE] Develop encryption malware for all E Corp systems
Phase 3: [PENDING] Deploy malware across all 71 E Corp buildings simultaneously
Phase 4: [PENDING] Destroy backup tapes at Steel Mountain
Phase 5: [PENDING] Public announcement claiming responsibility

Current Progress: 42%
Estimated timeline: 17 days until execution
        """)
    
    elif choice == "3":
        print(Fore.WHITE + """
Recent Communications:

[Darlene] We need more people on the Steel Mountain operation.
[Trenton] Encryption algorithm testing is proceeding well.
[Mobley] Security around E Corp headquarters has increased.
[Romero] Hardware for the final phase is being assembled.
[Mr. Robot] Remember why we're doing this. Stay focused.

Secure Chat Channel: IRC://fsociety.offset-314159.onion
Next Meeting: Tomorrow, 23:00 EST, Coney Island location
        """)
    
    elif choice == "4":
        print(Fore.WHITE + """
E Corp Intelligence:

CEO: Phillip Price
CTO: Tyrell Wellick
Security Director: Scott Knowles

Key Vulnerabilities:
- Jenkins server accessible via VPN (credentials required)
- Outdated HVAC control systems at most facilities
- Executive terminal privilege escalation flaw
- Weak password rotation policies for mid-level employees

Security Alert Level: ELEVATED
Recent Security Changes: Added biometric verification to data centers
        """)
    
    elif choice.lower() == "back":
        return
    else:
        print(Fore.RED + "Invalid option.")
    
    # Return to the fsociety main menu
    input(Fore.CYAN + "\nPress Enter to return to main menu...")
    display_fsociety()

def display_ecorp_internal() -> None:
    """Display the E Corp internal site"""
    # This should only be accessible once specific missions are completed
    if game_state.player["reputation"] < 70:
        print(Fore.RED + """
===================================================
          ACCESS DENIED - E Corp Internal Network
===================================================

Your access attempt has been logged.
This incident will be reported to security.
    """)
        time.sleep(2)
        print(Fore.YELLOW + "Connection terminated.")
        game_state.connected_to_darkweb = False
        game_state.current_site = None
        return
    
    print(Fore.BLUE + """
 ______   ______     ______     ______     ______  
/\  ___\ /\  ___\   /\  __ \   /\  == \   /\  == \ 
\ \  __\ \ \ \____  \ \ \/\ \  \ \  __<   \ \  _-/ 
 \ \_____\\ \_____\  \ \_____\  \ \_\ \_\  \ \_\   
  \/_____/ \/_____/   \/_____/   \/_/ /_/   \/_/   
===================================================
          INTERNAL NETWORK - Authorized Users Only
===================================================
    """)
    
    print(Fore.RED + "WARNING: You have illegally accessed E Corp's internal network.")
    print("This is for storytelling purposes only. Unauthorized access to real systems is illegal.")
    
    menu_options = [
        "Employee Directory",
        "Project Dashboard",
        "Financial Records",
        "Security Protocols"
    ]
    
    print(Fore.WHITE + "\nE Corp Systems:")
    for i, option in enumerate(menu_options, 1):
        print(f"{i}. {option}")
    
    choice = input(Fore.CYAN + "\nSelect option (or 'back'): " + Fore.WHITE)
    
    if choice == "1":
        print(Fore.WHITE + """
Employee Directory:

Executive Team:
- Phillip Price (CEO)
- Tyrell Wellick (CTO)
- Angela Moss (PR Director)
- Scott Knowles (CTO Candidate)
- Sharon Knowles (Legal Director)

Security Team:
- Michael Hansen (CSO)
- James Williams (SOC Lead)
- Sarah Chen (Incident Response)
- Thomas Reed (Threat Intelligence)

IT Operations:
- Kevin Lynch (CIO)
- Marcus Brown (Infrastructure)
- Olivia Martinez (Applications)
- David Garcia (Network Operations)
        """)
    
    elif choice == "2":
        print(Fore.WHITE + """
Project Dashboard:

Active Projects:
- Project Olympus: E-Coin global deployment (Priority: HIGH)
- Project Sentinel: Security infrastructure upgrade (Priority: MEDIUM)
- Project Phoenix: Legacy system migration (Priority: MEDIUM)
- Project Atlas: Data center consolidation (Priority: LOW)

Recently Completed:
- Project Monarch: Executive communications encryption
- Project Icarus: Cloud transition phase 1
        """)
    
    elif choice == "3":
        print(Fore.WHITE + """
Financial Records:

Quarterly Earnings (Last Quarter):
- Revenue: $12.8 billion
- Net Income: $3.2 billion
- E-Coin Transaction Volume: $89.7 million

Loan Portfolio:
- Consumer Debt Holdings: $832 billion
- Corporate Loans: $1.3 trillion
- International Finance: $752 billion

Market Position:
- Global Market Share: 72% of consumer credit
- E-Coin Adoption Rate: 37% month-over-month growth
        """)
    
    elif choice == "4":
        print(Fore.WHITE + """
Security Protocols:

Current Security Level: 4 (ELEVATED)
Recent Incidents: 3 attempted network intrusions (last 48 hours)

Active Measures:
- Enhanced monitoring on all VPN connections
- Two-factor authentication enforcement
- Intrusion Prevention Systems activated
- Regular credential rotation
- Air-gapped backup systems

Security Bulletin:
"Be aware of increased phishing attempts and social engineering
attacks targeting E Corp employees. Report any suspicious
communications to security@ecorp.com immediately."
        """)
    
    elif choice.lower() == "back":
        return
    else:
        print(Fore.RED + "Invalid option.")
    
    # Return to the E Corp main menu
    input(Fore.CYAN + "\nPress Enter to return to main menu...")
    display_ecorp_internal()

def display_dark_army() -> None:
    """Display the Dark Army site"""
    if not game_state.player["dark_army_contact"]:
        print(Fore.RED + "Connection terminated. This site does not exist.")
        game_state.connected_to_darkweb = False
        game_state.current_site = None
        return
    
    print(Fore.MAGENTA + """
╔╦╗╔═╗╦═╗╦╔═  ╔═╗╦═╗╔╦╗╦ ╦
 ║║╠═╣╠╦╝╠╩╗  ╠═╣╠╦╝║║║╚╦╝
═╩╝╩ ╩╩╚═╩ ╩  ╩ ╩╩╚═╩ ╩ ╩ 
===================================================
         "Those who control the answers..."
===================================================
    """)
    
    print(Fore.WHITE + "\nWelcome. Time is always of the essence.")
    
    menu_options = [
        "Active Operations",
        "Communication Protocols",
        "Whiterose's Directives",
        "Intelligence Reports"
    ]
    
    print(Fore.WHITE + "\nTerminal:")
    for i, option in enumerate(menu_options, 1):
        print(f"{i}. {option}")
    
    choice = input(Fore.CYAN + "\nSelect option (or 'back'): " + Fore.WHITE)
    
    if choice == "1":
        print(Fore.WHITE + """
Active Operations:

Operation Nightshade [PRIORITY]:
- Surveillance of key FSociety members
- Infiltration of E Corp security team
- Hardware deployment at designated locations

Operation Eclipse:
- Support for Whiterose's Washington Township project
- Resource procurement and security
        
Operation Phantom:
- Monitoring of intelligence agencies
- Counterintelligence measures
- Elimination of security risks (as necessary)
        """)
    
    elif choice == "2":
        print(Fore.WHITE + """
Communication Protocols:

- All communications must use Tox encryption (no exceptions)
- Verification phrase changes daily (check secure channel)
- Meeting locations are communicated via dead drop only
- All communications are to be deleted after reading
- Use only approved hardware for contact
- Alternate identities must be maintained meticulously

Current Verification: "The highest value sees the farthest light"
Next rotation: 12 hours
        """)
    
    elif choice == "3":
        print(Fore.WHITE + """
Whiterose's Directives:

"Time remains our most valuable asset. Schedules must be maintained
precisely. Delays are unacceptable."

"The Washington Township project takes absolute priority. All
resources necessary should be allocated without hesitation."

"FSociety serves a purpose. Monitor but do not interfere with their
operation against E Corp unless specifically instructed."

"Eliminate any threats to our operations with extreme prejudice.
No exceptions, no matter the target's significance."
        """)
    
    elif choice == "4":
        print(Fore.WHITE + """
Intelligence Reports:

E Corp:
- CEO Price suspects external manipulation but has no evidence
- Internal security focusing on wrong attack vectors
- Project Olympus (E-Coin) approaching critical deployment phase

Government:
- FBI operation "Python" is monitoring known hackers
- Agent DiPierro showing concerning pattern recognition skills
- NSA data collection poses minimal risk due to implemented countermeasures

FSociety:
- Five/Nine attack preparations proceeding as expected
- Key members showing expected psychological patterns
- Potential for successful operation: 78%
        """)
    
    elif choice.lower() == "back":
        return
    else:
        print(Fore.RED + "Invalid option.")
    
    # Return to the Dark Army main menu
    input(Fore.CYAN + "\nPress Enter to return to main menu...")
    display_dark_army()

def cmd_scan(args: str) -> None:
    """Scan an IP address"""
    target_ip = args.strip()
    if not target_ip:
        print(Fore.RED + "Error: no IP address provided")
        print("Usage: scan <ip>")
        return
    
    # Get the target information
    target = get_target_by_ip(target_ip)
    
    if not target:
        print(Fore.YELLOW + f"Scanning {target_ip}...")
        time.sleep(1)
        print(Fore.RED + "No response from host. This IP appears to be offline or firewalled.")
        return
    
    print(Fore.YELLOW + f"Scanning {target_ip}...")
    
    # Simulate scanning progress
    time.sleep(1)
    print("Port scanning in progress...")
    time.sleep(0.5)
    print("Service detection running...")
    time.sleep(0.5)
    print("OS fingerprinting...")
    time.sleep(0.5)
    print("Vulnerability scanning...")
    time.sleep(1)
    
    # Mark the target as discovered
    is_new = discover_ip(target_ip)
    
    if is_new:
        add_to_history(f"Discovered new target: {target['name']} ({target_ip})", Fore.GREEN)
    
    # Display scan results
    print(Fore.GREEN + "\nScan Results:")
    print(f"Target: {target['name']} ({target_ip})")
    print(f"Status: Online")
    
    # Show open ports/services
    print("\nOpen Ports:")
    for service in target["services"]:
        port = None
        if service == "http":
            port = 80
        elif service == "https":
            port = 443
        elif service == "ssh":
            port = 22
        elif service == "ftp":
            port = 21
        elif service == "smtp":
            port = 25
        elif service == "mysql":
            port = 3306
        elif service == "vpn":
            port = 1194
        elif service == "hvac":
            port = 8080
        elif service == "radius":
            port = 1812
        elif service == "building_management":
            port = 9090
        
        if port:
            print(f"  {port}/tcp - {service}")
        else:
            print(f"  unknown - {service}")
    
    # Only show vulnerabilities if security skill is high enough
    security_level = target["security_level"]
    security_skill_needed = max(1, security_level - 2)
    
    if game_state.player["skills"]["network"] >= security_skill_needed:
        print("\nPotential Vulnerabilities:")
        for vuln in target.get("vulnerabilities", []):
            print(f"  - {vuln}")
    else:
        print("\nVulnerability scan inconclusive. Need higher network skills.")
    
    # Show additional information if available
    if "description" in target:
        print(f"\nAdditional Info: {target['description']}")
    
    # Improve network skill
    if skill_level_up_check("network"):
        new_level = int(game_state.player["skills"]["network"])
        print(Fore.CYAN + f"\nSkill level up! Your network skills improved to level {new_level}!")

def cmd_hack(args: str) -> None:
    """Hack a target system"""
    target_ip = args.strip()
    if not target_ip:
        print(Fore.RED + "Error: no IP address provided")
        print("Usage: hack <ip>")
        return
    
    # Get the target information
    target = get_target_by_ip(target_ip)
    
    if not target:
        print(Fore.RED + f"Error: IP {target_ip} not found in database.")
        print("Try scanning the network first with the 'scan' command.")
        return
    
    # Make sure the target has been discovered
    if not target["discovered"]:
        print(Fore.RED + f"Error: Target {target_ip} not recognized. Scan it first.")
        return
    
    # Perform the hack
    perform_hack(target_ip, "hack")

def cmd_bruteforce(args: str) -> None:
    """Bruteforce attack on a target"""
    target_ip = args.strip()
    if not target_ip:
        print(Fore.RED + "Error: no IP address provided")
        print("Usage: bruteforce <ip>")
        return
    
    # Get the target information
    target = get_target_by_ip(target_ip)
    
    if not target:
        print(Fore.RED + f"Error: IP {target_ip} not found in database.")
        print("Try scanning the network first with the 'scan' command.")
        return
    
    # Make sure the target has been discovered
    if not target["discovered"]:
        print(Fore.RED + f"Error: Target {target_ip} not recognized. Scan it first.")
        return
    
    # Perform the bruteforce attack
    perform_hack(target_ip, "bruteforce")

def cmd_mission(args: str) -> None:
    """Manage missions"""
    parts = args.strip().split(maxsplit=1)
    subcommand = parts[0].lower() if parts else ""
    subargs = parts[1] if len(parts) > 1 else ""
    
    if not subcommand:
        # Display mission help
        print(Fore.YELLOW + "Mission Commands:")
        print("  mission list - List available missions")
        print("  mission info <id> - Show information about a mission")
        print("  mission accept <id> - Accept a mission")
        print("  mission current - Show current mission status")
        return
    
    if subcommand == "list":
        # List available missions
        available_missions = [m for m in game_state.missions if not m["completed"]]
        
        if not available_missions:
            print(Fore.YELLOW + "No missions available. Check back later.")
            return
        
        print(Fore.CYAN + "Available Missions:")
        for mission in available_missions:
            # Check if player meets requirements
            can_accept = True
            requirements = []
            
            if mission.get("requires_rep", 0) > game_state.player["reputation"]:
                can_accept = False
                requirements.append(f"Need {mission.get('requires_rep')} reputation")
            
            if mission.get("fsociety_required") and not game_state.player["fsociety_member"]:
                can_accept = False
                requirements.append("Need fsociety membership")
            
            # Display mission info
            status = f"{Fore.GREEN}[AVAILABLE]" if can_accept else f"{Fore.RED}[LOCKED]"
            print(f"{mission['id']}: {Fore.WHITE}{mission['title']} {status}")
            print(f"  Difficulty: {mission['difficulty']}/10")
            print(f"  Reward: {format_btc(mission['reward'])} BTC + {mission['rep_reward']} rep")
            
            if requirements:
                print(f"  Requirements: {', '.join(requirements)}")
    
    elif subcommand == "info":
        if not subargs:
            print(Fore.RED + "Error: no mission ID provided")
            print("Usage: mission info <id>")
            return
        
        mission_id = subargs.strip()
        mission = get_mission_by_id(mission_id)
        
        if not mission:
            print(Fore.RED + f"Error: mission {mission_id} not found")
            return
        
        # Display mission info
        print(Fore.CYAN + f"Mission: {mission['title']} ({mission_id})")
        print(Fore.WHITE + f"Description: {mission['description']}")
        print(f"Target: {mission['target']}")
        print(f"Difficulty: {mission['difficulty']}/10")
        print(f"Reward: {format_btc(mission['reward'])} BTC + {mission['rep_reward']} rep")
        
        if mission["completed"]:
            print(Fore.GREEN + "Status: Completed")
        else:
            print(Fore.YELLOW + "Status: Available")
            
            # Show requirements
            requirements = []
            if mission.get("requires_rep", 0) > game_state.player["reputation"]:
                requirements.append(f"Need {mission.get('requires_rep')} reputation")
            
            if mission.get("fsociety_required") and not game_state.player["fsociety_member"]:
                requirements.append("Need fsociety membership")
                
            if requirements:
                print(f"Requirements: {', '.join(requirements)}")
            
            # Show mission steps
            print("\nMission Steps:")
            for i, step in enumerate(mission["steps"], 1):
                if i <= mission["current_step"]:
                    print(f"  {i}. {Fore.GREEN}[DONE] {step}")
                else:
                    print(f"  {i}. {Fore.YELLOW}{step}")
    
    elif subcommand == "accept":
        if not subargs:
            print(Fore.RED + "Error: no mission ID provided")
            print("Usage: mission accept <id>")
            return
        
        mission_id = subargs.strip()
        mission = get_mission_by_id(mission_id)
        
        if not mission:
            print(Fore.RED + f"Error: mission {mission_id} not found")
            return
        
        # Check if mission is already completed
        if mission["completed"]:
            print(Fore.YELLOW + f"Mission {mission_id} has already been completed.")
            return
        
        # Check if player already has an active mission
        if game_state.player["current_mission"]:
            current_mission = get_mission_by_id(game_state.player["current_mission"])
            print(Fore.YELLOW + f"You already have an active mission: {current_mission['title']}")
            print("Complete it or use 'mission current' to view details.")
            return
        
        # Check requirements
        if mission.get("requires_rep", 0) > game_state.player["reputation"]:
            print(Fore.RED + f"You need {mission.get('requires_rep')} reputation for this mission.")
            print(f"Your current reputation: {game_state.player['reputation']}")
            return
        
        if mission.get("fsociety_required") and not game_state.player["fsociety_member"]:
            print(Fore.RED + "This mission requires fsociety membership.")
            return
        
        # Accept the mission
        game_state.player["current_mission"] = mission_id
        print(Fore.GREEN + f"Mission accepted: {mission['title']}")
        print(f"Target: {mission['target']}")
        print(f"First step: {mission['steps'][0]}")
        add_to_history(f"Accepted mission: {mission['title']}", Fore.GREEN)
    
    elif subcommand == "current":
        # Show current mission status
        if not game_state.player["current_mission"]:
            print(Fore.YELLOW + "You don't have an active mission.")
            print("Use 'mission list' to view available missions.")
            return
        
        mission = get_mission_by_id(game_state.player["current_mission"])
        if not mission:
            print(Fore.RED + "Error: current mission not found")
            game_state.player["current_mission"] = None
            return
        
        print(Fore.CYAN + f"Current Mission: {mission['title']} ({mission['id']})")
        print(Fore.WHITE + f"Description: {mission['description']}")
        print(f"Target: {mission['target']}")
        print(f"Reward: {format_btc(mission['reward'])} BTC + {mission['rep_reward']} rep")
        
        print("\nProgress:")
        for i, step in enumerate(mission["steps"], 1):
            if i < mission["current_step"]:
                print(f"  {i}. {Fore.GREEN}[COMPLETED] {step}")
            elif i == mission["current_step"]:
                print(f"  {i}. {Fore.YELLOW}[CURRENT] {step}")
            else:
                print(f"  {i}. {Fore.WHITE}{step}")
    
    else:
        print(Fore.RED + f"Unknown mission subcommand: {subcommand}")
        print("Type 'mission' for help.")

def cmd_shop(args: str) -> None:
    """Access the upgrade shop"""
    category = args.strip().lower()
    
    if not category:
        # Show shop menu
        print(Fore.CYAN + "Upgrade Shop Categories:")
        print(f"  1. CPU - Current: {game_state.pc['cpu']['name']} (Level {game_state.pc['cpu']['level']})")
        print(f"  2. RAM - Current: {game_state.pc['ram']['name']} {game_state.pc['ram']['size']} MB (Level {game_state.pc['ram']['level']})")
        print(f"  3. Storage - Current: {game_state.pc['storage']['name']} {game_state.pc['storage']['size']} GB (Level {game_state.pc['storage']['level']})")
        print(f"  4. Network - Current: {game_state.pc['network']['name']} {game_state.pc['network']['speed']} Mbps (Level {game_state.pc['network']['level']})")
        print(f"  5. Security - Current: {game_state.pc['security']['name']} (Level {game_state.pc['security']['level']})")
        print()
        print(f"Your BTC balance: {format_btc(game_state.player['bitcoin'])} (${get_btc_usd_value(game_state.player['bitcoin']):.2f})")
        
        # Get shop selection
        selection = input(Fore.YELLOW + "Enter category number (or 'back'): ")
        
        if selection.lower() == "back":
            return
            
        if selection not in ["1", "2", "3", "4", "5"]:
            print(Fore.RED + "Invalid selection.")
            cmd_shop("")
            return
            
        categories = ["cpu", "ram", "storage", "network", "security"]
        cmd_shop(categories[int(selection) - 1])
        return
    
    # Show upgrades for the selected category
    if category not in game_state.upgrades:
        print(Fore.RED + f"Unknown category: {category}")
        print("Available categories: cpu, ram, storage, network, security")
        return
    
    print(Fore.CYAN + f"{category.upper()} Upgrades:")
    
    current_level = game_state.pc[category]["level"]
    upgrades = game_state.upgrades[category]
    
    for upgrade in upgrades:
        level = upgrade["level"]
        name = upgrade["name"]
        cost = upgrade["cost"]
        
        # Add description based on category-specific attributes
        description = ""
        if category == "cpu":
            description = f"{upgrade['speed']} GHz, {upgrade['cores']} cores"
        elif category == "ram":
            description = f"{upgrade['size']} MB"
        elif category == "storage":
            description = f"{upgrade['size']} GB"
        elif category == "network":
            description = f"{upgrade['speed']} Mbps"
        
        # Format the display
        if level < current_level:
            status = f"{Fore.YELLOW}[OWNED]"
        elif level == current_level:
            status = f"{Fore.GREEN}[CURRENT]"
        else:
            can_afford = game_state.player["bitcoin"] >= cost
            status = f"{Fore.GREEN}[AVAILABLE]" if can_afford else f"{Fore.RED}[CANNOT AFFORD]"
        
        cost_str = f"Cost: {format_btc(cost)}" if level > current_level else ""
        print(f"  Level {level}: {name} - {description} {cost_str} {status}")
    
    print(f"\nYour balance: {format_btc(game_state.player['bitcoin'])}")
    print("To purchase, use: upgrade <category> <level>")

def cmd_upgrade(args: str) -> None:
    """Purchase an upgrade"""
    parts = args.strip().split()
    if len(parts) < 2:
        print(Fore.RED + "Error: category and level required")
        print("Usage: upgrade <category> <level>")
        print("Example: upgrade cpu 3")
        return
    
    category = parts[0].lower()
    
    try:
        level = int(parts[1])
    except ValueError:
        print(Fore.RED + "Error: level must be a number")
        return
    
    if category not in game_state.upgrades:
        print(Fore.RED + f"Unknown category: {category}")
        print("Available categories: cpu, ram, storage, network, security")
        return
    
    current_level = game_state.pc[category]["level"]
    
    if level <= current_level:
        print(Fore.YELLOW + f"You already own level {level} or better of {category}.")
        return
    
    # Find the upgrade
    upgrade = None
    for u in game_state.upgrades[category]:
        if u["level"] == level:
            upgrade = u
            break
    
    if not upgrade:
        print(Fore.RED + f"Error: level {level} not found for {category}")
        return
    
    # Check if player can afford it
    if game_state.player["bitcoin"] < upgrade["cost"]:
        print(Fore.RED + f"You cannot afford this upgrade. Cost: {format_btc(upgrade['cost'])}")
        print(f"Your balance: {format_btc(game_state.player['bitcoin'])}")
        return
    
    # Check if player is skipping levels
    if level > current_level + 1:
        print(Fore.YELLOW + f"Warning: You must upgrade to level {current_level + 1} first.")
        return
    
    # Purchase the upgrade
    success = upgrade_component(category, level)
    
    if success:
        print(Fore.GREEN + f"Upgrade successful! Your {category} is now: {game_state.pc[category]['name']}")
        # Additional details based on category
        if category == "cpu":
            print(f"Specs: {game_state.pc[category]['speed']} GHz, {game_state.pc[category]['cores']} cores")
        elif category == "ram":
            print(f"Size: {game_state.pc[category]['size']} MB")
        elif category == "storage":
            print(f"Capacity: {game_state.pc[category]['size']} GB")
        elif category == "network":
            print(f"Speed: {game_state.pc[category]['speed']} Mbps")
        
        print(f"Remaining balance: {format_btc(game_state.player['bitcoin'])}")
        add_to_history(f"Upgraded {category} to level {level}: {game_state.pc[category]['name']}", Fore.GREEN)
    else:
        print(Fore.RED + "Upgrade failed. Please try again.")

def cmd_bitcoin() -> None:
    """Check Bitcoin balance"""
    btc = game_state.player["bitcoin"]
    usd_value = get_btc_usd_value(btc)
    
    print(Fore.YELLOW + "Bitcoin Balance:")
    print(Fore.WHITE + f"  {format_btc(btc)} (${usd_value:.2f})")
    print(f"BTC/USD Rate: ${DEFAULT_BTC_VALUE:.2f}")
    
    if game_state.player["ecoin"] > 0:
        print(Fore.BLUE + "\nE-Coin Balance:")
        print(Fore.WHITE + f"  {game_state.player['ecoin']:.2f} E-Coin (${game_state.player['ecoin'] * DEFAULT_ECOIN_VALUE:.2f})")

def cmd_run(args: str) -> None:
    """Run a tool or script"""
    if not args:
        print(Fore.RED + "Error: no tool specified")
        print("Usage: run <tool> [args]")
        return
    
    parts = args.split(maxsplit=1)
    tool = parts[0]
    tool_args = parts[1] if len(parts) > 1 else ""
    
    # Current directory contents
    current_path = game_state.current_dir
    current = game_state.file_system
    
    # Navigate to the current directory
    for component in current_path.split('/'):
        if not component or component == '.' or component == '~':
            continue
            
        current = current[component]["content"]
    
    # Check if the tool exists
    if not tool in current:
        print(Fore.RED + f"Error: {tool} not found in current directory")
        return
    
    # Check if it's a file
    if current[tool]["type"] != "file":
        print(Fore.RED + f"Error: {tool} is not a file")
        return
    
    # Specific tool behaviors
    if tool == "network_scanner.py":
        if not tool_args:
            print(Fore.RED + "Error: no target specified")
            print("Usage: run network_scanner.py <target_ip>")
            return
        
        target_ip = tool_args.strip()
        cmd_scan(target_ip)
    
    elif tool == "bruteforce.py":
        if not tool_args:
            print(Fore.RED + "Error: no target specified")
            print("Usage: run bruteforce.py <target_ip>")
            return
        
        target_ip = tool_args.strip().split()[0]
        cmd_bruteforce(target_ip)
    
    elif tool == "rootkit_gen.py":
        if not tool_args:
            print(Fore.RED + "Error: no target specified")
            print("Usage: run rootkit_gen.py <target_ip>")
            return
        
        target_ip = tool_args.strip()
        # Special case for rootkit - this is an advanced hack
        perform_hack(target_ip, "exploit")
    
    elif tool == "data_exfiltrator.py":
        if not tool_args:
            print(Fore.RED + "Error: no target specified")
            print("Usage: run data_exfiltrator.py <target_ip> [path]")
            return
        
        args = tool_args.strip().split()
        target_ip = args[0]
        # This is an advanced data extraction hack
        success = perform_hack(target_ip, "hack")
        
        if success:
            # Simulate data extraction
            print(Fore.YELLOW + "\nExtracting data...")
            time.sleep(1)
            
            # Generate some fake data based on the target
            target = get_target_by_ip(target_ip)
            if target:
                if "E Corp" in target["name"]:
                    print(Fore.GREEN + "\nData extracted:")
                    print("- customer_database_partial.sql (2.3 GB)")
                    print("- executive_emails_q1.pst (156 MB)")
                    print("- financial_projections.xlsx (4.2 MB)")
                elif "Steel Mountain" in target["name"]:
                    print(Fore.GREEN + "\nData extracted:")
                    print("- hvac_control_protocols.pdf (8.7 MB)")
                    print("- facility_security_layout.dwg (12.4 MB)")
                    print("- backup_rotation_schedule.txt (2.1 KB)")
                else:
                    print(Fore.GREEN + "\nData extracted:")
                    print("- user_credentials.db (4.3 MB)")
                    print("- system_logs.gz (78.2 MB)")
                    print("- config_backups.tar (23.5 MB)")
    
    else:
        # Generic script execution
        print(Fore.YELLOW + f"Running {tool}...")
        time.sleep(1)
        print("...")
        time.sleep(0.5)
        print(f"Executed {tool} successfully.")

def main():
    """Main function to run the hacker terminal game"""
    # Initialize colorama
    colorama.init(autoreset=True)
    
    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Load the game
    if not load_game():
        print(Fore.YELLOW + "Starting new game...")
    else:
        print(Fore.GREEN + "Game loaded successfully!")
    
    # Print the header
    print_header()
    
    # Welcome message
    print("Welcome to ASATHOT - A Mr. Robot-inspired hacking simulation!")
    print("Type 'help' to see available commands.")
    
    # Main game loop
    while True:
        try:
            current_dir_display = game_state.current_dir
            if game_state.connected_to_darkweb:
                prompt = f"{Fore.RED}[{game_state.current_site}]{Fore.GREEN} $ "
            else:
                # Windows-style command prompt
                drive = "C:"
                if game_state.player["fsociety_member"]:
                    drive = "F:"  # F for fsociety
                elif game_state.player["dark_army_contact"]:
                    drive = "D:"  # D for Dark Army
                
                windows_path = current_dir_display.replace("/", "\\")
                if windows_path == "~":
                    windows_path = "\\Users\\Elliot"
                    
                prompt = f"{Fore.GREEN}{drive}{windows_path}>{Fore.GREEN} "
            
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
