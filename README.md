# Reddit MCP Server

This project implements a Model Context Protocol (MCP) server that provides tools for interacting with the Reddit API.

## Features

-   **Get Saved Posts**: Retrieve a list of saved Reddit posts for the authenticated user.
-   **Search Reddit**: Search for posts across all of Reddit or within a specific subreddit.
-   **Get Comments**: Fetch comments from a specific Reddit submission.
-   **Reply to Comment**: Post a reply to an existing Reddit comment.

## Setup

### Prerequisites

-   Python 3.12 or higher.

### Installation

1.  **Clone the repository** (if applicable, otherwise ensure you have the project files):
    ```bash
    git clone https://github.com/netixc/reddit-mcp-server.git
    cd reddit-mcp-server
    ```

2.  **Create a Python virtual environment**:
    ```bash
    uv sync
    ```

## Reddit API Configuration

You need to set up Reddit API credentials for your application. These can be obtained by creating an application on Reddit's developer page (https://www.reddit.com/prefs/apps).


## Running the MCP Server

```json
{
  "mcpServers": {
    "reddit-mcp-server": {
      "command": "mcp",
      "args": [
        "run",
        "/path/to/reddit-mcp-server/server.py"
      ],
      "env": {
        "REDDIT_CLIENT_ID": "YOUR_REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET": "YOUR_REDDIT_CLIENT_SECRET",
        "REDDIT_USERNAME": "YOUR_REDDIT_USERNAME",
        "REDDIT_PASSWORD": "YOUR_REDDIT_PASSWORD"
      }
    }
  }
}
```

**Note:** Replace `YOUR_REDDIT_CLIENT_ID`, `YOUR_REDDIT_CLIENT_SECRET`, `YOUR_REDDIT_USERNAME`, and `YOUR_REDDIT_PASSWORD` with your actual Reddit API credentials.

## Available Tools

Once the server is running and configured in your MCP client, you can call its tools.

### `get_saved_posts(limit: int = 25, subreddit: Optional[str] = None)`

Fetches a list of saved Reddit posts for the authenticated user.

-   `limit` (int, optional): The maximum number of saved posts to retrieve. Defaults to 25.
-   `subreddit` (str, optional): If provided, only posts from this specific subreddit will be returned.


### `search_reddit(query: str, subreddit: Optional[str] = None, sort: str = "relevance", limit: int = 10)`

Searches Reddit for posts matching a given query.

-   `query` (str): The search query.
-   `subreddit` (str, optional): If provided, the search will be limited to this specific subreddit.
-   `sort` (str, optional): The sorting method for the search results (e.g., "relevance", "hot", "new", "top", "comments"). Defaults to "relevance".
-   `limit` (int, optional): The maximum number of search results to retrieve. Defaults to 10.


### `get_comments(submission_id: str, limit: int = 25)`

Fetches comments from a specific Reddit submission.

-   `submission_id` (str): The ID of the Reddit submission (post) to fetch comments from.
-   `limit` (int, optional): The maximum number of comments to retrieve. Defaults to 25.


### `reply_to_comment(comment_id: str, text: str)`

Replies to a specific Reddit comment.

-   `comment_id` (str): The ID of the comment to reply to.
-   `text` (str): The text content of the reply.

