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

### Way 1: Manual Activation (Simple)

**Just say: "Activate personalization"**

That's it! i-skill will start applying your profile to all responses.

**Before activating, i-skill needs to learn about you:**
- Have 3-5 conversations with AI
- Talk about topics you're interested in
- Share your preferences naturally

**After activating:**
- i-skill automatically personalizes all your responses
- No need to activate again
- Your profile keeps learning and improving

### Way 2: Automatic Activation (No Action Needed)

Many skills can automatically activate i-skill to provide better personalized responses.

**How It Works:**
1. When you use a skill that depends on i-skill  
  ```yaml
   depends:
  - i-skill
  ```yaml
2. i-skill activates automatically in the background
3. Your personal profile is loaded and applied
4. You get personalized responses without any extra effort
 
**Example:**
- You use a "coding assistant" skill
- The skill declares dependency on i-skill
- i-skill activates automatically
- The coding assistant now knows your programming style and preferences
- You get personalized code suggestions and explanations

**Benefits:**
- No manual activation needed
- Profile applies automatically when relevant
- Seamless experience across different skills

### Adding i-skill Support to Your Skills

If you're a skill developer and want your skill to support personalization, simply add a dependency declaration in your skill's SKILL.md:

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

**When Invoked**:
- Automatically activate i-skill
- i-skill will load user profile and provide personalized context
- See i-skill's USER_GUIDE.md for detailed personalization features
```

**That's it!** After adding these lines, when your skill is invoked, i-skill will automatically activate and provide personalized context.

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
- High-level summaries of your interests
- Your communication style preferences
- Evidence from conversations (brief quotes)
- Statistics (conversation count, etc.)

i-skill does NOT store:
- Original conversation text
- Personal information (names, addresses, etc.)
- Sensitive data

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
