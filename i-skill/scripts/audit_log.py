import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from enum import Enum


class AuditAction(Enum):
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    CONSENT_GRANTED = "CONSENT_GRANTED"
    CONSENT_DENIED = "CONSENT_DENIED"
    CONSENT_REVOKED = "CONSENT_REVOKED"
    CONSENT_RESTORED = "CONSENT_RESTORED"
    ACCESS_DENIED = "ACCESS_DENIED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    SANITIZATION_APPLIED = "SANITIZATION_APPLIED"
    PROFILE_UPDATED = "PROFILE_UPDATED"
    PROFILE_RESET = "PROFILE_RESET"
    SKILL_ACTIVATED = "SKILL_ACTIVATED"
    SKILL_DEACTIVATED = "SKILL_DEACTIVATED"


class AuditLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditLog:
    def __init__(self, user_data_path: str = "./user_data", config_path: str = None):
        self.user_data_path = Path(user_data_path)
        self.user_data_path.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config(config_path)
        self.audit_log_file = self.user_data_path / "audit_log.json"
        self.defensive_log_file = self.user_data_path / "defensive_log.json"
        self.metrics_file = self.user_data_path / "audit_metrics.json"
        
        self._initialize_audit_log()
        self._initialize_defensive_log()
        self._initialize_metrics()

    def _load_config(self, config_path: str) -> Dict:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "audit": {
                "log_all_access": True,
                "log_all_writes": True,
                "log_all_consents": True,
                "log_validation_failures": True,
                "log_sanitization": True,
                "max_log_size": 10000,
                "log_rotation": True,
                "export_format": "json"
            }
        }

    def _initialize_audit_log(self):
        if not self.audit_log_file.exists():
            with open(self.audit_log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

    def _initialize_defensive_log(self):
        if not self.defensive_log_file.exists():
            with open(self.defensive_log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

    def _initialize_metrics(self):
        if not self.metrics_file.exists():
            default_metrics = {
                "total_entries": 0,
                "total_reads": 0,
                "total_writes": 0,
                "total_denied": 0,
                "total_consents": 0,
                "total_validations": 0,
                "total_sanitizations": 0,
                "skill_access_count": {},
                "last_updated": None
            }
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(default_metrics, f, indent=2)

    def _load_audit_log(self) -> List[Dict]:
        with open(self.audit_log_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_audit_log(self, log: List[Dict]):
        with open(self.audit_log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2)

    def _load_defensive_log(self) -> List[Dict]:
        with open(self.defensive_log_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_defensive_log(self, log: List[Dict]):
        with open(self.defensive_log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2)

    def _load_metrics(self) -> Dict:
        with open(self.metrics_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_metrics(self, metrics: Dict):
        metrics["last_updated"] = datetime.now().isoformat()
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)

    def _update_metrics(self, action: AuditAction, skill_name: Optional[str] = None):
        metrics = self._load_metrics()
        metrics["total_entries"] += 1

        if action == AuditAction.READ:
            metrics["total_reads"] += 1
        elif action == AuditAction.WRITE:
            metrics["total_writes"] += 1
        elif action == AuditAction.ACCESS_DENIED:
            metrics["total_denied"] += 1
        elif action in [AuditAction.CONSENT_GRANTED, AuditAction.CONSENT_DENIED, AuditAction.CONSENT_REVOKED]:
            metrics["total_consents"] += 1
        elif action == AuditAction.VALIDATION_FAILED:
            metrics["total_validations"] += 1
        elif action == AuditAction.SANITIZATION_APPLIED:
            metrics["total_sanitizations"] += 1

        if skill_name:
            if skill_name not in metrics["skill_access_count"]:
                metrics["skill_access_count"][skill_name] = 0
            metrics["skill_access_count"][skill_name] += 1

        self._save_metrics(metrics)

    def log(self, skill_name: str, action: str, message: str,
            details: Optional[Dict] = None, level: str = "INFO",
            user_consent: Optional[bool] = None, success: bool = True) -> Tuple[bool, str]:
        
        if not self._should_log(action):
            return True, "Logging disabled for this action type"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "level": level,
            "success": success,
            "skill_name": skill_name,
            "user_consent": user_consent,
            "details": details or {}
        }

        try:
            if level in [AuditLevel.ERROR, AuditLevel.CRITICAL]:
                self._log_to_defensive_log(log_entry)
            else:
                self._log_to_audit_log(log_entry)

            self._update_metrics(action, skill_name)

            return True, "Log entry created successfully"

        except Exception as e:
            return False, f"Failed to create log entry: {str(e)}"

    def _should_log(self, action: str) -> bool:
        if action == "READ" and not self.config["audit"]["log_all_access"]:
            return False
        if action == "WRITE" and not self.config["audit"]["log_all_writes"]:
            return False
        if action in ["CONSENT_GRANTED", "CONSENT_DENIED", "CONSENT_REVOKED"] and not self.config["audit"]["log_all_consents"]:
            return False
        if action == "VALIDATION_FAILED" and not self.config["audit"]["log_validation_failures"]:
            return False
        if action == "SANITIZATION_APPLIED" and not self.config["audit"]["log_sanitization"]:
            return False

        return True

    def _log_to_audit_log(self, log_entry: Dict):
        log = self._load_audit_log()
        log.append(log_entry)

        if self.config["audit"]["log_rotation"] and len(log) > self.config["audit"]["max_log_size"]:
            log = log[-self.config["audit"]["max_log_size"]:]  # 修复日志轮转

        self._save_audit_log(log)  # 保存截断后的日志

    def _log_to_defensive_log(self, log_entry: Dict):
        log = self._load_defensive_log()
        log.append(log_entry)

        if self.config["audit"]["log_rotation"] and len(log) > self.config["audit"]["max_log_size"]:
            log = log[-self.config["audit"]["max_log_size"]:]  # 修复日志轮转

        self._save_defensive_log(log)  # 保存截断后的日志

    def get_audit_log(self, skill_name: Optional[str] = None, 
                      action: Optional[AuditAction] = None,
                      level: Optional[AuditLevel] = None,
                      limit: int = 100,
                      offset: int = 0) -> List[Dict]:
        log = self._load_audit_log()

        filtered_log = log

        if skill_name:
            filtered_log = [entry for entry in filtered_log if entry.get("skill_name") == skill_name]

        if action:
            filtered_log = [entry for entry in filtered_log if entry.get("action") == action.value]

        if level:
            filtered_log = [entry for entry in filtered_log if entry.get("level") == level.value]

        filtered_log = filtered_log[offset:offset + limit]

        return filtered_log

    def get_defensive_log(self, skill_name: Optional[str] = None,
                        level: Optional[AuditLevel] = None,
                        limit: int = 100,
                        offset: int = 0) -> List[Dict]:
        log = self._load_defensive_log()

        filtered_log = log

        if skill_name:
            filtered_log = [entry for entry in filtered_log if entry.get("skill_name") == skill_name]

        if level:
            filtered_log = [entry for entry in filtered_log if entry.get("level") == level.value]

        filtered_log = filtered_log[offset:offset + limit]

        return filtered_log

    def get_metrics(self) -> Dict:
        return self._load_metrics()

    def get_skill_access_summary(self, skill_name: str) -> Dict:
        metrics = self._load_metrics()
        audit_log = self._load_audit_log()

        skill_entries = [entry for entry in audit_log if entry.get("skill_name") == skill_name]

        reads = len([entry for entry in skill_entries if entry.get("action") == AuditAction.READ.value])
        writes = len([entry for entry in skill_entries if entry.get("action") == AuditAction.WRITE.value])
        denied = len([entry for entry in skill_entries if entry.get("action") == AuditAction.ACCESS_DENIED.value])
        errors = len([entry for entry in skill_entries if entry.get("level") in [AuditLevel.ERROR.value, AuditLevel.CRITICAL.value]])

        return {
            "skill_name": skill_name,
            "total_access": len(skill_entries),
            "reads": reads,
            "writes": writes,
            "denied": denied,
            "errors": errors,
            "access_count": metrics["skill_access_count"].get(skill_name, 0),
            "last_access": skill_entries[-1]["timestamp"] if skill_entries else None
        }

    def get_all_skills_summary(self) -> List[Dict]:
        metrics = self._load_metrics()
        audit_log = self._load_audit_log()

        skills = set()
        for entry in audit_log:
            if entry.get("skill_name"):
                skills.add(entry["skill_name"])

        summaries = []
        for skill_name in skills:
            summary = self.get_skill_access_summary(skill_name)
            summaries.append(summary)

        summaries.sort(key=lambda x: x["total_access"], reverse=True)

        return summaries

    def export_log(self, output_path: str, log_type: str = "audit", 
                   format: str = "json", filters: Optional[Dict] = None) -> Tuple[bool, str]:
        try:
            if log_type == "audit":
                log = self._load_audit_log()
            elif log_type == "defensive":
                log = self._load_defensive_log()
            else:
                return False, f"Unknown log type: {log_type}"

            if filters:
                if filters.get("skill_name"):
                    log = [entry for entry in log if entry.get("skill_name") == filters["skill_name"]]
                if filters.get("action"):
                    log = [entry for entry in log if entry.get("action") == filters["action"]]
                if filters.get("level"):
                    log = [entry for entry in log if entry.get("level") == filters["level"]]

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            if format == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(log, f, indent=2)
            elif format == "csv":
                import csv
                if log:
                    with open(output_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=log[0].keys())
                        writer.writeheader()
                        writer.writerows(log)
            else:
                return False, f"Unsupported format: {format}"

            return True, f"Log exported to {output_path}"

        except Exception as e:
            return False, f"Failed to export log: {str(e)}"

    def clear_log(self, log_type: str = "audit") -> Tuple[bool, str]:
        try:
            if log_type == "audit":
                self._save_audit_log([])
            elif log_type == "defensive":
                self._save_defensive_log([])
            else:
                return False, f"Unknown log type: {log_type}"

            return True, f"{log_type} log cleared successfully"

        except Exception as e:
            return False, f"Failed to clear log: {str(e)}"

    def get_recent_activity(self, hours: int = 24, limit: int = 50) -> List[Dict]:
        from datetime import timedelta

        audit_log = self._load_audit_log()
        security_log = self._load_security_log()

        all_logs = audit_log + security_log

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_logs = [
            entry for entry in all_logs 
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_time
        ]

        recent_logs.sort(key=lambda x: x["timestamp"], reverse=True)

        return recent_logs[:limit]

    def get_defensive_events(self, hours: int = 24) -> List[Dict]:
        from datetime import timedelta

        security_log = self._load_defensive_log()

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [
            entry for entry in security_log 
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_time
        ]

        recent_events.sort(key=lambda x: x["timestamp"], reverse=True)

        return recent_events

    def get_anomaly_report(self) -> Dict:
        metrics = self._load_metrics()
        audit_log = self._load_audit_log()
        security_log = self._load_security_log()

        denied_entries = [entry for entry in audit_log if entry.get("action") == AuditAction.ACCESS_DENIED.value]
        error_entries = [entry for entry in audit_log if entry.get("level") in [AuditLevel.ERROR.value, AuditLevel.CRITICAL.value]]

        skill_denials = {}
        for entry in denied_entries:
            skill_name = entry.get("skill_name", "unknown")
            if skill_name not in skill_denials:
                skill_denials[skill_name] = 0
            skill_denials[skill_name] += 1

        return {
            "total_denied_access": len(denied_entries),
            "total_errors": len(error_entries),
            "high_denial_skills": [
                {"skill": skill, "denials": count} 
                for skill, count in sorted(skill_denials.items(), key=lambda x: x[1], reverse=True)[:5]
            ],
            "recent_defensive_events": len(self.get_defensive_events(hours=24)),
            "recommendations": self._generate_recommendations(denied_entries, error_entries)
        }

    def _generate_recommendations(self, denied_entries: List[Dict], error_entries: List[Dict]) -> List[str]:
        recommendations = []

        if len(denied_entries) > 10:
            recommendations.append("High number of access denials detected. Review consent settings.")

        skill_denials = {}
        for entry in denied_entries:
            skill_name = entry.get("skill_name", "unknown")
            if skill_name not in skill_denials:
                skill_denials[skill_name] = 0
            skill_denials[skill_name] += 1

        for skill, count in skill_denials.items():
            if count > 5:
                recommendations.append(f"Skill '{skill}' has {count} denied accesses. Consider reviewing consent status.")

        if len(error_entries) > 5:
            recommendations.append("Multiple errors detected. Review system logs for details.")

        return recommendations
