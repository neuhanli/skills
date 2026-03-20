# i-skill User Guide

Welcome to i-skill! This guide will help you understand how to use i-skill to get personalized responses.

## What is i-skill?

i-skill is your personal profile generator that learns about you from your conversations and helps AI assistants provide personalized responses.

### How It Works

i-skill analyzes your conversations to understand:
- Your interests (e.g., technology, sports, work)
- Your communication style (e.g., concise, detailed)
- Your preferences (e.g., likes code examples, prefers simple explanations)
- Your expertise level in different topics

Based on this information, i-skill creates a personal profile that helps AI assistants tailor responses to your needs.

## How to Use i-skill

### Manual Activation (Required)

**User must explicitly activate i-skill before any profile access:**

**Step 1: Activate Personalization**
- Say: "Activate personalization"
- i-skill loads and becomes active
- Profile is available for current conversation

**Step 2: Use with Dependent Skills**
- If a skill has `depends: - i-skill`, it indicates it can use profile data
- **Important**: i-skill must already be active via user activation
- If i-skill is not active, dependent skill cannot access profile

**Before activating, i-skill needs to learn about you:**
- Have 3-5 conversations with AI
- Talk about topics you're interested in
- Share your preferences naturally

**After activating:**
- i-skill personalizes all your responses
- Your profile keeps learning and improving
- You can pause/resume anytime

### For Skill Developers

If you're a skill developer and want your skill to support personalization, add a dependency declaration in your skill's SKILL.md:

**Steps:**
1. Add a `depends` field to your skill's SKILL.md
2. Declare dependency on i-skill
3. Add dependency management section

**Example:**
```yaml
---
name: "YourSkill"
description: "Your skill description"
depends:
  - i-skill
---

## Dependency Management

This skill depends on `i-skill` for personalized responses.

**Important**: i-skill must be manually activated by the user first.
**When Invoked**:
- If i-skill is active: Profile becomes available as read-only context
- If i-skill is not active: Profile is not available
- User is notified: "Profile available for [Skill Name]"
```

**Note**: Dependency declaration only indicates compatibility. User must manually activate i-skill first.

## Managing Your Profile

### View Your Profile
Say any of:
- "View my profile"
- "Show my profile"
- "My profile"
- "查看我的说明书"

This will show you what i-skill has learned about you.

### Pause Personalization
If you want to temporarily stop personalization:
- Say: "Pause personalization" or "Stop personalization"
- i-skill will stop applying your profile
- Your profile is still saved and can be resumed later

### Resume Personalization
To start personalization again:
- Say: "Resume personalization" or "Continue personalization"
- i-skill will start applying your profile again

### Reset Your Profile
If you want to start over:
- Say: "Reset profile" or "Delete profile"
- i-skill will ask for confirmation
- After confirmation, your profile is deleted
- i-skill will start learning about you from scratch

### Edit Your Profile Directly
You can also edit your profile file directly:
- Profile location: `./user_data/myself.md`
- Open the file in any text editor
- Make changes as needed
- Save the file
- i-skill will use your updated profile

## Getting the Best Experience

### Tips for Better Personalization

1. **Be Natural**: Just have normal conversations
   - Don't try to "train" i-skill
   - Let it learn naturally from your interactions

2. **Be Consistent**: Your communication style will be learned better
   - If you prefer concise answers, be concise in your requests
   - If you like detailed explanations, ask for them

3. **Share Your Interests**: Talk about topics you care about
   - Your hobbies (sports, music, games)
   - Your work (programming, writing, design)
   - Your interests (technology, science, art)

4. **Give Feedback**: If responses don't match your preferences
   - Say: "I prefer more concise answers"
   - Say: "I like detailed explanations"
   - i-skill will learn from your feedback

### When to Activate

**Activate personalization when:**
- You've had 3-5 conversations with AI
- You want consistent personalized responses
- You're using skills that support personalization

**Don't worry about:**
- When exactly to activate (just say "activate personalization")
- How to activate (it's just one command)
- Whether it's working (i-skill will apply it automatically)

## Privacy and Control

### Your Data, Your Control

- **Local Storage**: All data is stored on your device
- **No Cloud Upload**: Your profile never leaves your device
- **Full Control**: You can view, edit, delete anytime
- **Transparent**: You can see exactly what i-skill has learned

### What i-skill Stores

i-skill stores:
- High-level summaries of your interests (e.g., "interested in technology")
- Your communication style preferences (e.g., "prefers concise answers")
- Minimal evidence from conversations (1-2 brief keywords or phrases per topic)
- Statistics (conversation count, etc.)

### Evidence Storage Policy

**What is stored as evidence:**
- 1-2 brief keywords or phrases per topic (maximum 20 characters each)
- No full sentences or complete quotes
- No contextual information or surrounding text

**Example of stored evidence:**
- ✅ Stored: "AI", "machine learning", "NBA" (brief keywords)
- ❌ NOT stored: "I'm really interested in AI and machine learning" (full sentence)

### Content Sanitization

i-skill automatically removes:
- Personal identifiers (names, emails, phone numbers)
- Sensitive information (addresses, financial data)
- Profanity or inappropriate content
- Timestamps or temporal markers

### Data Collection Scope

**Conversation Analysis:**
- Scope: Only analyzes conversations where i-skill is active
- No historical scan: Does not scan entire conversation history
- Recent interactions: Only analyzes current and recent conversations
- Dependency activation: When activated by dependency, only analyzes current conversation

**Data Collection Limits:**
- Per conversation: Maximum 5 topics extracted
- Per session: Maximum 10 topics extracted
- No background collection: Does not collect data when not active

### Data Retention Policy

**Evidence Retention:**
- Maximum per topic: 1-2 evidence entries
- Total maximum: 20 evidence entries across all topics
- Automatic cleanup: Oldest evidence removed when limit exceeded
- User control: Users can manually delete any evidence

**Profile Retention:**
- No automatic deletion: Profile persists until user deletes it
- User control: Users can delete entire profile anytime
- Data portability: Users can export profile (copy myself.md)

### Enforcement Requirements

**Before storing any data, i-skill verifies:**
- Evidence length ≤ 20 characters (truncates if longer)
- No personal identifiers present
- No sensitive information present
- Evidence count ≤ 20 total
- Evidence count ≤ 2 per topic
- Topic count ≤ 5 per conversation
- Topic count ≤ 10 per session
- No historical scanning

**If any check fails: Data is not stored**

### Access Control

**User Access:**
- Full read/write access to profile
- Can view, edit, delete anytime
- Can pause/resume personalization

**Dependency Skill Access:**
- Read-only access: Dependent skills can only read profile
- No modification: Skills cannot modify profile
- Context-only: Profile provided as read-only context
- Explicit declaration: Skills must declare dependency in SKILL.md

**Consent Management:**
- First-time activation: Asks for explicit consent
- Example: "Skill [Name] wants to access your profile. Allow? (yes/no)"
- Remembers your choice for this skill
- You can revoke consent anytime
- Commands: "Allow [Skill Name]", "Deny [Skill Name]", "Revoke [Skill Name]"

**No Third-Party Access:**
- No cloud upload: Profile never leaves your device
- No API exposure: No external API endpoints
- No sharing: Profile not shared with third parties

**Access Logging:**
- Every profile access is logged
- Log includes: timestamp, skill_name, action, user_consent
- You can view logs: "Show profile access log"

### User Consent and Control

**Manual Activation Required:**
- User must explicitly activate i-skill: "Activate personalization"
- No automatic activation by dependent skills
- User has full control over when personalization is active

**Your Control:**
- Activate: "Activate personalization"
- Pause: "Pause personalization"
- Resume: "Resume personalization"
- View: "View my profile"
- Reset: "Reset profile"

**Transparency:**
- Always notify when profile is accessed
- Always indicate when personalization is applied
- Always show which skills are using your profile

## Troubleshooting

### Personalization Not Working

**Check:**
1. Is personalization activated? Say "View my profile" to check
2. Have you had enough conversations? Need 3-5 conversations
3. Is the profile complete? View profile to see what's recorded

**Solution:**
- If not activated, say "Activate personalization"
- If profile is incomplete, have more conversations
- If issues persist, try "Reset profile" and start over

### Profile Not Updating

**Check:**
1. Is i-skill analyzing conversations? It should update after each conversation
2. Are you providing new information? i-skill only updates with new info

**Solution:**
- Continue having conversations
- Share new topics or preferences
- Check profile after a few conversations

### Want to Start Over

**Solution:**
- Say "Reset profile"
- Confirm deletion
- Start fresh conversations

## FAQ

**Q: How long does it take to learn about me?**
A: Usually 3-5 conversations. The more you talk, the better it understands you.

**Q: Can I use i-skill with other skills?**
A: Yes! Many skills automatically activate i-skill for better personalization.

**Q: Is my data private?**
A: Yes. All data is stored locally on your device and never uploaded.

**Q: Can I edit my profile?**
A: Yes. You can view and edit your profile at any time.

**Q: What if I don't like personalization?**
A: You can pause or reset personalization anytime, or edit your profile directly.

## Getting Help

If you have questions or issues:
- Check this guide first
- View your profile to see what's recorded
- Try resetting and starting over if needed

Enjoy your personalized AI experience! 🎉
