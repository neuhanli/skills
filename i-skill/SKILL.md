---
name: "i-skill"
description: "Generates and maintains a dynamic personal profile (myself.md) by analyzing user conversations. Provides persistent context for personalized responses. Integration: other skills can declare dependency on i-skill to access user profile."
version: "1.0.0"
tags: ["profile", "personal", "analysis", "conversation", "user-model", "personalization", "context"]

# 新增命令定义
activation_commands:
  - "激活个性化"
  - "Activate personalization"
  - "开启个性化"

deactivation_commands:
  - "暂停个性化"
  - "Pause personalization"

# Integration Support
integration_type: "persistent_context"
provides_context: "user_profile"
activation_mode: "manual"  # Changed from automatic_on_dependency to manual
---

# i-skill - Personal Profile Generator

Analyzes user conversations to generate and maintain a dynamic personal profile for personalized responses.

## Core Functionality

### Data Collection
- Analyzes conversations for topics, communication style, preferences
- Records interests, expertise level, emotional patterns
- Maintains minimal evidence for each profile entry

### Profile Generation
- Creates structured profile in `./user_data/myself.md`
- Tracks activation state in `./user_data/i-skill_state.json`
- Updates profile when new information emerges

### Context Provision
- Provides user profile as persistent context
- Enables other skills to access user characteristics
- Supports personalized response generation

## When to Invoke

### Manual Activation Only
**User must explicitly activate i-skill before any profile access:**

1. **User initiates activation**:
   - User runs command: "Activate personalization" or similar
   - i-skill loads and becomes active
   - Profile is available for current conversation

2. **For dependent skills**:
   - If a skill has `depends: - i-skill`, it indicates it can use profile data
   - BUT: i-skill must already be active via user activation
   - If i-skill is not active, dependent skill cannot access profile

### User Commands
- "Activate personalization" - Enable profile generation and access
- "View my profile" - Display current profile
- "Pause personalization" - Temporarily disable
- "Resume personalization" - Re-enable
- "Reset profile" - Clear all profile data

## Integration with Other Skills

### Declare Dependency (Optional)
Other skills can indicate they support profile integration:

```yaml
depends:
  - i-skill
```

**Important**: This only indicates compatibility. i-skill must be manually activated by user first.

### Profile Access Flow
1. **User activates i-skill** (required first step)
2. **Dependent skill loads** (with dependency declared)
3. **Profile becomes available** as read-only context
4. **User is notified**: "Profile available for [Skill Name]"

### Profile Structure
Profile is stored in `./user_data/myself.md` with minimal evidence format.

## Data Storage

### Files
- `./user_data/myself.md`: User profile (read-only for dependent skills)
- `./user_data/i-skill_state.json`: Activation state and statistics

### State Format
```json
{
  "last_update_time": "2025-03-20T10:30:00",
  "conversation_count": 3,
  "personalization_active": false,
  "activation_threshold": 3,
  "topics_discussed": ["technology", "NBA", "work"]
}
```

## Security Implementation

### Skill-Level Security Controls

**Data Validation**
- Evidence length validation (≤ 20 characters)
- Personal identifier detection and removal
- Sensitive information detection and removal
- Profanity filtering
- Topic and evidence count limits

**Access Control**
- Profile is read-only for dependent skills
- No direct file modification by dependent skills
- All access attempts are logged

**User Consent Model**
- **Explicit activation required**: User must manually activate i-skill
- **No automatic profile access**: Dependent skills cannot trigger activation
- **User control**: Users can pause/resume/delete anytime

### Platform Recommendations (Optional)
For enhanced security, platforms can implement:

1. **File access monitoring** - Log all profile access attempts
2. **Consent UI** - Clear indication when profile is active
3. **Audit trails** - Track profile usage by skills

### Security Checklist

Before installation:
- [ ] Understand that user must manually activate i-skill
- [ ] Review data collection and storage practices
- [ ] Confirm platform supports basic file operations

During operation:
- [ ] User explicitly activates personalization
- [ ] All profile access is logged
- [ ] User can pause/resume/delete profile
- [ ] Profile is read-only for dependent skills

## Usage Examples

### For AI Agents

**Profile generation (when i-skill is active):**
```python
# Analyze conversation for profile updates
if i_skill_active:
    topics = extract_topics(conversation)
    for topic in topics:
        if is_new_information(topic):
            update_profile(topic, minimal_evidence=True)
```

**Profile access (for dependent skills):**
```python
# Check if i-skill is active before accessing profile
if i_skill_active:
    profile = read_profile()
    # Use profile data for personalization
else:
    # Handle case where profile is not available
    use_default_behavior()
```

### For Users

**Activation flow:**
1. User: "Activate personalization"
2. System: "Personalization activated. Profile will be generated from this conversation."
3. User: "What do you know about me?"
4. System: (Uses profile data) "Based on our conversations, you're interested in..."

**Deactivation flow:**
1. User: "Pause personalization"
2. System: "Personalization paused. Profile data will not be used."
3. User: "What do you know about me?"
4. System: "Personalization is currently paused. No profile data is being used."

## Privacy and Data Handling

### Data Collection Scope
- **Only when active**: Analyzes conversations only when i-skill is manually activated
- **Minimal evidence**: Stores 1-2 brief keywords per topic (max 20 characters)
- **User control**: Users can view, edit, delete profile anytime
- **No external sharing**: Profile never leaves user's device

### Evidence Storage Policy
**What is stored:**
- Brief keywords: "AI", "machine learning", "NBA"
- No full sentences or contextual information
- No personal identifiers or sensitive data

**What is NOT stored:**
- Full conversation text
- Personal information (names, emails, etc.)
- Timestamps or location data

## Additional Resources

- **User Guide**: [references/USER_GUIDE.md](references/USER_GUIDE.md) - Detailed user instructions
- **Implementation Details**: Technical implementation notes

## Key Design Changes

### Resolved Issues from Clawhub Review:

1. **✅ Fixed activation vs consent contradiction**:
   - Changed from `automatic_on_dependency` to `manual` activation
   - User must explicitly activate i-skill before any profile access
   - Dependent skills cannot trigger automatic activation

2. **✅ Simplified platform dependencies**:
   - Removed mandatory platform-level security requirements
   - Skill implements basic security controls internally
   - Platform enhancements are optional recommendations

3. **✅ Clearer user consent model**:
   - Explicit user activation required
   - No automatic data collection
   - User has full control over activation state

4. **✅ Reduced risk profile**:
   - No automatic activation reduces privilege escalation risk
   - Clear activation flow prevents unexpected behavior
   - User maintains control at all times

This design ensures i-skill functions safely even on platforms without advanced security features, while maintaining the core personalization functionality.