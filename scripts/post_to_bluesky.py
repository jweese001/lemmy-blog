#!/usr/bin/env python3
"""
Post to Bluesky (AT Protocol)
Usage: python post_to_bluesky.py "Post text" [--link URL] [--link-title TITLE]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import requests

# Credentials from environment or file
BLUESKY_HANDLE = os.environ.get("BLUESKY_HANDLE", "lemmysmic.bsky.social")
BLUESKY_APP_PASSWORD = os.environ.get("BLUESKY_APP_PASSWORD")

# Fallback to credentials file
CREDS_FILE = Path.home() / ".config" / "bluesky" / "credentials.json"


def load_credentials():
    """Load credentials from env or file."""
    handle = BLUESKY_HANDLE
    password = BLUESKY_APP_PASSWORD
    
    if not password and CREDS_FILE.exists():
        with open(CREDS_FILE) as f:
            creds = json.load(f)
            handle = creds.get("handle", handle)
            password = creds.get("app_password")
    
    if not password:
        raise ValueError(
            "No Bluesky credentials found. Set BLUESKY_APP_PASSWORD env var "
            f"or create {CREDS_FILE}"
        )
    
    return handle, password


def create_session(handle: str, password: str) -> dict:
    """Create authenticated session with Bluesky."""
    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    resp.raise_for_status()
    return resp.json()


def parse_facets(text: str) -> list:
    """Parse URLs and mentions from text to create facets."""
    facets = []
    
    # Find URLs
    url_pattern = r'https?://[^\s<>"\')]*[^\s<>"\').,;:!?]'
    for match in re.finditer(url_pattern, text):
        start = len(text[:match.start()].encode('utf-8'))
        end = len(text[:match.end()].encode('utf-8'))
        facets.append({
            "index": {"byteStart": start, "byteEnd": end},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": match.group()}]
        })
    
    return facets


def create_post(session: dict, text: str, link_url: str = None, link_title: str = None) -> dict:
    """Create a post on Bluesky."""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
    }
    
    # Add facets for any URLs in text
    facets = parse_facets(text)
    if facets:
        record["facets"] = facets
    
    # Add link card embed if provided
    if link_url:
        record["embed"] = {
            "$type": "app.bsky.embed.external",
            "external": {
                "uri": link_url,
                "title": link_title or link_url,
                "description": "",
            }
        }
    
    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {session['accessJwt']}"},
        json={
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": record,
        },
    )
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Post to Bluesky")
    parser.add_argument("text", help="Post text")
    parser.add_argument("--link", help="URL to embed as link card")
    parser.add_argument("--link-title", help="Title for link card")
    args = parser.parse_args()
    
    try:
        handle, password = load_credentials()
        print(f"Authenticating as {handle}...")
        session = create_session(handle, password)
        print(f"Logged in as {session['handle']}")
        
        print(f"Posting: {args.text[:50]}...")
        result = create_post(session, args.text, args.link, args.link_title)
        print(f"Posted! URI: {result['uri']}")
        
        # Return post URL
        post_id = result['uri'].split('/')[-1]
        print(f"View at: https://bsky.app/profile/{handle}/post/{post_id}")
        
    except requests.HTTPError as e:
        print(f"API Error: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
