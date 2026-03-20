import json
from typing import Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime


class AccessControl:
    def __init__(self, user_data_path: str = "./user_data", config_path: str = None):
        self.user_data_path = Path(user_data_path)
        self.user_data_path.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config(config_path)
        self.consent_file = self.user_data_path / "consent_state.json"
        self.access_log_file = self.user_data_path / "access_log.json"
        
        self._initialize_consent_state()

    def _load_config(self, config_path: str) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "access_control": {
                "read_only": True,
                "require_consent": True,
                "log_all_access": True
            }
        }

    def _initialize_consent_state(self):
        if not self.consent_file.exists():
            default_state = {
                "allowed_skills": [],
                "denied_skills": [],
                "pending_skills": [],
                "first_time_prompted": {}
            }
            with open(self.consent_file, 'w', encoding='utf-8') as f:
                json.dump(default_state, f, indent=2)

    def _load_consent_state(self) -> Dict:
        with open(self.consent_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_consent_state(self, state: Dict):
        with open(self.consent_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

    def _load_access_log(self) -> list:
        if not self.access_log_file.exists():
            return []
        
        with open(self.access_log_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_access_log(self, log: list):
        with open(self.access_log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2)

    def check_access_permission(self, skill_name: str) -> Tuple[bool, str, Optional[str]]:
        # 首先检查i-skill是否激活
        if not self._is_i_skill_active():
            return False, "i-skill is not active. User must activate personalization first.", None
        
        state = self._load_consent_state()

        if skill_name in state["denied_skills"]:
            return False, f"Access denied: {skill_name} is not allowed to access profile", None

        if skill_name in state["allowed_skills"]:
            return True, f"Access granted: {skill_name} has permission", None

        if self.config["access_control"]["require_consent"]:
            state["pending_skills"].append(skill_name)
            self._save_consent_state(state)
            return False, f"Consent required: {skill_name} needs user approval", "CONSENT_REQUIRED"

        return False, f"Access denied: {skill_name} does not have permission", None

    def grant_consent(self, skill_name: str) -> Tuple[bool, str]:
        state = self._load_consent_state()

        if skill_name in state["denied_skills"]:
            state["denied_skills"].remove(skill_name)

        if skill_name not in state["allowed_skills"]:
            state["allowed_skills"].append(skill_name)

        if skill_name in state["pending_skills"]:
            state["pending_skills"].remove(skill_name)

        state["first_time_prompted"][skill_name] = True
        self._save_consent_state(state)

        self._log_access(skill_name, "CONSENT_GRANTED", True)

        return True, f"Consent granted for {skill_name}"

    def revoke_consent(self, skill_name: str) -> Tuple[bool, str]:
        state = self._load_consent_state()

        if skill_name in state["allowed_skills"]:
            state["allowed_skills"].remove(skill_name)

        if skill_name not in state["denied_skills"]:
            state["denied_skills"].append(skill_name)

        if skill_name in state["pending_skills"]:
            state["pending_skills"].remove(skill_name)

        self._save_consent_state(state)

        self._log_access(skill_name, "CONSENT_REVOKED", True)

        return True, f"Consent revoked for {skill_name}"

    def read_profile(self, skill_name: str) -> Tuple[bool, str, Optional[str]]:
        has_permission, message, status = self.check_access_permission(skill_name)

        if not has_permission:
            return False, message, status

        profile_file = self.user_data_path / "myself.md"

        if not profile_file.exists():
            return False, "Profile not found", None

        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile_content = f.read()

            if self.config["access_control"]["log_all_access"]:
                self._log_access(skill_name, "READ", True)

            return True, "Profile read successfully", profile_content

        except Exception as e:
            return False, f"Error reading profile: {str(e)}", None

    def write_profile(self, skill_name: str, content: str) -> Tuple[bool, str]:
        # 首先检查i-skill是否激活
        if not self._is_i_skill_active():
            return False, "i-skill is not active. Cannot write profile"
        
        # 然后检查权限
        has_permission, message, status = self.check_access_permission(skill_name)
        if not has_permission:
            return False, f"Permission denied: {message}"
        
        # 最后检查read_only配置
        if self.config["access_control"]["read_only"]:
            return False, "Profile is read-only for dependent skills"

        profile_file = self.user_data_path / "myself.md"

        try:
            with open(profile_file, 'w', encoding='utf-8') as f:
                f.write(content)

            if self.config["access_control"]["log_all_access"]:
                self._log_access(skill_name, "WRITE", True)

            return True, "Profile written successfully"

        except Exception as e:
            return False, f"Error writing profile: {str(e)}"

    def get_consent_status(self, skill_name: str) -> Dict:
        state = self._load_consent_state()

        return {
            "skill_name": skill_name,
            "is_allowed": skill_name in state["allowed_skills"],
            "is_denied": skill_name in state["denied_skills"],
            "is_pending": skill_name in state["pending_skills"],
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

    def get_access_log(self, skill_name: Optional[str] = None, limit: int = 100) -> list:
        log = self._load_access_log()

        if skill_name:
            filtered_log = [entry for entry in log if entry["skill_name"] == skill_name]
        else:
            filtered_log = log

        return filtered_log[-limit:]

    def _is_i_skill_active(self) -> bool:
        """检查i-skill是否激活"""
        state_file = self.user_data_path / "i-skill_state.json"
        if not state_file.exists():
            return False
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            return state.get("personalization_active", False)
        except:
            return False

    def _log_access(self, skill_name: str, action: str, consent: bool):
        if not self.config["access_control"]["log_all_access"]:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "skill_name": skill_name,
            "action": action,
            "user_consent": consent
        }

        log = self._load_access_log()
        log.append(log_entry)

        self._save_access_log(log)

    def clear_access_log(self) -> Tuple[bool, str]:
        try:
            self._save_access_log([])
            return True, "Access log cleared"
        except Exception as e:
            return False, f"Error clearing access log: {str(e)}"

    def is_first_time_access(self, skill_name: str) -> bool:
        state = self._load_consent_state()
        return not state["first_time_prompted"].get(skill_name, False)

    def get_pending_consents(self) -> list:
        state = self._load_consent_state()
        return state["pending_skills"]
