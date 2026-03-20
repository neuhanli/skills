---
name: "i-skill"
description: "Generates and maintains a dynamic personal profile (myself.md) by analyzing user conversations. Provides persistent context for personalized responses. Integration: other skills can declare dependency on i-skill to access user profile."
version: "1.0.0"
tags: ["profile", "personal", "analysis", "conversation", "user-model", "personalization", "context"]

# Integration Support
integration_type: "persistent_context"
provides_context: "user_profile"
activation_mode: "automatic_on_dependency"
---

# i-skill - Personal Profile Generator

Analyzes user conversations to generate and maintain a dynamic personal profile for personalized responses.

## Core Functionality

### Data Collection
- Analyzes conversations for topics, communication style, preferences
- Records interests, expertise level, emotional patterns
- Maintains evidence for each profile entry

### Profile Generation
- Creates structured profile in `./user_data/myself.md`
- Tracks activation state in `./user_data/i-skill_state.json`
- Updates profile when new information emerges

### Context Provision
- Provides user profile as persistent context
- Enables other skills to access user characteristics
- Supports personalized response generation

## When to Invoke

### Automatic Invocation
1. **When other skills declare dependency**:
   - If a skill has `depends: - i-skill`, automatically activate i-skill
   - Load profile and provide context to dependent skill
   - Profile remains active throughout the conversation

2. **After user explicitly activates**:
   - User can activate via manual commands (see USER_GUIDE.md)
   - Once activated, profile applies to all subsequent responses

### Manual Invocation
User commands (see USER_GUIDE.md for details):
- View profile, reset profile, pause/resume personalization

## Integration with Other Skills

### Declare Dependency
Other skills can access user profile by declaring dependency:

```yaml
depends:
  - i-skill
```

### Access Profile
When dependency is declared:
1. i-skill automatically activates
2. Profile loads into conversation context
3. Dependent skill can access user characteristics
4. Profile remains active throughout the conversation

### Profile Structure
See USER_GUIDE.md for detailed profile format

## Data Storage

### Files
- `./user_data/myself.md`: User profile
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

## Core Principles

1. **Privacy First**: No original conversation text storage
2. **User Control**: Users can view, edit, delete profile anytime
3. **Explainability**: Every judgment has evidence
4. **No Unnecessary Updates**: Only when new information exists
5. **Smart Activation**: Auto-activate when sufficient context or dependency declared
6. **Complete Recording**: Record ALL topics and interests

## Success Criteria

- User feedback "you understand me better" increases
- Response style consistency improves
- Manual corrections decrease
- User continues using for 1+ month
- Dependent skills successfully access profile
