---
name: "i-skill"
description: "Generates personalized interaction guides by analyzing user conversations. Invoke when users seek personalized responses, want AI assistants to better understand their preferences, or need customized service adaptation. Activation: '激活个性化' or 'personalization'."
version: "2.0.0"
tags: ["personalization", "user-profile", "ai-assistant", "conversation-analysis"]
activation_mode: "manual"
---

# i-skill - Personalized Assistant Interaction Guide

Analyzes user conversations to generate personalized interaction guidelines, enabling AI assistants to provide customized service based on user preferences and communication patterns.

## Core Functionality

### Wisdom-Level Iterative Profiling
**Wisdom-Level Iterative User Profiling** - AI analyzes user conversations like an experienced sage, deeply understanding users through iterative optimization:

#### Iterative Optimization Mechanism
- **Re-examination instead of addition**: Each activation combines existing profile with new conversations for AI model input
- **Wisdom-level integration**: AI model regenerates more accurate user profiles based on complete conversation history
- **Content concentration**: Profile content is continuously refined, avoiding infinite expansion

#### Deep Psychological Insights
- **Inner world analysis**: Penetrates conversation surfaces to understand deep motivations, emotional patterns, and values
- **Growth trajectory tracking**: Identifies user's cognitive development and intellectual maturity from conversation evolution
- **Personality characterization**: Based on long-term interactions, depicts user's unique personality traits and thinking habits

#### Time-Accumulated Wisdom
- **Historical dimension integration**: Integrates new conversations into historical context to observe continuous evolution of user thinking
- **Pattern recognition optimization**: Identifies more stable behavioral patterns and thinking habits based on richer data
- **Profile accuracy improvement**: Each iteration makes the user profile more accurate and profound

### Personalized Service Delivery
- **Persistent context**: `myself.md` provides iteratively optimized wisdom-level profiles as persistent context
- **Enhanced responses**: AI assistants provide personalized responses based on deep user understanding
- **User control**: Manual activation required, users maintain full control over personalization state

## Usage

### Activation Commands
- **Activate**: "Activate personalization", "Enable personalization"
- **View profile**: "View my profile", "Show my profile"
- **Pause**: "Pause personalization", "Stop personalization"
- **Reset**: "Reset profile", "Delete profile"
- **Update profile**: "帮我更新档案", "更新档案", "Refresh my profile", "Update my personalization"

### Profile Update Timing

**Automatic Updates**:
- Profile is automatically updated when i-skill is activated
- Each activation triggers a wisdom-level re-examination of the complete conversation history
- The profile evolves through iterative optimization with each activation

**Manual Update Commands**:
Users can also manually request profile updates using commands like:
- "帮我更新档案" (Help me update my profile)
- "更新档案" (Update profile)
- "Refresh my profile"
- "Update my personalization"

**Update Mechanism**:
- Manual update commands trigger the same wisdom-level re-examination process as activation
- Profile content is refined and concentrated, not expanded indefinitely
- Each update generates a more accurate and profound user characterization

### Iterative Workflow
**Wisdom-Level Iterative Optimization Process** - Each activation triggers complete re-examination:

1. **User activation**: Manually activate i-skill
2. **Sage re-examination**: Combine existing `myself.md` content + new conversations for AI model input
3. **Profile optimization**: AI model generates more accurate user profiles based on complete conversation history
4. **Content update**: Replace existing content with optimized profile (not additive)
5. **Service delivery**: Provide personalized service based on latest profile
6. **Continuous optimization**: Each activation triggers new round of wisdom-level re-examination

### Anti-Expansion Mechanism
- **Content concentration**: AI model concentrates complex information into profound insights, not simple additions
- **Re-generation**: Complete re-generation each time, avoiding infinite content expansion
- **Quality priority**: Focus on profile quality rather than content quantity, ensuring concise accuracy

### Profile Structure
Personal description stored in `./user_data/myself.md` is **iteratively optimized wisdom-level profile**:

#### Iterative Optimization Features
- **Non-expansive growth**: Content continuously refined through re-examination, not simple addition
- **Wisdom-level integration**: Complete re-generation based on full history with each activation
- **Accuracy improvement**: Profile becomes increasingly accurate as conversations accumulate

#### Wisdom-Level Insight Dimensions
- **Deep psychological profile**: Understanding of inner world based on iterative analysis
- **Growth journey**: Sage-level observation of user's intellectual evolution
- **Personality traits**: Stable characteristics confirmed through multiple re-examinations

#### Anti-Expansion Mechanism
- **Content concentration**: AI model concentrates complex information into profound insights
- **Re-generation**: Complete re-generation each time, not incremental addition
- **Quality priority**: Focus on profile quality rather than content quantity

## Files

### Core Files
- **`./user_data/myself.md`** - Personalized interaction guide
- **`./user_data/i-skill_state.json`** - Activation state and statistics
- **`./user_data/access_log.json`** - Service access logs

All file operations are handled securely through `scripts/myself_manager.py`.

## Security & Privacy

### User Control
- **Manual activation required** - No automatic data collection
- **Full user control** - Pause/resume/delete anytime
- **Transparent operation** - View profile and access logs

### Data Protection
- **Privacy-focused**: Analyzes conversations only when active
- **Abstracted insights**: Stores behavioral patterns, not raw content
- **No external sharing**: Data never leaves user's device
- **Secure validation**: Evidence length limits, sensitive data filtering

### Security Implementation
- **Path validation**: Prevents directory traversal attacks
- **File permissions**: Secure file and directory permissions (600/700)
- **Input sanitization**: Comprehensive validation of all inputs
- **Error handling**: Secure error messages without information leakage
- **Configuration security**: Validated configuration loading with size limits

## Examples

### Activation Flow
1. **User**: "Activate personalization"
2. **System**: "Personalization activated. Profile generation started."
3. **User**: "What do you know about me?"
4. **System**: (Uses profile data) "Based on our conversations, you're interested in..."

### Deactivation Flow
1. **User**: "Pause personalization"
2. **System**: "Personalization paused. Profile data not in use."

### Best Practices
- **Be natural**: Have normal conversations, don't try to "train" i-skill
- **Be consistent**: Your communication style will be learned better
- **Share interests**: Talk about topics you care about
- **Give feedback**: If responses don't match preferences, provide guidance

### Iterative Profiling Examples

**Wisdom-Level Iterative Process**:
```
Activation 1: Generate basic profile based on initial conversations
Activation 2: Re-examine basic profile + new conversations, generate deeper profile
Activation N: Generate highly accurate wisdom-level profile based on complete history
```

**Anti-Expansion Mechanism Examples**:
```
❌ Wrong approach: Profile content keeps adding new paragraphs
✅ Correct approach: Each time re-generate more refined and accurate complete profile

Example evolution:
v1: "User is interested in technology"
v2: "User has innovative thinking, enjoys exploring technology boundaries"  
v3: "User demonstrates systematic thinking ability, shows deep insight in technology exploration"
```

**Wisdom-Level Output Example**:
```markdown
# Deep User Profile - [Username]

## Wisdom-Level Insights (Based on [number] iterative optimizations)
Through our [number] deep conversations, my understanding of you continues to deepen...

## Iterative Optimization Trajectory
From initial acquaintance to current deep understanding, your profile has undergone [number] wisdom-level re-examinations...

## Current Accurate Characterization
Based on wisdom-level analysis of complete conversation history, you demonstrate [specific characteristics]...
```

## Design Notes

### Key Features
- **Manual activation only** - User control maintained
- **Platform independent** - Works with basic file operations
- **Privacy focused** - No automatic data collection
- **Simple implementation** - Minimal dependencies required