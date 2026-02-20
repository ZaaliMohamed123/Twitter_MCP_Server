# TrendToTweet MCP Server - Architecture

## Why We Built a Local MCP Server

### The Problem
We tried several existing Twitter MCP solutions:

1. **Smithery Twitter MCP** - OAuth issues, account suspension problems
2. **Composio** - API v3 migration issues, CLI broken
3. **rafaljanicki/x-twitter-mcp-server** - Configuration parsing bugs
4. **vidhupv/x-mcp** - Server initialization failed (404)

**None of the hosted solutions worked reliably.**

### The Solution
We built our own local MCP server that:
- Uses your own Twitter API credentials (full control)
- Runs locally with ngrok for remote access
- No dependency on third-party OAuth flows
- Simple `.env` configuration

---

## Architecture Diagram

```mermaid
flowchart TB
    subgraph USER["👤 User / AI Platform"]
        A[User Request]
        B[AI Agent<br/>TrendToTweet]
    end

    subgraph NGROK["🌐 Ngrok Tunnel"]
        C[Public URL<br/>https://xxx.ngrok-free.app]
    end

    subgraph LOCAL["💻 Local Machine"]
        subgraph SERVER["MCP Server :8000"]
            D[FastMCP Framework]
            E["/mcp endpoint<br/>(Streamable HTTP)"]
            F["/sse endpoint<br/>(Server-Sent Events)"]
        end
        
        subgraph TOOLS["🔧 MCP Tools"]
            G[post_tweet]
            H[post_thread]
            I[search_tweets]
            J[get_user_profile]
        end
        
        subgraph CONFIG["⚙️ Configuration"]
            K[.env file]
            L[config.py]
        end
    end

    subgraph TWITTER["🐦 Twitter API v2"]
        M[POST /2/tweets]
        N[GET /2/tweets/search]
        O[GET /2/users/me]
    end

    A --> B
    B -->|MCP Request| C
    C -->|Tunnel| E
    C -->|Tunnel| F
    E --> D
    F --> D
    D --> TOOLS
    G --> M
    H --> M
    I --> N
    J --> O
    K --> L
    L --> D

    style USER fill:#e1f5fe
    style NGROK fill:#fff3e0
    style LOCAL fill:#e8f5e9
    style TWITTER fill:#e3f2fd
```

---

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Agent as 🤖 AI Agent
    participant Ngrok as 🌐 Ngrok
    participant MCP as 💻 MCP Server
    participant Twitter as 🐦 Twitter API

    User->>Agent: "Tweet about AI trends"
    Agent->>Ngrok: POST /mcp (tools/call)
    Ngrok->>MCP: Forward request
    MCP->>MCP: Parse JSON-RPC request
    MCP->>MCP: Execute post_tweet tool
    MCP->>Twitter: POST /2/tweets (OAuth1)
    Twitter-->>MCP: 201 Created + tweet_id
    MCP-->>Ngrok: JSON-RPC response
    Ngrok-->>Agent: Tool result
    Agent-->>User: "Tweet posted! URL: ..."
```

---

## File Structure

```mermaid
flowchart LR
    subgraph FILES["📁 Project Files"]
        A[twitter_mcp_server.py<br/>Main server + tools]
        B[config.py<br/>Load .env variables]
        C[start_with_ngrok.py<br/>Server + tunnel launcher]
        D[.env<br/>API credentials]
        E[requirements.txt<br/>Dependencies]
    end

    subgraph FLOW["Execution Flow"]
        F[start_with_ngrok.py] --> G[Load config.py]
        G --> H[Validate credentials]
        H --> I[Start ngrok tunnel]
        I --> J[Start MCP server]
        J --> K[Listen on :8000]
    end

    A --> FLOW
    B --> G
    D --> B
```

---

## Tool Architecture

```mermaid
flowchart TB
    subgraph MCP_TOOLS["MCP Tools Layer"]
        A["@mcp.tool()<br/>post_tweet"]
        B["@mcp.tool()<br/>post_thread"]
        C["@mcp.tool()<br/>search_tweets"]
        D["@mcp.tool()<br/>get_user_profile"]
    end

    subgraph AUTH["Authentication Layer"]
        E[OAuth1 Authentication<br/>requests_oauthlib]
    end

    subgraph TWITTER_API["Twitter API v2 Endpoints"]
        F[POST /2/tweets<br/>Create tweet]
        G[GET /2/tweets/search/recent<br/>Search tweets]
        H[GET /2/users/me<br/>User profile]
    end

    A -->|"text, reply_to_id"| E
    B -->|"tweets[]"| A
    C -->|"query, max_results"| E
    D -->|"user.fields"| E

    E -->|OAuth1 signed request| F
    E -->|OAuth1 signed request| G
    E -->|OAuth1 signed request| H

    style MCP_TOOLS fill:#c8e6c9
    style AUTH fill:#fff9c4
    style TWITTER_API fill:#bbdefb
```

---

## Key Design Decisions

| Decision | Reason |
|----------|--------|
| **Local server + ngrok** | Hosted MCP servers had OAuth/config issues |
| **OAuth 1.0a (not Bearer)** | Bearer tokens are read-only, can't post tweets |
| **FastMCP framework** | Simple Python decorators for MCP tools |
| **Streamable HTTP transport** | Stateless, works with most platforms |
| **`.env` configuration** | Secure, git-ignored, easy to change |
| **Dual endpoints (/mcp, /sse)** | Compatibility with different MCP clients |

---

## Security Notes

1. **Never commit `.env`** - Contains API secrets
2. **Ngrok URLs are temporary** - New URL each restart
3. **OAuth1 signs each request** - Credentials never sent in plain text
4. **Access tokens are user-scoped** - Only affects your Twitter account
