# Conversation Manager Component Documentation

## Overview
The `conversation_manager.py` file manages the conversation history and context between the user and the AI agent. It stores conversation turns, manages context limits, and provides conversation context to the LLM.

## Key Classes and Functions

### ConversationManager Class
- **Purpose**: Manages conversation history and context for the AI agent
- **Key Responsibilities**:
  - Stores conversation turns (user questions and AI responses)
  - Manages conversation history limits to prevent memory issues
  - Provides conversation context to the LLM for coherence
  - Serializes and deserializes conversation history
  - Integrates with history storage mechanisms

### Context Management
- Maintains conversation history within configurable limits
- Provides recent conversation context to the LLM
- Handles conversation serialization for persistence
- Integrates with history_manager for long-term storage

## Key Methods
- `__init__(self, history_manager=None, max_turns=50)` - Initializes with history manager and limits
- `add_message(self, role, content)` - Adds a message to the conversation
- `get_conversation_context(self)` - Gets formatted conversation history for LLM
- `clear_conversation(self)` - Clears the current conversation history
- `to_dict(self)` - Serializes conversation to dictionary
- `from_dict(cls, data)` - Deserializes conversation from dictionary

## Dependencies
- `history_manager` - For long-term conversation storage
- `config` - For conversation history limits
- `logger` - For logging conversation events

## Usage Context
This component is used by the main agent to maintain conversation continuity, ensuring the AI has access to recent conversation history for contextual responses. It works with the history manager to persist conversations across sessions.