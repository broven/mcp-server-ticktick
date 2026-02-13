#!/usr/bin/env python3
"""
TickTick OAuth authentication command-line utility.

This script guides users through the process of authenticating with TickTick
and obtaining the necessary access tokens for the TickTick MCP server.
"""

import sys
import os
import logging
import argparse
from typing import Optional
from pathlib import Path
from .src.auth import TickTickAuth

def main(manual: Optional[bool] = None) -> int:
    """Run the authentication flow.

    Args:
        manual: If provided, override the --manual flag. Used when called from cli.py.
    """
    if manual is None:
        parser = argparse.ArgumentParser(description='TickTick MCP Server Authentication')
        parser.add_argument('--manual', action='store_true',
                            help='Manual mode for VPS/remote: print auth URL and prompt for callback URL')
        args = parser.parse_args()
        manual = args.manual

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    print("""
╔════════════════════════════════════════════════╗
║       TickTick MCP Server Authentication       ║
╚════════════════════════════════════════════════╝

This utility will help you authenticate with TickTick
and obtain the necessary access tokens for the TickTick MCP server.

Before you begin, you will need:
1. A TickTick account (https://ticktick.com)
2. A registered TickTick API application (https://developer.ticktick.com)
3. Your Client ID and Client Secret from the TickTick Developer Center
    """)
    
    # Check for existing credentials: env vars → ~/.ticktick/config.json
    config = TickTickAuth.load_config()
    existing_client_id = os.getenv("TICKTICK_CLIENT_ID") or config.get("client_id")
    existing_client_secret = os.getenv("TICKTICK_CLIENT_SECRET") or config.get("client_secret")
    has_credentials = bool(existing_client_id and existing_client_secret)

    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    if has_credentials:
        print(f"Existing TickTick credentials found (Client ID: {existing_client_id[:8]}...).")
        use_existing = input("Do you want to use these credentials? (y/n): ").lower().strip()

        if use_existing == 'y':
            client_id = existing_client_id
            client_secret = existing_client_secret
            print("Using existing credentials.")
        else:
            client_id = get_user_input("Enter your TickTick Client ID: ")
            client_secret = get_user_input("Enter your TickTick Client Secret: ")
    else:
        print("No existing TickTick credentials found.")
        client_id = get_user_input("Enter your TickTick Client ID: ")
        client_secret = get_user_input("Enter your TickTick Client Secret: ")

    # Save credentials to ~/.ticktick/config.json
    TickTickAuth.save_config({
        "client_id": client_id,
        "client_secret": client_secret,
    })
    
    # Initialize the auth manager
    auth = TickTickAuth(
        client_id=client_id,
        client_secret=client_secret
    )
    
    manual = args.manual
    if manual:
        print("\nStarting the OAuth authentication flow in manual mode...")
        print("You will need to open the authorization URL in a browser manually.\n")
    else:
        print("\nStarting the OAuth authentication flow...")
        print("A browser window will open for you to authorize the application.")
        print("After authorization, you will be redirected back to this application.\n")

    # Start the OAuth flow
    result = auth.start_auth_flow(manual=manual)
    
    print("\n" + result)
    
    if "successful" in result.lower():
        print("""
Authentication complete! You can now use the TickTick MCP server.

To start the server with Claude for Desktop:
1. Make sure you have configured Claude for Desktop
2. Restart Claude for Desktop
3. You should now see the TickTick tools available in Claude

Enjoy using TickTick through Claude!
        """)
        return 0
    else:
        print("""
Authentication failed. Please try again or check the error message above.

Common issues:
- Incorrect Client ID or Client Secret
- Network connectivity problems
- Permission issues with the ~/.ticktick/ directory

For further assistance, please refer to the documentation or raise an issue
on the GitHub repository.
        """)
        return 1

def get_user_input(prompt: str) -> str:
    """Get user input with validation."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")

if __name__ == "__main__":
    sys.exit(main())