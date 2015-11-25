"""
This module helps calculate how many swear words are in the hook of each song,
which aids in calculating the number of swear words in the entire song
depending on how many times the hook gets repeated
"""

import re


def calc_hook_start(lyrics):
    """Figure out where the hook starts"""
    line_count = 1
    for line in lyrics.splitlines():
        # Look for the '[Hook]' tag
        if re.search(r"\[Hook", line):
            return line_count
        line_count += 1


def calc_hook_end(lyrics, hook_start):
    """Figure out where the hook ends"""
    line_count = 1
    for line in lyrics.splitlines():
        # Start scanning the file from the beginning of the hook
        if line_count >= hook_start:
            # Once we've found an empty line we can stop
            if line == "":
                return line_count - 1
        line_count += 1
    return len(lyrics.splitlines())


def get_hook(lyrics):
    """Returns all the lyrics in the Hook as a single string"""
    hook_start = calc_hook_start(lyrics)
    hook_end = calc_hook_end(lyrics, hook_start)
    hook = ""
    # It's important that we split the lyrics across lines
    for line_count, line in enumerate(lyrics.splitlines()):
        if line_count > hook_start and line_count <= hook_end:
            hook += line + "\n"
        line_count += 1
    return hook
