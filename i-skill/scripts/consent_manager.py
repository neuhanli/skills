import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime


class ConsentManager:
    def __init__(self, user_data_path: str = "./user_data"):
        self.user_data_path = Path(user_data_path)
        self.user_data_path.mkdir(parents=True, exist_ok=True)
        
        self.consent_file = self.user_data_path / "consent_state.json"
        self.conversation_file = self.user_data_path / "consent_conversations.json"
        
        self._initialize_consent_state()
        self._initialize_conversation_log()

    def _initialize_consent_state(self):
        if not self.consent_file.exists():
            default_state = {
                "allowed_skills": [],
                "denied_skills": [],
                "pending_skills": [],
                "first_time_prompted": {},
                "consent_history": []
            }
            with open(self.consent_file, 'w', encoding='utf-8') as f:
                json.dump(default_state, f, indent=2)

    def _initialize_conversation_log(self):
        if not self.conversation_file.exists():
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

    def _load_consent_state(self) -> Dict:
        with open(self.consent_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_consent_state(self, state: Dict):
        with open(self.consent_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

    def _load_conversation_log(self) -> List[Dict]:
        with open(self.conversation_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_conversation_log(self, log: List[Dict]):
        with open(self.conversation_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2)

    def request_consent(self, skill_name: str, skill_description: str = "") -> Tuple[bool, str, Optional[str]]:
        state = self._load_consent_state()

        if skill_name in state["allowed_skills"]:
            return True, f"Consent already granted for {skill_name}", "GRANTED"

        if skill_name in state["denied_skills"]:
            return False, f"Consent previously denied for {skill_name}", "DENIED"

        if skill_name in state["pending_skills"]:
            return False, f"Consent request already pending for {skill_name}", "PENDING"

        state["pending_skills"].append(skill_name)
        self._save_consent_state(state)

        prompt = self._generate_consent_prompt(skill_name, skill_description)
        return False, prompt, "PROMPT_REQUIRED"

    def _generate_consent_prompt(self, skill_name: str, skill_description: str) -> str:
        base_prompt = f"Skill '{skill_name}' wants to access your personal profile."
        
        if skill_description:
            base_prompt += f"\n\nPurpose: {skill_description}"
        
        base_prompt += "\n\nYour profile contains:"
        base_prompt += "\n- Your interests and preferences"
        base_prompt += "\n- Your communication style"
        base_prompt += "\n- Your expertise level"
        
        base_prompt += "\n\nDo you allow this skill to access your profile?"
        base_prompt += "\n\nOptions:"
        base_prompt += "\n- 'yes' or 'allow' to grant access"
        base_prompt += "\n- 'no' or 'deny' to deny access"
        base_prompt += "\n- 'ask me later' to postpone decision"
        
        return base_prompt

    def process_consent_response(self, skill_name: str, response: str) -> Tuple[bool, str, Optional[str]]:
        state = self._load_consent_state()

        if skill_name not in state["pending_skills"]:
            return False, f"No pending consent request for {skill_name}", None

        response_lower = response.lower().strip()
        
        if response_lower in ['yes', 'y', 'allow', 'grant', 'approve']:
            return self._grant_consent(skill_name, state)
        elif response_lower in ['no', 'n', 'deny', 'reject', 'disapprove']:
            return self._deny_consent(skill_name, state)
        elif response_lower in ['ask me later', 'later', 'postpone']:
            return self._postpone_consent(skill_name)
        else:
            return False, "Invalid response. Please use 'yes', 'no', or 'ask me later'", None

    def _grant_consent(self, skill_name: str, state: Dict) -> Tuple[bool, str, Optional[str]]:
        state["pending_skills"].remove(skill_name)
        
        if skill_name not in state["allowed_skills"]:
            state["allowed_skills"].append(skill_name)
        
        state["first_time_prompted"][skill_name] = True
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "skill_name": skill_name,
            "action": "GRANTED",
            "user_response": "yes"
        }
        state["consent_history"].append(history_entry)
        
        self._save_consent_state(state)
        
        self._log_conversation(skill_name, "CONSENT_GRANTED", "User granted access")
        
        return True, f"Consent granted for {skill_name}", "GRANTED"

    def _deny_consent(self, skill_name: str, state: Dict) -> Tuple[bool, str, Optional[str]]:
        state["pending_skills"].remove(skill_name)
        
        if skill_name not in state["denied_skills"]:
            state["denied_skills"].append(skill_name)
        
        state["first_time_prompted"][skill_name] = True
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "skill_name": skill_name,
            "action": "DENIED",
            "user_response": "no"
        }
        state["consent_history"].append(history_entry)
        
        self._save_consent_state(state)
        
        self._log_conversation(skill_name, "CONSENT_DENIED", "User denied access")
        
        return False, f"Consent denied for {skill_name}", "DENIED"

    def _postpone_consent(self, skill_name: str) -> Tuple[bool, str, Optional[str]]:
        self._log_conversation(skill_name, "CONSENT_POSTPONED", "User postponed decision")
        
        return False, f"Consent request for {skill_name} postponed. You can decide later.", "POSTPONED"

    def revoke_consent(self, skill_name: str) -> Tuple[bool, str]:
        state = self._load_consent_state()

        if skill_name not in state["allowed_skills"]:
            return False, f"{skill_name} is not in the allowed list"

        state["allowed_skills"].remove(skill_name)
        
        if skill_name not in state["denied_skills"]:
            state["denied_skills"].append(skill_name)
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "skill_name": skill_name,
            "action": "REVOKED",
            "user_response": "revoke"
        }
        state["consent_history"].append(history_entry)
        
        self._save_consent_state(state)
        
        self._log_conversation(skill_name, "CONSENT_REVOKED", "User revoked consent")
        
        return True, f"Consent revoked for {skill_name}"

    def restore_consent(self, skill_name: str) -> Tuple[bool, str]:
        state = self._load_consent_state()

        if skill_name not in state["denied_skills"]:
            return False, f"{skill_name} is not in the denied list"

        state["denied_skills"].remove(skill_name)
        
        if skill_name not in state["allowed_skills"]:
            state["allowed_skills"].append(skill_name)
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "skill_name": skill_name,
            "action": "RESTORED",
            "user_response": "restore"
        }
        state["consent_history"].append(history_entry)
        
        self._save_consent_state(state)
        
        self._log_conversation(skill_name, "CONSENT_RESTORED", "User restored consent")
        
        return True, f"Consent restored for {skill_name}"

    def get_consent_status(self, skill_name: str) -> Dict:
        state = self._load_consent_state()

        return {
            "skill_name": skill_name,
            "status": "allowed" if skill_name in state["allowed_skills"] 
                     else "denied" if skill_name in state["denied_skills"]
                     else "pending" if skill_name in state["pending_skills"]
                     else "unknown",
            "first_time_prompted": state["first_time_prompted"].get(skill_name, False)
        }

    def get_all_consents(self) -> Dict:
        state = self._load_consent_state()

        return {
            "allowed_skills": state["allowed_skills"],
            "denied_skills": state["denied_skills"],
            "pending_skills": state["pending_skills"],
            "first_time_prompted": state["first_time_prompted"]
        }

    def get_consent_history(self, skill_name: Optional[str] = None, limit: int = 50) -> List[Dict]:
        state = self._load_consent_state()

        if skill_name:
            history = [entry for entry in state["consent_history"] if entry["skill_name"] == skill_name]
        else:
            history = state["consent_history"]

        return history[-limit:]

    def get_pending_consents(self) -> List[str]:
        state = self._load_consent_state()
        return state["pending_skills"]

    def clear_pending_consents(self) -> Tuple[bool, str]:
        state = self._load_consent_state()
        count = len(state["pending_skills"])
        state["pending_skills"] = []
        self._save_consent_state(state)
        return True, f"Cleared {count} pending consent requests"

    def _log_conversation(self, skill_name: str, action: str, message: str):
        log = self._load_conversation_log()
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "skill_name": skill_name,
            "action": action,
            "message": message
        }
        
        log.append(log_entry)
        self._save_conversation_log(log)

    def get_conversation_log(self, skill_name: Optional[str] = None, limit: int = 100) -> List[Dict]:
        log = self._load_conversation_log()

        if skill_name:
            filtered_log = [entry for entry in log if entry["skill_name"] == skill_name]
        else:
            filtered_log = log

        return filtered_log[-limit:]

    def is_first_time_access(self, skill_name: str) -> bool:
        state = self._load_consent_state()
        return not state["first_time_prompted"].get(skill_name, False)

    def get_consent_summary(self) -> Dict:
        state = self._load_consent_state()

        return {
            "total_allowed": len(state["allowed_skills"]),
            "total_denied": len(state["denied_skills"]),
            "total_pending": len(state["pending_skills"]),
            "total_history": len(state["consent_history"]),
            "skills": {
                "allowed": state["allowed_skills"],
                "denied": state["denied_skills"],
                "pending": state["pending_skills"]
            }
        }
