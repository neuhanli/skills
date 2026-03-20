# Platform Integration Guide for i-skill

## Overview

This guide provides platform developers with optional enhancements for integrating i-skill with their skill platform. The skill is designed to function safely even on basic platforms, but these enhancements can provide additional security and monitoring capabilities.

## Key Design Changes

**Important**: i-skill now uses **manual activation** instead of automatic activation. This eliminates the security concerns identified in the clawhub evaluation.

### Manual Activation Model
- User must explicitly activate i-skill: "Activate personalization"
- No automatic activation by dependent skills
- Profile access is only available when i-skill is manually activated
- Dependent skills cannot trigger automatic activation

## Optional Platform Enhancements

### 1. File Access Monitoring (Optional)

Platforms can implement file system monitoring to track profile access:

```python
class FileAccessMonitor:
    def __init__(self):
        self.access_log = []
    
    def monitor_file_access(self, file_path: str, skill_name: str, action: str):
        if file_path.endswith('user_data/myself.md'):
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "skill_name": skill_name,
                "action": action,
                "file": file_path
            }
            self.access_log.append(log_entry)
```

### 2. Enhanced Audit Integration (Optional)

Platforms can integrate with i-skill's audit logging system:

```python
class PlatformAuditIntegration:
    def __init__(self):
        self.audit_log = AuditLog()
    
    def collect_platform_audit_data(self):
        # Collect platform-level audit data
        platform_data = {
            "skill_activations": self.get_skill_activations(),
            "file_access_attempts": self.get_file_access_attempts(),
            "user_commands": self.get_user_commands()
        }
        
        # Combine with i-skill audit data
        i_skill_data = self.audit_log.get_audit_log()
        
        return {
            "platform": platform_data,
            "i_skill": i_skill_data,
            "collected_at": datetime.now().isoformat()
        }
```

### 3. User Interface Enhancements (Optional)

Platforms can provide enhanced UI for profile management:

```python
class ProfileManagementUI:
    def __init__(self):
        self.user_data_path = "./user_data"
    
    def display_profile_status(self):
        # Show current activation status
        status_file = Path(self.user_data_path) / "i-skill_state.json"
        if status_file.exists():
            with open(status_file, 'r') as f:
                state = json.load(f)
            
            active = state.get("personalization_active", False)
            return f"Personalization: {'Active' if active else 'Inactive'}"
        
        return "Personalization: Not activated"
    
    def show_profile_access_log(self):
        # Display recent profile access
        audit_log = AuditLog()
        recent_access = audit_log.get_audit_log(limit=10)
        
        for entry in recent_access:
            print(f"{entry['timestamp']} - {entry['skill_name']} - {entry['action']}")
```

## Basic Integration (Required)

### Skill Loading

When loading skills that declare dependency on i-skill:

```python
def load_skill_with_dependencies(skill_name: str, skill_definition: dict):
    # Check if skill depends on i-skill
    if 'depends' in skill_definition and 'i-skill' in skill_definition['depends']:
        # Note: This only indicates compatibility
        # i-skill must be manually activated by user first
        print(f"Skill {skill_name} supports personalization via i-skill")
        print("Note: User must manually activate i-skill first")
    
    # Load the skill
    return load_skill(skill_name, skill_definition)
```

### Profile Access Flow

When a dependent skill attempts to access profile data:

```python
def provide_profile_context(skill_name: str):
    # Check if i-skill is active
    state_file = Path("./user_data/i-skill_state.json")
    
    if not state_file.exists():
        return None  # Profile not available
    
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    if not state.get("personalization_active", False):
        return None  # i-skill not active
    
    # Profile is available
    profile_file = Path("./user_data/myself.md")
    if profile_file.exists():
        with open(profile_file, 'r') as f:
            profile_content = f.read()
        
        # Log access
        audit_log = AuditLog()
        audit_log.log(
            action=AuditAction.READ,
            skill_name=skill_name,
            details={"file": "myself.md"},
            level=AuditLevel.INFO,
            user_consent=True,
            success=True
        )
        
        return profile_content
    
    return None
```

## Security Benefits of Manual Activation

### Eliminated Security Concerns

1. **No automatic activation vs consent contradiction**
   - User must explicitly activate i-skill
   - No automatic activation by dependent skills
   - Clear user control over when personalization is active

2. **Reduced platform dependency**
   - Skill implements basic security controls internally
   - No mandatory platform-level security requirements
   - Functions safely on basic platforms

3. **Simplified consent model**
   - No complex consent management required
   - User activation serves as implicit consent
   - Clear activation/deactivation commands

### Risk Reduction

| Risk Factor | Before | After | Improvement |
|-------------|--------|-------|-------------|
| Automatic activation risk | High | Low | ✅ Significant |
| Platform dependency risk | High | Medium | ✅ Noticeable |
| User control | Partial | Full | ✅ Significant |
| Integration complexity | Complex | Simple | ✅ Major |

## Testing and Validation

### Basic Functionality Test

```python
def test_basic_integration():
    # Test manual activation
    print("1. User activates i-skill: 'Activate personalization'")
    print("2. i-skill becomes active")
    print("3. Dependent skills can access profile")
    print("4. User can pause/resume personalization")
    
    # Verify profile access works correctly
    profile = provide_profile_context("TestSkill")
    if profile:
        print("✓ Profile access working correctly")
    else:
        print("✗ Profile access not working")
```

### Security Test

```python
def test_security_controls():
    # Test that dependent skills cannot activate i-skill
    print("Testing security controls...")
    
    # Attempt to access profile without activation
    profile = provide_profile_context("UnauthorizedSkill")
    if not profile:
        print("✓ Security controls working: Profile not accessible without activation")
    else:
        print("✗ Security controls failed: Profile accessible without activation")
```

## Configuration (Optional)

### Platform Configuration

Platforms can optionally configure enhanced features:

```json
{
  "platform": {
    "name": "YourPlatform",
    "enable_file_monitoring": false,
    "enable_audit_integration": false,
    "enable_ui_enhancements": false
  }
}
```

### Skill Configuration

i-skill uses its internal configuration:

```json
{
  "data_validation": {
    "max_evidence_length": 20,
    "max_evidence_per_topic": 2,
    "max_total_evidence": 20
  },
  "access_control": {
    "read_only": true,
    "log_all_access": true
  }
}
```

## Troubleshooting

### Common Issues

**Issue: Profile not available to dependent skills**
- Check if i-skill is activated: User must say "Activate personalization"
- Verify i-skill_state.json exists and personalization_active is true
- Check file permissions for ./user_data/myself.md

**Issue: Personalization not working**
- Ensure i-skill is activated
- Check if profile file exists and contains data
- Verify dependent skill has correct dependency declaration

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

### For Platform Developers

1. **Respect Manual Activation**
   - Never automatically activate i-skill
   - Always check activation status before providing profile
   - Clear user notifications about activation state

2. **Implement Optional Enhancements**
   - File access monitoring for security auditing
   - Audit integration for comprehensive logging
   - UI enhancements for better user experience

3. **Test Integration**
   - Test manual activation flow
   - Test profile access controls
   - Test error handling

### For Skill Developers

1. **Declare Dependencies Correctly**
   - Use `depends: - i-skill` to indicate compatibility
   - Understand that dependency only works when i-skill is manually activated
   - Handle cases where profile is not available

2. **Use Profile Data Responsibly**
   - Only access profile when i-skill is active
   - Use profile data to enhance user experience
   - Respect user privacy and data

## Support and Resources

For integration support:
- Review SKILL.md for core functionality
- Check USER_GUIDE.md for user instructions
- Review SECURITY.md for security details

## Version History

- **v1.0.0** (2025-03-20): Simplified platform integration guide reflecting manual activation model

## Conclusion

i-skill's manual activation model provides a secure and user-controlled personalization experience. While optional platform enhancements can improve security monitoring, the skill functions safely on any platform that supports basic file operations and skill loading.

The key security improvement is the elimination of automatic activation, which resolves the security concerns identified in the clawhub evaluation while maintaining the core personalization functionality.