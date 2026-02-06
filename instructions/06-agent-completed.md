# Agent Assistant Implementation

This document describes the AI Agent Assistant feature that was implemented based on the Databricks Agent Framework.

## Overview

The Agent Assistant provides an interactive chat interface that allows users to ask questions about call center analytics, quality scores, and specific calls. The assistant is accessible from anywhere in the application via a floating action button.

## Components

### 1. Backend API (`routers/agent.py`)

- **Endpoint**: `POST /api/agent/chat`
- **Purpose**: Proxies chat requests to the Databricks Agent serving endpoint
- **Authentication**: Uses OAuth client credentials to obtain Databricks access tokens
- **Request Format**: OpenAI-compatible chat format
  ```json
  {
    "messages": [
      {"role": "user", "content": "What is the average quality score?"},
      {"role": "assistant", "content": "The average score is..."},
      {"role": "user", "content": "Show me calls from today"}
    ]
  }
  ```

### 2. Frontend UI (`frontend/index.html`)

#### Floating Action Button
- Fixed position button in bottom-right corner
- Robot emoji (🤖) icon
- Accessible from any page in the application
- Opens/closes the agent sidebar

#### Sidebar Interface
- Slides in from the right side
- 450px width (responsive on mobile to full screen)
- Contains three sections:
  1. **Header**: Title and close button
  2. **Chat Container**: Scrollable message history
  3. **Input Area**: Text input and send button

#### Chat Messages
- iMessage-style design
- User messages: Right-aligned, purple gradient background
- Assistant messages: Left-aligned, white background
- Typing indicator: Animated dots while waiting for response
- Welcome message: Displayed when no conversation exists

### 3. Environment Configuration

Required environment variables:

```bash
# Agent endpoint URL
DATABRICKS_AGENT_ENDPOINT=https://your-workspace.cloud.databricks.com/serving-endpoints/your-agent/invocations

# Authentication (same as Lakebase)
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_CLIENT_ID=your-client-id
DATABRICKS_CLIENT_SECRET=your-client-secret
```

## Implementation Details

### Authentication Flow

1. Backend receives chat request from frontend
2. Checks for existing `DATABRICKS_TOKEN` environment variable
3. If not found, obtains OAuth token using client credentials:
   - Calls `{DATABRICKS_HOST}/oidc/v1/token`
   - Uses `grant_type=client_credentials` with `scope=all-apis`
4. Uses token to authenticate with agent endpoint

### Error Handling

- Network errors: Displayed as assistant message to user
- API errors: HTTP status and detail message shown
- Timeout: 30 second timeout on agent requests
- Graceful degradation: Agent button always visible even if backend unavailable

### Response Parsing

The backend handles multiple response formats from Databricks agents:
- OpenAI format: `data.choices[0].message.content`
- Simple format: `data.message.content` or `data.message`
- Raw string: Direct string response
- Fallback: JSON stringification if format is unknown

## User Experience

1. **Discoverability**: Floating button is always visible in bottom-right
2. **Accessibility**: No navigation required - available from any view
3. **Context Persistence**: Chat history maintained during session
4. **Responsive Design**: Full-screen on mobile, sidebar on desktop
5. **Visual Feedback**: Typing indicator shows assistant is working
6. **Smooth Animations**: Sidebar slides in/out, messages fade in

## Future Enhancements

Potential improvements for the agent assistant:

1. **Context Awareness**: Pass current page/call context to agent
2. **Quick Actions**: Buttons for common queries (e.g., "Show worst calls today")
3. **Chat History Persistence**: Save conversations across sessions
4. **Voice Input**: Speech-to-text for hands-free operation
5. **Suggested Questions**: Display helpful prompts when chat is empty
6. **Multi-turn Memory**: Maintain conversation context server-side
7. **Rich Responses**: Support for charts, tables, and call cards in responses

## Testing

To test the agent assistant:

1. Ensure environment variables are configured
2. Start the application: `python app.py`
3. Open browser to `http://localhost:8000`
4. Click the 🤖 button in bottom-right
5. Type a question and press Enter or click send
6. Verify response appears as assistant message

Example test questions:
- "What is the average quality score across all calls?"
- "Show me the worst performing call from today"
- "Which call center rep has the highest average score?"
- "Summarize the call with ID: [call_id]"

## Security Considerations

- Agent endpoint URL stored in environment, not hardcoded
- OAuth tokens obtained server-side, never exposed to frontend
- Chat requests proxied through backend for authentication
- No sensitive data stored in frontend chat history
- CORS and authentication handled by FastAPI middleware
