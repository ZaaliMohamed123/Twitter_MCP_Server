"""
TrendToThread - Twitter MCP Server
A Model Context Protocol server for posting tweets and threads to Twitter/X.

This server exposes Twitter functionality as MCP tools that can be used by
AI agents and low-code platforms.
"""

import sys
from mcp.server.fastmcp import FastMCP
import requests
from requests_oauthlib import OAuth1
from typing import Optional

from config import TwitterConfig, SERVER_HOST, SERVER_PORT


# Validate Twitter credentials on startup
if not TwitterConfig.validate():
    missing = TwitterConfig.get_missing()
    print("ERROR: Missing Twitter API credentials!")
    print(f"Please set these environment variables in .env file: {', '.join(missing)}")
    print("\nSee .env.example for the required format.")
    sys.exit(1)


# Initialize FastMCP server with stateless HTTP mode
mcp = FastMCP(
    name="TrendToThread",
    instructions="Twitter MCP Server - Post tweets, threads, and search Twitter",
    host=SERVER_HOST,
    port=SERVER_PORT,
    stateless_http=True  # Enable stateless mode for simpler /mcp endpoint
)


def get_twitter_auth() -> OAuth1:
    """Get OAuth1 authentication for Twitter API."""
    return OAuth1(
        TwitterConfig.API_KEY,
        TwitterConfig.API_SECRET,
        TwitterConfig.ACCESS_TOKEN,
        TwitterConfig.ACCESS_TOKEN_SECRET
    )


@mcp.tool()
def post_tweet(text: str, reply_to_tweet_id: Optional[str] = None) -> dict:
    """
    Post a single tweet to Twitter/X.
    
    Args:
        text: The tweet content (max 280 characters)
        reply_to_tweet_id: Optional tweet ID to reply to (for creating threads)
    
    Returns:
        Dictionary with success status, tweet_id, and tweet_url or error message
    """
    url = "https://api.twitter.com/2/tweets"
    auth = get_twitter_auth()
    
    payload: dict = {"text": text}
    
    if reply_to_tweet_id:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}
    
    try:
        response = requests.post(
            url,
            auth=auth,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            tweet_id = data["data"]["id"]
            return {
                "success": True,
                "tweet_id": tweet_id,
                "tweet_url": f"https://twitter.com/i/status/{tweet_id}"
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def post_thread(tweets: list[str]) -> dict:
    """
    Post a Twitter thread (multiple connected tweets).
    
    Args:
        tweets: List of tweet texts to post as a connected thread (each max 280 chars)
    
    Returns:
        Dictionary with success status, thread_url, tweet_ids list, and tweets_posted count
    """
    if not tweets:
        return {
            "success": False,
            "error": "No tweets provided"
        }
    
    tweet_ids = []
    previous_tweet_id = None
    
    for i, tweet_text in enumerate(tweets):
        result = post_tweet(tweet_text, reply_to_tweet_id=previous_tweet_id)
        
        if result["success"]:
            tweet_ids.append(result["tweet_id"])
            previous_tweet_id = result["tweet_id"]
        else:
            return {
                "success": False,
                "tweets_posted": i,
                "tweet_ids": tweet_ids,
                "error": f"Failed at tweet {i + 1}: {result['error']}"
            }
    
    return {
        "success": True,
        "thread_url": f"https://twitter.com/i/status/{tweet_ids[0]}",
        "tweet_ids": tweet_ids,
        "tweets_posted": len(tweet_ids)
    }


@mcp.tool()
def search_tweets(query: str, max_results: int = 10) -> dict:
    """
    Search for recent tweets matching a query.
    
    Args:
        query: Search query (supports Twitter search operators)
        max_results: Maximum number of tweets to return (10-100, default 10)
    
    Returns:
        Dictionary with success status, tweets list, and count
    """
    url = "https://api.twitter.com/2/tweets/search/recent"
    auth = get_twitter_auth()
    
    params = {
        "query": query,
        "max_results": min(max(max_results, 10), 100),
        "tweet.fields": "created_at,author_id,public_metrics"
    }
    
    try:
        response = requests.get(url, auth=auth, params=params)
        
        if response.status_code == 200:
            data = response.json()
            tweets = data.get("data", [])
            return {
                "success": True,
                "tweets": tweets,
                "count": len(tweets)
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_user_profile() -> dict:
    """
    Get the authenticated user's Twitter profile.
    
    Returns:
        Dictionary with success status and user profile data (id, name, username)
    """
    url = "https://api.twitter.com/2/users/me"
    auth = get_twitter_auth()
    
    params = {
        "user.fields": "id,name,username,description,profile_image_url,public_metrics"
    }
    
    try:
        response = requests.get(url, auth=auth, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "user": data.get("data", {})
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Start the MCP server."""
    import uvicorn
    
    print("=" * 50)
    print("TrendToThread - Twitter MCP Server")
    print("=" * 50)
    print()
    print(f"Server running on http://{SERVER_HOST}:{SERVER_PORT}")
    print()
    print("Endpoints:")
    print(f"  SSE:  http://{SERVER_HOST}:{SERVER_PORT}/sse")
    print(f"  MCP:  http://{SERVER_HOST}:{SERVER_PORT}/mcp")
    print()
    print("Use ngrok to expose publicly: ngrok http 8000")
    print()
    
    # Use streamable HTTP app which provides /mcp endpoint
    # SSE is also available at /sse by default
    uvicorn.run(mcp.streamable_http_app(), host=SERVER_HOST, port=SERVER_PORT)


if __name__ == "__main__":
    main()
