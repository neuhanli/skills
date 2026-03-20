# i-skill

An intelligent personal profile generator that analyzes user conversations to create and maintain dynamic user profiles for personalized AI responses.

## Overview

i-skill is a persistent context skill that learns about users from their conversations and provides personalized context to AI assistants. It enables skills to deliver personalized responses based on user interests, communication style, and preferences.

## Features

- **Automatic Learning**: Analyzes conversations to understand user characteristics
- **Dynamic Profile**: Maintains an evolving user profile (myself.md)
- **Persistent Context**: Provides user profile as context throughout conversations
- **Skill Integration**: Other skills can declare dependency to access user profile
- **Privacy-First**: Stores only high-level summaries, not original conversations
- **User Control**: Users can view, edit, pause, or reset their profile anytime

## How It Works

### Data Collection

i-skill analyzes conversations to extract:
- **Topics**: User interests (e.g., technology, sports, work)
- **Communication Style**: Language habits, tone preferences
- **Task Style**: Goal-setting approach, problem-solving methods
- **Emotional Patterns**: Common emotions, expectations
- **Capabilities**: Skilled areas, tools used, expertise levels

### Profile Generation

Based on collected data, i-skill creates a structured profile:

```markdown
# Personal Profile

## Basic Profile
- **Inferred Occupation**: {occupation}
- **Common Tools**: {tools}
- **Interest Areas**: {areas}

## Communication Style
- **Language Habits**: {description}
- **Tone Preferences**: {description}

## Task Style
- **Goal Setting**: {description}
- **Problem Solving**: {description}

## Topics and Interests
- **Technology**: {description}
- **Sports**: {description}
- **Work**: {description}
```

### Context Provision

When activated, i-skill provides user profile as persistent context:
- Loads profile into conversation context
- Enables personalized response generation
- Maintains context throughout conversation
- Updates profile as new information emerges

## Installation

### Prerequisites

- Python 3.7+ (if using Python-based implementation)
- A skill platform that supports dependency management

### Setup

1. **Clone or Download i-skill**
   ```bash
   git clone <repository-url>
   cd i-skill
   ```

2. **Verify Structure**
   ```
   i-skill/
   ├── SKILL.md              # Skill definition
   ├── USER_GUIDE.md          # User guide (English)
   ├── 用户指南.md              # User guide (Chinese)
   ├── README.md               # This file
   └── user_data/             # User data directory
       ├── myself.md          # User profile
       └── i-skill_state.json # Activation state
   ```

3. **Create User Data Directory**
   ```bash
   mkdir -p user_data
   ```

4. **Initialize State File** (Optional)
   ```bash
   cat > user_data/i-skill_state.json << EOF
   {
     "last_update_time": "2025-03-20T00:00:00",
     "conversation_count": 0,
     "personalization_active": false,
     "activation_threshold": 3,
     "topics_discussed": []
   }
   EOF
   ```

## Usage

### For Users

#### Manual Activation

Simply say:
```
"Activate personalization"
```

i-skill will start applying your profile to all responses.

#### Automatic Activation

When using skills that depend on i-skill:
- i-skill activates automatically
- Profile is loaded and applied
- No manual action required

### For Skill Developers

#### Adding i-skill Dependency

To make your skill support personalization, add i-skill as a dependency:

**Step 1: Add Dependency Declaration**

In your skill's SKILL.md:

```yaml
---
name: "YourSkill"
description: "Your skill description"
depends:
  - i-skill
---
```

**Step 2: Add Dependency Management Section**

```markdown
## Dependency Management

This skill depends on `i-skill` for personalized responses.

**When Invoked**:
- Automatically activate i-skill
- i-skill will load user profile and provide personalized context
- See i-skill's USER_GUIDE.md for detailed personalization features
```

**That's it!** Your skill will now automatically benefit from i-skill's personalization.

#### Accessing User Profile

When your skill is invoked with i-skill dependency:

1. i-skill activates automatically
2. User profile loads into context
3. Access profile information:
   ```python
   # Example: Read user profile
   with open('./user_data/myself.md', 'r') as f:
       profile = f.read()
   
   # Parse profile and extract relevant information
   user_interests = parse_interests(profile)
   user_style = parse_style(profile)
   
   # Use profile to personalize responses
   response = personalize(response, user_interests, user_style)
   ```

## Configuration

### State File Format

`user_data/i-skill_state.json`:

```json
{
  "last_update_time": "2025-03-20T10:30:00",
  "conversation_count": 3,
  "personalization_active": false,
  "activation_threshold": 3,
  "topics_discussed": ["technology", "NBA", "work"]
}
```

### Activation Threshold

- **Minimum Conversations**: 3-5 conversations before activation
- **Minimum Topics**: At least 2 different topics
- **Clear Patterns**: Distinct communication style detected

## API Reference

### Skill Definition

**File**: `SKILL.md`

**Key Fields**:
```yaml
---
name: "i-skill"
description: "Generates and maintains a dynamic personal profile"
version: "1.0.0"
tags: ["profile", "personal", "analysis", "conversation", "user-model", "personalization", "context"]

# Integration Support
integration_type: "persistent_context"
provides_context: "user_profile"
activation_mode: "automatic_on_dependency"
---
```

### Profile Structure

**File**: `user_data/myself.md`

**Sections**:
- Basic Profile
- Communication Style
- Task Style
- Emotional Characteristics
- Capability Profile
- Topics and Interests
- Recent Updates

## Examples

### Example 1: Basic Integration

**Skill SKILL.md**:

```yaml
---
name: "NewsSearchSkill"
description: "Searches for news articles"
depends:
  - i-skill
---

## Dependency Management

This skill depends on `i-skill` for personalized news.

**When Invoked**:
- Automatically activate i-skill
- i-skill will load user profile and provide personalized context
```

**Result**: When user searches for news, results are personalized based on their interests.

### Example 2: Personalized Coding Assistant

**Skill SKILL.md**:

```yaml
---
name: "CodingAssistant"
description: "Provides code suggestions and explanations"
depends:
  - i-skill
---

## Dependency Management

This skill depends on `i-skill` for personalized coding assistance.

**When Invoked**:
- Automatically activate i-skill
- i-skill will load user profile and provide personalized context
```

**Result**: Code suggestions match user's programming style and expertise level.

## User Guide

For detailed user instructions, see:
- [USER_GUIDE.md](USER_GUIDE.md) - English version
- [用户指南.md](用户指南.md) - Chinese version

## Privacy and Security

### Data Storage

- **Local Only**: All data stored on user's device
- **No Cloud Upload**: Profile never leaves user's device
- **User Control**: Users can view, edit, delete anytime

### What's Stored

i-skill stores:
- High-level summaries of interests
- Communication style preferences
- Evidence from conversations (brief quotes)
- Statistics (conversation count, etc.)

i-skill does NOT store:
- Original conversation text
- Personal information (names, addresses, etc.)
- Sensitive data

## Troubleshooting

### Profile Not Activating

**Problem**: Personalization not working

**Solutions**:
1. Check if profile exists: `user_data/myself.md`
2. Verify activation state: `user_data/i-skill_state.json`
3. Ensure sufficient conversations (3-5)
4. Try manual activation: "Activate personalization"

### Dependency Not Working

**Problem**: Skills not accessing i-skill

**Solutions**:
1. Verify dependency declaration in SKILL.md
2. Check Dependency Management section exists
3. Ensure i-skill is installed and accessible
4. Review skill platform's dependency support

## FAQ

**Q: How long does it take to learn about a user?**
A: Usually 3-5 conversations. The more conversations, the better the understanding.

**Q: Can multiple skills use i-skill simultaneously?**
A: Yes. i-skill provides persistent context that can be accessed by multiple skills.

**Q: Is user data private?**
A: Yes. All data is stored locally and never uploaded to the cloud.

**Q: Can users edit their profile?**
A: Yes. Users can directly edit `user_data/myself.md` at any time.

**Q: What if a user doesn't want personalization?**
A: Users can pause or reset personalization anytime using voice commands.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Author

Created for Agent Skills platform

## Support

For issues or questions:
- Check [USER_GUIDE.md](USER_GUIDE.md) for detailed usage
- Review [SKILL.md](SKILL.md) for technical details
- Open an issue on the repository

---

**Enjoy personalized AI experiences with i-skill!** 🎉
