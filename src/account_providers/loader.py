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
    invite_code: str

class AccountProvider():
    def __init__(self):
        #loads bots
        self.person_index = 0

        # Load bot accounts from bots.json
        with open("bots.json", "r") as f:
            data = json.load(f)

        # Load invite code from .env
        invite_code = self._load_invite_code_from_env()
        if not invite_code:
            raise ValueError("No INVITE_CODE found in .env file")

        # Create bot instances from bots.json data
        bots_data = data["bots"]
        self._bots = []
        
        for bot_data in bots_data:
            if all(key in bot_data for key in ["user_name", "password", "display_name"]):
                self._bots.append(Bot(
                    login=bot_data["user_name"],
                    password=bot_data["password"], 
                    display_name=bot_data["display_name"],
                    invite_code=invite_code
                ))
            else:
                print(f"Warning: Bot entry missing required fields (user_name, password, display_name): {bot_data}")
        
        if not self._bots:
            raise ValueError("No valid bot entries found in bots.json")
            
        print(f"Loaded {len(self._bots)} bot accounts from bots.json with invite code from .env")
        for i, bot in enumerate(self._bots):
            print(f"  Bot {i+1}: {bot.display_name} ({bot.login})")

    def _load_invite_code_from_env(self) -> Optional[str]:
        """Load invite code from .env file."""
        env_file = Path(".env")
        if not env_file.exists():
            return None

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
                    
                    if key == "INVITE_CODE":
                        return value
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
            'invite_code': bot.invite_code
        }

    def get_current_account_info(self) -> str:
        """Get info about current account for logging."""
        bot = self._bots[self.person_index]
        return f"{bot.display_name} ({bot.login})"

    def get_total_accounts(self) -> int:
        """Get total number of available accounts."""
        return len(self._bots)
