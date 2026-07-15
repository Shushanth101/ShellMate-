#!/usr/bin/env python3
"""
Print the current date.
"""

from datetime import date

def main() -> None:
    # Get today's date
    today = date.today()
    # Print it in a readable format
    print(f"Today's date: {today.isoformat()}")   # e.g. 2026-06-25

if __name__ == "__main__":
    main()
