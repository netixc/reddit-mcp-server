from dotenv import load_dotenv
load_dotenv()
import os
import praw
from praw.models import Submission, Comment
from praw.exceptions import PRAWException
from typing import Optional
from redditwarp.ASYNC import Client
from redditwarp.models.submission_ASYNC import LinkPost, TextPost, GalleryPost
import logging

# IMPORTANT: Set these environment variables before running the server:
# REDDIT_CLIENT_ID
# REDDIT_CLIENT_SECRET
# REDDIT_USERNAME
# REDDIT_PASSWORD

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Reddit-MCP-Server") # Keep existing MCP initialization

mcp = FastMCP("Reddit-MCP-Server")

reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    username=os.environ.get("REDDIT_USERNAME"),
    password=os.environ.get("REDDIT_PASSWORD"),
    user_agent=os.environ.get("REDDIT_USER_AGENT", "reddit-mcp-server")
)

client = Client()
logging.getLogger().setLevel(logging.WARNING)
print(f"User Agent: {os.environ.get('REDDIT_USER_AGENT')}")
print(f"Redditwarp Client Initialized. Log Level: {logging.getLevelName(logging.getLogger().level)}")

@mcp.tool()
def get_saved_posts(limit: int = 25, subreddit: Optional[str] = None) -> list:
    """
    Fetches a list of saved Reddit posts for the authenticated user.

    Purpose of the function:
    This tool retrieves saved posts from the user's Reddit account.
    It can be optionally filtered by number of posts and/or a specific subreddit.

    Expected parameters:
    - limit (int, optional): The maximum number of saved posts to retrieve. Defaults to 25.
    - subreddit (str, optional): If provided, only posts from this specific subreddit will be returned.

    Return values:
    A list of dictionaries, where each dictionary represents a saved post
    and contains the following keys:
    - 'title': The title of the post.
    - 'url': The URL of the post.
    - 'author': The username of the post's author.
    - 'subreddit': The subreddit the post belongs to.
    - 'created_utc': The UTC timestamp of when the post was created.

    Usage examples:
    # To get the 50 most recent saved posts:
    # mcp call reddit-mcp-server get_saved_posts --limit 50

    # To get saved posts from the "programming" subreddit:
    # mcp call reddit-mcp-server get_saved_posts --subreddit "programming"

    # To get 10 saved posts from the "reactjs" subreddit:
    # mcp call reddit-mcp-server get_saved_posts --limit 10 --subreddit "reactjs"
    """
    saved_posts = []
    try:
        print(f"Attempting to fetch {limit} saved posts. Subreddit filter: {subreddit or 'None'}")
        
        # Get the authenticated user object
        me = reddit.user.me()
        if not me:
            print("Authentication failed: 'me' object is None. Cannot fetch saved posts.")
            return []

        # PRAW's saved() method returns a generator, so we iterate through it directly.
        for item in me.saved(limit=limit):
            # Check if the item is a submission (a post) and not a comment
            if isinstance(item, Submission):
                print(f"Processing post: {item.title}")
                # Filter by subreddit if specified
                if subreddit and item.subreddit.display_name.lower() != subreddit.lower():
                    continue

                saved_posts.append({
                    "title": item.title,
                    "url": item.url,
                    "author": item.author.name if item.author else "[deleted]",
                    "subreddit": item.subreddit.display_name,
                    "created_utc": item.created_utc,
                })
    except PRAWException as e:
        print(f"An error occurred while fetching saved posts: {e}")
        # Optionally, you might want to return an empty list or raise a more specific exception
        return []
    if not saved_posts:
        print("No saved posts found or fetched.")
    return saved_posts

@mcp.tool()
def search_reddit(query: str, subreddit: Optional[str] = None, sort: str = "relevance", limit: int = 10) -> list:
    """
    Searches Reddit for posts matching a given query.

    Purpose of the function:
    This tool allows searching for posts across all of Reddit or within a specific subreddit.

    Expected parameters:
    - query (str): The search query.
    - subreddit (str, optional): If provided, the search will be limited to this specific subreddit.
    - sort (str, optional): The sorting method for the search results (e.g., "relevance", "hot", "new", "top", "comments"). Defaults to "relevance".
    - limit (int, optional): The maximum number of search results to retrieve. Defaults to 10.

    Return values:
    A list of dictionaries, where each dictionary represents a found post
    and contains the following keys:
    - 'title': The title of the post.
    - 'url': The URL of the post.
    - 'author': The username of the post's author.
    - 'subreddit': The subreddit the post belongs to.
    - 'created_utc': The UTC timestamp of when the post was created.

    Usage examples:
    # To search for "AI agents" across all of Reddit:
    # mcp call reddit-mcp-server search_reddit --query "AI agents"

    # To search for "Python" within the "programming" subreddit, sorted by new:
    # mcp call reddit-mcp-server search_reddit --query "Python" --subreddit "programming" --sort "new"

    # To get 10 top posts about "machine learning" from the past week:
    # mcp call reddit-mcp-server search_reddit --query "machine learning" --limit 10 --sort "top" --time_filter "week"
    """
    search_results = []
    try:
        print(f"Searching Reddit for query: '{query}' in subreddit: {subreddit or 'All Reddit'}, sorted by: {sort}, limit: {limit}")
        
        # Determine the search scope
        if subreddit:
            # Search within a specific subreddit
            target_subreddit = reddit.subreddit(subreddit)
            posts = target_subreddit.search(query, sort=sort, limit=limit)
        else:
            # Search across all of Reddit
            posts = reddit.subreddits.search(query, sort=sort, limit=limit) # Corrected for global search

        for post in posts:
            search_results.append({
                "title": post.title,
                "url": post.url,
                "author": post.author.name if post.author else "[deleted]",
                "subreddit": post.subreddit.display_name,
                "created_utc": post.created_utc,
            })
    except PRAWException as e:
        print(f"An error occurred while searching Reddit: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during search: {e}")
        return []

    if not search_results:
        print("No search results found.")
    return search_results

@mcp.tool()
def get_comments(submission_id: str, limit: int = 25) -> list:
    """
    Fetches comments from a specific Reddit submission.

    Purpose of the function:
    This tool retrieves comments associated with a given Reddit post ID.

    Expected parameters:
    - submission_id (str): The ID of the Reddit submission (post) to fetch comments from.
    - limit (int, optional): The maximum number of comments to retrieve. Defaults to 25.

    Return values:
    A list of dictionaries, where each dictionary represents a comment
    and contains the following keys:
    - 'id': The ID of the comment.
    - 'author': The username of the comment's author.
    - 'body': The text body of the comment.
    - 'score': The comment's score (upvotes minus downvotes).
    - 'created_utc': The UTC timestamp of when the comment was created.

    Usage examples:
    # To get the first 50 comments from a submission with ID 'example_id':
    # mcp call reddit-mcp-server get_comments --submission_id "example_id" --limit 50
    """
    comments_list = []
    try:
        submission = reddit.submission(id=submission_id)
        print(f"Fetching {limit} comments for submission ID: {submission_id}")
        
        # Limit the comments to the specified number
        submission.comments.replace_more(limit=None) # To get all comments, not just top level
        # Filter out MoreComments objects and apply limit
        for c in submission.comments.list():
            if isinstance(c, Comment): # Ensure it's a valid Comment object
                comments_list.append({
                    "id": c.id,
                    "author": c.author.name if c.author else "[deleted]",
                    "body": c.body,
                    "score": c.score,
                    "created_utc": c.created_utc,
                })
            # Apply limit after processing a comment
            if len(comments_list) >= limit:
                break
    except PRAWException as e:
        print(f"An error occurred while fetching comments: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

    if not comments_list:
        print(f"No comments found for submission ID: {submission_id} or API limit reached.")
    return comments_list

@mcp.tool()
def reply_to_comment(comment_id: str, text: str) -> str:
    """
    Replies to a specific Reddit comment.

    Purpose of the function:
    Allows the authenticated user to post a reply to an existing comment.

    Expected parameters:
    - comment_id (str): The ID of the comment to reply to.
    - text (str): The text content of the reply.

    Return values:
    A string indicating the success or failure of the reply operation.

    Usage examples:
    # To reply to a comment with ID 'abcdef' with a specific message:
    # mcp call reddit-mcp-server reply_to_comment --comment_id "abcdef" --text "This is my reply."
    """
    try:
        comment = reddit.comment(id=comment_id)
        print(f"Attempting to reply to comment ID: {comment_id}")
        reply_object = comment.reply(body=text)
        if reply_object: # Check if the reply operation was successful
            print(f"Successfully replied to comment ID: {comment_id}. New comment ID: {reply_object.id}")
            return f"Successfully replied to comment. New comment ID: {reply_object.id}"
        else:
            print(f"Failed to reply to comment ID: {comment_id}. Reply object was None.")
            return f"Failed to reply to comment: The reply operation returned no object."
    except PRAWException as e:
        print(f"An error occurred while replying to comment: {e}")
        return f"Failed to reply to comment: {e}"
    except Exception as e:
        print(f"An unexpected error occurred while replying to comment: {e}")
        return f"Failed to reply to comment due to an unexpected error: {e}"
# Helper to determine post type (adapted for synchronous PRAW)
def _praw_get_post_type(submission: Submission) -> str:
    """Helper method to determine post type based on PRAW Submission attributes."""
    if submission.is_self: # Text post
        return 'text'
    elif submission.is_video: # Video post
        return 'video'
    elif submission.url and ('redd.it/gallery' in submission.url or '/gallery/' in submission.url):
        return 'gallery'
    elif submission.url: # Link post (includes images/other media not directly handled as gallery/video)
        return 'link'
    return 'unknown'

# Helper to extract post content (adapted for synchronous PRAW)
def _praw_get_content(submission: Submission) -> Optional[str]:
    """Helper method to extract post content based on type."""
    if submission.is_self:
        return submission.selftext # For text posts
    elif submission.url and not submission.is_self:
        return submission.url # For link/video/image posts
    return None

# Helper to format comment tree synchronously (PRAW)
def _praw_format_comment_tree(comment: Comment, indent_level: int, max_depth: int) -> str:
    """Recursively formats a comment and its replies."""
    if indent_level >= max_depth:
        return ""

    indent_str = "    " * indent_level
    author = comment.author.name if comment.author else '[deleted]'
    body = comment.body.replace('\n', '\n' + indent_str + '    ') # Indent multi-line comments

    formatted_comment = f"{indent_str}- Author: {author}, Score: {comment.score}\n{indent_str}  {body}\n"

    if hasattr(comment, 'replies') and comment.replies:
        comment.replies.replace_more(limit=None) # Ensure all replies are loaded
        for reply in comment.replies:
            if isinstance(reply, Comment): # Make sure it's a Comment object, not MoreComments
                formatted_comment += _praw_format_comment_tree(reply, indent_level + 1, max_depth)
    return formatted_comment

# NEW redditwarp-based functions
def _redditwarp_format_comment_tree(comment_node, depth: int = 0) -> str:
    """Helper method to recursively format comment tree with proper indentation for redditwarp"""
    comment = comment_node.value
    indent = "-- " * depth
    content = (
        f"{indent}* Author: {comment.author_display_name or '[deleted]'}\n"
        f"{indent}  Score: {comment.score}\n"
        f"{indent}  {comment.body}\n"
    )

    for child in comment_node.children:
        content += "\n" + _redditwarp_format_comment_tree(child, depth + 1)

    return content

def _redditwarp_get_post_type(submission) -> str:
    """Helper method to determine post type for redditwarp"""
    if isinstance(submission, LinkPost):
        return 'link'
    elif isinstance(submission, TextPost):
        return 'text'
    elif isinstance(submission, GalleryPost):
        return 'gallery'
    return 'unknown'

def _redditwarp_get_content(submission) -> Optional[str]:
    """Helper method to extract post content based on type for redditwarp"""
    if isinstance(submission, LinkPost):
        return submission.permalink
    elif isinstance(submission, TextPost):
        return submission.body
    elif isinstance(submission, GalleryPost):
        return str(submission.gallery_link)
    return None


@mcp.tool()
async def fetch_reddit_post_content(post_id: str, comment_limit: int = 20, comment_depth: int = 3) -> str:
    """
    Fetch detailed content of a specific post
    
    Args:
        post_id: Reddit post ID
        comment_limit: Number of top level comments to fetch
        comment_depth: Maximum depth of comment tree to traverse

    Returns:
        Human readable string containing post content and comments tree
    """
    try:
        submission = await client.p.submission.fetch(post_id)
        
        content = (
            f"Title: {submission.title}\n"
            f"Score: {submission.score}\n"
            f"Author: {submission.author_display_name or '[deleted]'}\n"
            f"Type: {_redditwarp_get_post_type(submission)}\n" # Using redditwarp specific helper
            f"Content: {_redditwarp_get_content(submission)}\n" # Using redditwarp specific helper
        )

        comments = await client.p.comment_tree.fetch(post_id, sort='top', limit=comment_limit, depth=comment_depth)
        if comments.children:
            content += "\nComments:\n"
            for comment in comments.children:
                content += "\n" + _redditwarp_format_comment_tree(comment) # Using redditwarp specific helper
        else:
            content += "\nNo comments found."

        return content

    except Exception as e:
        return f"An error occurred: {str(e)}"