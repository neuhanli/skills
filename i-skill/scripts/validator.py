"""
Data Validator - Secure input validation and sanitization for i-skill

This module provides comprehensive validation and sanitization for user data,
ensuring all inputs are safe and comply with privacy requirements.

Security Features:
- Input validation and type checking
- Pattern-based sanitization
- Safe error handling without information leakage
- Configurable validation rules
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class ValidationError(Exception):
    """Custom exception for validation-related errors"""
    pass


class DataValidator:
    def __init__(self, config_path: str = None):
        """Initialize validator with secure configuration loading"""
        self.config = self._load_config(config_path)
        self._compile_patterns()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration with security validation"""
        if config_path:
            try:
                config_file = Path(config_path)
                
                # Validate config file path
                if not config_file.exists():
                    raise ValidationError(f"Configuration file not found: {config_path}")
                
                # Check file size (prevent large config files)
                if config_file.stat().st_size > 1024 * 1024:  # 1MB limit
                    raise ValidationError("Configuration file too large")
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Validate configuration structure
                self._validate_config_structure(config)
                return config
                
            except (json.JSONDecodeError, ValidationError) as e:
                raise ValidationError(f"Invalid configuration: {str(e)}")
        
        # Return secure default configuration
        return {
            "data_validation": {
                "max_evidence_length": 20,
                "max_evidence_per_topic": 2,
                "max_total_evidence": 20,
                "max_topics_per_conversation": 5,
                "max_topics_per_session": 10
            },
            "sanitization_rules": {
                "remove_personal_identifiers": True,
                "remove_sensitive_info": True,
                "remove_profanity": True,
                "remove_timestamps": True
            }
        }
    
    def _validate_config_structure(self, config: Dict):
        """Validate configuration structure and values"""
        required_sections = ["data_validation", "sanitization_rules"]
        
        for section in required_sections:
            if section not in config:
                raise ValidationError(f"Missing configuration section: {section}")
        
        # Validate data validation settings
        data_validation = config["data_validation"]
        for key, default_value in [
            ("max_evidence_length", 20),
            ("max_evidence_per_topic", 2),
            ("max_total_evidence", 20),
            ("max_topics_per_conversation", 5),
            ("max_topics_per_session", 10)
        ]:
            if key not in data_validation:
                raise ValidationError(f"Missing data_validation key: {key}")
            
            value = data_validation[key]
            if not isinstance(value, int) or value <= 0:
                raise ValidationError(f"Invalid value for {key}: {value}")

    def _compile_patterns(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
        self.credit_card_pattern = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
        self.ssn_pattern = re.compile(r'\b\d{3}[-]?\d{2}[-]?\d{4}\b')
        self.ip_pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
        self.url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
        self.timestamp_pattern = re.compile(r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|\b\d{1,2}:\d{2}(:\d{2})?\b')
        self.date_pattern = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b')
        self.name_pattern = re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b')

    def validate_evidence(self, evidence: str, topic: str, current_evidence_count: int, topic_evidence_count: int) -> Tuple[bool, str, Optional[str]]:
        if not evidence or not isinstance(evidence, str):
            return False, "Evidence must be a non-empty string", None

        truncated_evidence = evidence[:self.config["data_validation"]["max_evidence_length"]]

        if self.config["sanitization_rules"]["remove_personal_identifiers"]:
            if self._contains_personal_identifiers(truncated_evidence):
                return False, "Evidence contains personal identifiers", None

        if self.config["sanitization_rules"]["remove_sensitive_info"]:
            if self._contains_sensitive_info(truncated_evidence):
                return False, "Evidence contains sensitive information", None

        if self.config["sanitization_rules"]["remove_profanity"]:
            if self._contains_profanity(truncated_evidence):
                return False, "Evidence contains inappropriate content", None

        if self.config["sanitization_rules"]["remove_timestamps"]:
            if self._contains_timestamps(truncated_evidence):
                return False, "Evidence contains temporal markers", None

        if current_evidence_count >= self.config["data_validation"]["max_total_evidence"]:
            return False, f"Maximum total evidence ({self.config['data_validation']['max_total_evidence']}) exceeded", None

        if topic_evidence_count >= self.config["data_validation"]["max_evidence_per_topic"]:
            return False, f"Maximum evidence per topic ({self.config['data_validation']['max_evidence_per_topic']}) exceeded", None

        return True, "Valid", truncated_evidence

    def validate_topic_count(self, current_topic_count: int, is_conversation: bool = True) -> Tuple[bool, str]:
        if is_conversation:
            max_topics = self.config["data_validation"]["max_topics_per_conversation"]
        else:
            max_topics = self.config["data_validation"]["max_topics_per_session"]

        if current_topic_count >= max_topics:
            return False, f"Maximum topics ({max_topics}) exceeded for {'conversation' if is_conversation else 'session'}"

        return True, "Valid"

    def sanitize_text(self, text: str) -> str:
        sanitized = text

        if self.config["sanitization_rules"]["remove_personal_identifiers"]:
            sanitized = self._remove_personal_identifiers(sanitized)

        if self.config["sanitization_rules"]["remove_sensitive_info"]:
            sanitized = self._remove_sensitive_info(sanitized)

        if self.config["sanitization_rules"]["remove_profanity"]:
            sanitized = self._remove_profanity(sanitized)

        if self.config["sanitization_rules"]["remove_timestamps"]:
            sanitized = self._remove_timestamps(sanitized)

        return sanitized

    def _contains_personal_identifiers(self, text: str) -> bool:
        patterns = [self.email_pattern, self.phone_pattern, self.ssn_pattern, self.name_pattern]
        return any(pattern.search(text) for pattern in patterns)

    def _contains_sensitive_info(self, text: str) -> bool:
        patterns = [self.credit_card_pattern, self.ip_pattern, self.url_pattern]
        return any(pattern.search(text) for pattern in patterns)

    def _contains_profanity(self, text: str) -> bool:
        profanity_list = ['fuck', 'shit', 'damn', 'ass', 'bitch', 'crap', 'hell', 'bastard']
        text_lower = text.lower()
        return any(word in text_lower for word in profanity_list)

    def _contains_timestamps(self, text: str) -> bool:
        patterns = [self.timestamp_pattern, self.date_pattern]
        return any(pattern.search(text) for pattern in patterns)

    def _remove_personal_identifiers(self, text: str) -> str:
        text = self.email_pattern.sub('[EMAIL]', text)
        text = self.phone_pattern.sub('[PHONE]', text)
        text = self.ssn_pattern.sub('[SSN]', text)
        text = self.name_pattern.sub('[NAME]', text)
        return text

    def _remove_sensitive_info(self, text: str) -> str:
        text = self.credit_card_pattern.sub('[CARD]', text)
        text = self.ip_pattern.sub('[IP]', text)
        text = self.url_pattern.sub('[URL]', text)
        return text

    def _remove_profanity(self, text: str) -> str:
        profanity_list = ['fuck', 'shit', 'damn', 'ass', 'bitch', 'crap', 'hell', 'bastard']
        for word in profanity_list:
            text = re.sub(r'\b' + word + r'\b', '[REDACTED]', text, flags=re.IGNORECASE)
        return text

    def _remove_timestamps(self, text: str) -> str:
        text = self.timestamp_pattern.sub('[DATE]', text)
        text = self.date_pattern.sub('[DATE]', text)
        return text

    def validate_profile_update(self, profile_data: Dict, current_evidence: Dict) -> Tuple[bool, str]:
        total_evidence = sum(len(evidences) for evidences in current_evidence.values())

        for topic, evidences in profile_data.items():
            if topic in current_evidence:
                topic_count = len(current_evidence[topic])
            else:
                topic_count = 0

            for evidence in evidences:
                is_valid, message, _ = self.validate_evidence(
                    evidence, topic, total_evidence, topic_count
                )
                if not is_valid:
                    return False, message

                total_evidence += 1
                topic_count += 1

        return True, "Valid"
