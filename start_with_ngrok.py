#!/usr/bin/env python3
"""
TrendToThread - Start MCP Server with Ngrok
Runs the Twitter MCP server and exposes it via ngrok for remote access.
"""

import sys
import os

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import TwitterConfig, NgrokConfig, SERVER_PORT, SERVER_HOST


def main():
    print("=" * 55)
    print("  TrendToThread - Twitter MCP Server with Ngrok")
    print("=" * 55)
    print()
    
    # Validate Twitter credentials
    print("[1/4] Checking Twitter credentials...")
    if not TwitterConfig.validate():
        missing = TwitterConfig.get_missing()
        print(f"      ERROR: Missing credentials: {', '.join(missing)}")
        print()
        print("      Please create a .env file with your Twitter API credentials.")
        print("      See .env.example for the required format.")
        sys.exit(1)
    print("      Twitter credentials OK")
    
    # Check ngrok
    print("[2/4] Checking ngrok...")
    try:
        from pyngrok import ngrok, conf
        
        # Use auth token from .env if available
        if NgrokConfig.is_configured():
            conf.get_default().auth_token = NgrokConfig.AUTH_TOKEN
            print("      Using ngrok auth token from .env")
        
        print("      ngrok is available")
    except ImportError:
        print("      ERROR: pyngrok not installed.")
        print("      Run: pip install pyngrok")
        sys.exit(1)
    
    # Start ngrok tunnel
    print(f"[3/4] Starting ngrok tunnel on port {SERVER_PORT}...")
    try:
        tunnel = ngrok.connect(SERVER_PORT, "http")
        public_url = tunnel.public_url  # Extract just the URL string
        print(f"      Tunnel established: {public_url}")
    except Exception as e:
        print(f"      ERROR: Failed to start ngrok: {e}")
        print()
        print("      You may need to authenticate ngrok first:")
        print("        ngrok config add-authtoken YOUR_AUTH_TOKEN")
        print()
        print("      Or add NGROK_AUTH_TOKEN to your .env file")
        print("      Get your token at: https://dashboard.ngrok.com/get-started/your-authtoken")
        sys.exit(1)
    
    # Print configuration for user's platform
    print("[4/4] Server ready!")
    print()
    print("=" * 55)
    print("  MCP SERVER CONFIGURATION")
    print("=" * 55)
    print()
    print(f"  Name:        TrendToThread Twitter MCP")
    print(f"  Description: Post tweets and threads to Twitter/X")
    print()
    print(f"  Endpoints:")
    print(f"    SSE: {public_url}/sse")
    print(f"    MCP: {public_url}/mcp")
    print()
    print("  Headers (JSON):")
    print('  {')
    print('    "Content-Type": "application/json",')
    print('    "Accept": "application/json, text/event-stream"')
    print('  }')
    print()
    print("=" * 55)
    print()
    print("Available tools:")
    print("  - post_tweet(text, reply_to_tweet_id?)")
    print("  - post_thread(tweets[])")
    print("  - search_tweets(query, max_results?)")
    print("  - get_user_profile()")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Start the MCP server
    try:
        from twitter_mcp_server import mcp
        import uvicorn
        uvicorn.run(mcp.streamable_http_app(), host=SERVER_HOST, port=SERVER_PORT)
    except KeyboardInterrupt:
        print("\nShutting down...")
        ngrok.disconnect(tunnel.public_url)
        ngrok.kill()
        print("Server stopped.")


if __name__ == "__main__":
    main()
