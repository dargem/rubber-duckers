"""Loads keys form the json"""

import json
import os
from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path

@dataclass
class Bot:
    login: str
    password: str
    display_name: str
    member_email: str

class AccountProvider():
    def __init__(self):
        #loads bots
        self.person_index = 0

        # Load display names from bots.json
        with open("bots.json", "r") as f:
            data = json.load(f)

        # Load credentials from .env
        env_credentials = self._load_env_credentials()
        if not env_credentials:
            raise ValueError("No credentials found in .env file (need EMAIL and PASSWORD)")

        # Combine: use display names from bots.json with credentials from .env
        bots_data = data["bots"]
        self._bots = []
        
        for bot_data in bots_data:
            if "display_name" in bot_data:
                self._bots.append(Bot(
                    login=env_credentials["login"],
                    password=env_credentials["password"], 
                    display_name=bot_data["display_name"],
                    member_email=env_credentials["member_email"]
                ))
            else:
                print(f"Warning: Bot entry missing display_name: {bot_data}")
        
        if not self._bots:
            raise ValueError("No valid bot entries found in bots.json (need display_name)")
            
        print(f"Loaded {len(self._bots)} bot personas from bots.json using .env credentials")
        for i, bot in enumerate(self._bots):
            print(f"  Bot {i+1}: {bot.display_name} ({bot.login})")

    def _load_env_credentials(self) -> Optional[Dict[str, str]]:
        """Load credentials from .env file as fallback."""
        env_file = Path(".env")
        if not env_file.exists():
            return None

        env_vars = {}
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove surrounding quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    env_vars[key] = value

            # Extract required fields
            if all(key in env_vars for key in ["EMAIL", "PASSWORD", "NAME"]):
                return {
                    "login": env_vars["NAME"],  # Use NAME as the username for login
                    "member_email": env_vars["EMAIL"],  # Full email for member_email
                    "password": env_vars["PASSWORD"],
                    "display_name": env_vars["NAME"]  # Use NAME as display name too
                }
        except Exception as e:
            print(f"Error reading .env file: {e}")
        
        return None

    def get_account(self) -> Dict[str, str]:
        """Very basic key rotation for now"""
        if self.person_index >= len(self._bots) - 1:
            self.person_index = 0
        else:
            self.person_index += 1
        
        bot = self._bots[self.person_index]
        return {
            'login': bot.login,
            'password': bot.password,
            'display_name': bot.display_name,
            'member_email': bot.member_email
        }

    def get_current_account_info(self) -> str:
        """Get info about current account for logging."""
        bot = self._bots[self.person_index]
        return f"{bot.display_name} ({bot.login})"

    def get_total_accounts(self) -> int:
        """Get total number of available accounts."""
        return len(self._bots)
