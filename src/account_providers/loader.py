"""Loads keys form the json"""

import json
from typing import Optional, List
from pathlib import Path
import twooter.sdk
from twooter import Twooter

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
        print("logging into accounts")
        self._bots = []
        for bot_data in bots_data:
            if all(key in bot_data for key in ["user_name", "password", "display_name"]):
                tweeter = twooter.sdk.new()
                login_result = tweeter.login(
                    username=bot_data["user_name"], 
                    password=bot_data["password"], 
                    display_name=bot_data["display_name"],
                    invite_code=invite_code
                )
                # Store the tweeter instance, not the login result
                self._bots.append(tweeter)
            else:
                print(f"Warning: Bot entry missing required fields (user_name, password, display_name): {bot_data}")
        
        if not self._bots:
            raise ValueError("No valid bot entries found in bots.json")
            
        print(f"Loaded {len(self._bots)} bot accounts from bots.json with invite code from .env")

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

    def get_account(self) -> Twooter:
        """Very basic key rotation for now"""
        if self.person_index >= len(self._bots) - 1:
            self.person_index = 0
        else:
            self.person_index += 1
        
        return self._bots[self.person_index]
    
    def get_all_accounts(self) -> List[Twooter]:
        """Returns all of them"""
        return self._bots


    def get_current_account_info(self) -> str:
        """Get info about current account for logging."""
        current_index = self.person_index
        if current_index < len(self._bots):
            return f"Bot account #{current_index + 1}"
        return "No active account"

    def get_total_accounts(self) -> int:
        """Get total number of available accounts."""
        return len(self._bots)
