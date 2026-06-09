"""Ingest RPI Reddit threads into plain-text documents.

For each thread URL we append `.json` to hit Reddit's read-only JSON view
(no API key needed), then extract the original post plus its top-level
comments and write one .txt file per thread into documents/.

Run:  python ingest_reddit.py
"""

import json
import re
import time
import urllib.request
from pathlib import Path

# The 10 sources from planning.md (Documents table).
THREAD_URLS = [
    "https://www.reddit.com/r/RPI/comments/1ap0cuk/first_year_housing/",
    "https://www.reddit.com/r/RPI/comments/1qevhdr/prospective_student/",
    "https://www.reddit.com/r/RPI/comments/cp98ps/what_clubsgroups_official_and_not_should_i_check/",
    "https://www.reddit.com/r/RPI/comments/1ayi1im/social_life_is_it_really_that_bad/",
    "https://www.reddit.com/r/RPI/comments/1coxkbd/gender_inclusive_housing/",
    "https://www.reddit.com/r/RPI/comments/28ds30/accessing_supercomputer_resources/",
    "https://www.reddit.com/r/RPI/comments/cf25ul/study_spots_onoff_campus/",
    "https://www.reddit.com/r/RPI/comments/1n1wdpg/sites_you_need_to_know_about_as_an_incoming/",
    "https://www.reddit.com/r/RPI/comments/uierkf/incoming_freshman_packing_list/",
    "https://www.reddit.com/r/RPI/comments/v0cwth/dorm_room_necessities/",
]

# Reddit returns 429 for the default urllib User-Agent, so identify ourselves.
USER_AGENT = "rpi-unofficial-guide/0.1 (document ingestion script)"
OUTPUT_DIR = Path("documents")
DELAY_SECONDS = 2  # be polite between requests


def fetch_thread(url):
    """Fetch a thread's JSON listing (post + comments)."""
    json_url = url.rstrip("/") + "/.json"
    request = urllib.request.Request(json_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def extract_text(listing):
    """Pull the post body and top-level comment bodies as plain text.

    Reddit's JSON is a two-element list: [0] is the post, [1] is the
    comment tree. We only read the direct children of the comment tree
    (top-level comments) and ignore nested replies and "load more" stubs.
    """
    post_data = listing[0]["data"]["children"][0]["data"]
    title = post_data.get("title", "").strip()
    selftext = post_data.get("selftext", "").strip()

    parts = [f"Title: {title}"]
    if selftext:
        parts.append(selftext)

    comment_children = listing[1]["data"]["children"]
    for child in comment_children:
        if child.get("kind") != "t1":  # skip "more" stubs, only real comments
            continue
        body = child["data"].get("body", "").strip()
        if body and body not in ("[deleted]", "[removed]"):
            parts.append(body)

    return "\n\n".join(parts)


def slug_from_url(url):
    """Derive a clean filename from the thread's URL slug."""
    match = re.search(r"/comments/[a-z0-9]+/([^/]+)", url)
    name = match.group(1) if match else "thread"
    return f"{name}.txt"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    for url in THREAD_URLS:
        filename = slug_from_url(url)
        try:
            listing = fetch_thread(url)
            text = extract_text(listing)
        except Exception as error:  # noqa: BLE001 - report and keep going
            print(f"FAILED  {filename}: {error}")
            time.sleep(DELAY_SECONDS)
            continue

        (OUTPUT_DIR / filename).write_text(text, encoding="utf-8")
        print(f"saved   {filename}  ({len(text)} chars)")
        time.sleep(DELAY_SECONDS)


if __name__ == "__main__":
    main()
