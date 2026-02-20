# TrendToThread - Twitter MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

A **Model Context Protocol (MCP) server** for posting tweets and threads to Twitter/X. Built for AI agents, low-code platforms, and automation workflows.

## Features

- **Post Tweets** - Post single tweets with optional reply threading
- **Post Threads** - Post connected multi-tweet threads in one call
- **Search Tweets** - Search recent tweets with query operators
- **Get Profile** - Retrieve authenticated user's profile info
- **Dual Endpoints** - Supports both `/mcp` (Streamable HTTP) and `/sse` (Server-Sent Events)
- **Remote Access** - Expose locally via ngrok for remote MCP clients
- **Easy Config** - Simple `.env` file for credentials

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/ZaaliMohamed123/Twitter_MCP_Server.git
cd Twitter_MCP_Server

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Twitter API Credentials

#### Step 1: Create a Twitter Developer Account
1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Sign in with your Twitter/X account
3. Apply for a developer account if you don't have one

#### Step 2: Create a Project and App
1. Click **+ Create Project**
2. Enter a project name (e.g., `TrendToThread`)
3. Select a use case (e.g., `Building tools for Twitter users`)
4. Enter a project description (minimum 250 characters):
   ```
   Building an AI-powered content automation tool that researches trending topics, generates engaging Twitter threads, and publishes them automatically. The app helps creators and marketers save time by transforming news into social media content.
   ```
5. Create an **App** within the project

#### Step 3: Configure User Authentication (Important!)
1. In your App, go to **Settings** tab
2. Scroll to **User authentication settings** and click **Set up**
3. Configure as follows:

| Setting | Value |
|---------|-------|
| **App permissions** | **Read and write** (Required for posting tweets!) |
| **Type of App** | Web App, Automated App or Bot |
| **Callback URI** | `https://localhost:8000/callback` |
| **Website URL** | `https://github.com/ZaaliMohamed123/Twitter_MCP_Server` |

4. Click **Save**

> **Warning:** If you skip setting "Read and write" permissions, you'll get a `403 Forbidden` error when trying to post tweets!

#### Step 4: Get Your API Keys
1. Go to **Keys and Tokens** tab
2. Copy these credentials:

| Credential | Location in Developer Portal |
|------------|------------------------------|
| `TWITTER_API_KEY` | API Key and Secret → API Key |
| `TWITTER_API_SECRET` | API Key and Secret → API Secret |
| `TWITTER_ACCESS_TOKEN` | Access Token and Secret → Access Token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Access Token and Secret → Access Token Secret |

> **Note:** If you changed permissions after generating tokens, you must click **Regenerate** to get new Access Token and Secret!

#### Step 5: Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

### 3. Configure Ngrok (Optional - for remote access)

If you want to expose your MCP server to remote platforms:

1. Sign up at [ngrok.com](https://ngrok.com)
2. Get your auth token from [dashboard.ngrok.com](https://dashboard.ngrok.com/get-started/your-authtoken)
3. Either configure globally:
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```
   Or add to your `.env` file:
   ```env
   NGROK_AUTH_TOKEN=your_ngrok_token_here
   ```

### 4. Run the Server

**With ngrok (recommended for remote access):**
```bash
python start_with_ngrok.py
```

**Local only:**
```bash
python twitter_mcp_server.py
```

## MCP Configuration

After starting the server, you'll see configuration details like:

```
===========================================================
  MCP SERVER CONFIGURATION FOR YOUR PLATFORM
===========================================================

  Name:        TrendToThread Twitter MCP
  Description: Post tweets and threads to Twitter/X

  Endpoints:
    SSE: https://abc123.ngrok-free.app/sse
    MCP: https://abc123.ngrok-free.app/mcp

  Headers (JSON):
  {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
  }
```

> **Important:** Make sure to use the full endpoint URL including `/mcp` or `/sse` path. Requests to the root URL `/` will return 404.

Use these values in your MCP client or low-code platform.

## Available Tools

### `post_tweet`

Post a single tweet to Twitter/X.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `text` | string | Yes | Tweet content (max 280 characters) |
| `reply_to_tweet_id` | string | No | Tweet ID to reply to (for threading) |

**Returns:**
```json
{
  "success": true,
  "tweet_id": "1234567890",
  "tweet_url": "https://twitter.com/i/status/1234567890"
}
```

**Example:**
```json
{
  "name": "post_tweet",
  "arguments": {
    "text": "Hello from TrendToThread! 🚀"
  }
}
```

---

### `post_thread`

Post a connected thread of multiple tweets.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tweets` | array[string] | Yes | List of tweet texts (each max 280 chars) |

**Returns:**
```json
{
  "success": true,
  "thread_url": "https://twitter.com/i/status/1234567890",
  "tweet_ids": ["1234567890", "1234567891", "1234567892"],
  "tweets_posted": 3
}
```

**Example:**
```json
{
  "name": "post_thread",
  "arguments": {
    "tweets": [
      "1/ Here's an interesting thread about AI agents 🧵",
      "2/ First, let's talk about MCP (Model Context Protocol)...",
      "3/ MCP allows AI models to interact with external tools...",
      "4/ This enables powerful automation workflows! 🚀"
    ]
  }
}
```

---

### `search_tweets`

Search for recent tweets matching a query.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | Search query (supports Twitter operators) |
| `max_results` | integer | No | Max tweets to return (10-100, default: 10) |

**Returns:**
```json
{
  "success": true,
  "tweets": [
    {
      "id": "1234567890",
      "text": "Tweet content...",
      "author_id": "987654321",
      "created_at": "2024-01-15T12:00:00.000Z"
    }
  ],
  "count": 10
}
```

**Example:**
```json
{
  "name": "search_tweets",
  "arguments": {
    "query": "MCP AI agents",
    "max_results": 20
  }
}
```

---

### `get_user_profile`

Get the authenticated user's Twitter profile.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "user": {
    "id": "1234567890",
    "name": "Your Name",
    "username": "yourusername",
    "description": "Your bio...",
    "public_metrics": {
      "followers_count": 1000,
      "following_count": 500,
      "tweet_count": 2500
    }
  }
}
```

## Testing

### Test with curl

**List available tools:**
```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

**Post a tweet:**
```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "post_tweet",
      "arguments": {"text": "Hello from TrendToThread!"}
    }
  }'
```

### Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python twitter_mcp_server.py
```

## Project Structure

```
Twitter_MCP_Server/
├── twitter_mcp_server.py   # Main MCP server with Twitter tools
├── start_with_ngrok.py     # Launcher with ngrok tunnel
├── config.py               # Configuration loader
├── .env.example            # Example environment variables
├── .env                    # Your credentials (git-ignored)
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
└── README.md               # This file
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TWITTER_API_KEY` | Yes | Twitter API Key (Consumer Key) |
| `TWITTER_API_SECRET` | Yes | Twitter API Secret (Consumer Secret) |
| `TWITTER_ACCESS_TOKEN` | Yes | Twitter Access Token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Yes | Twitter Access Token Secret |
| `NGROK_AUTH_TOKEN` | No | Ngrok auth token for remote access |
| `SERVER_HOST` | No | Server host (default: 0.0.0.0) |
| `SERVER_PORT` | No | Server port (default: 8000) |

## Troubleshooting

### "Missing Twitter API credentials"
- Ensure `.env` file exists in project root
- Check all 4 Twitter credentials are set correctly
- Credentials should not have quotes around values

### Ngrok authentication error
```bash
ngrok config add-authtoken YOUR_TOKEN
```
Or add `NGROK_AUTH_TOKEN` to your `.env` file.

### Twitter API 403 Forbidden - "Client Forbidden"
This error means your app is not attached to a Project:
```
"detail": "When authenticating requests to the Twitter API v2 endpoints, you must use keys and tokens from a Twitter developer App that is attached to a Project."
```
**Fix:** Go to Twitter Developer Portal and ensure your App is inside a Project.

### Twitter API 403 Forbidden - "OAuth1 Permissions"
This error means your app doesn't have write permissions:
```
"detail": "Your client app is not configured with the appropriate oauth1 app permissions for this endpoint."
```
**Fix:**
1. Go to your App → Settings → User authentication settings
2. Set App permissions to **Read and write**
3. Save changes
4. Go to Keys and Tokens → **Regenerate** Access Token and Secret
5. Update your `.env` file with the new tokens

### Twitter API 401 Unauthorized
- Your API keys or tokens are invalid
- Regenerate all keys in the Developer Portal
- Make sure you're copying the full key without extra spaces

### Port already in use
```bash
# Find and kill existing process
lsof -i :8000
kill -9 <PID>
```

## Use Cases

- **AI Content Agents** - Automate social media posting from AI workflows
- **Content Repurposing** - Convert blog posts, videos, or news into tweet threads
- **Social Media Automation** - Schedule and post content via MCP-compatible platforms
- **Research & Monitoring** - Search and analyze Twitter content programmatically

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Author

**Mohamed Zaali** - [@ZaaliMohamed123](https://github.com/ZaaliMohamed123)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - The MCP specification
- [FastMCP](https://github.com/jlowin/fastmcp) - Python MCP framework
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api) - Twitter's official API

---

**Built with ❤️ for the AI agent community**
