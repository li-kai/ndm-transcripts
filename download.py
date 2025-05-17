#!/usr/bin/env python3
"""
Batch‐download all episodes of the
'Naturalistic Decision Making' podcast
via its Anchor.fm RSS feed.
This script uses built-in XML parsing to avoid external dependencies like `feedparser`.
"""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import requests


def sanitize_filename(s: str) -> str:
    """Turn a title into a safe filename."""
    # replace any character that isn't alphanumeric, dash, underscore or dot with underscore
    sanitized = re.sub(r'[^A-Za-z0-9\-\._]+', '_', s)
    return sanitized.strip('_')


def parse_rss(feed_url: str):
    """Fetch and parse the RSS feed, returning a list of (title, url)."""
    resp = requests.get(feed_url)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    # Find all <item> elements under any namespace
    items = root.findall('.//item')
    episodes = []
    for item in items:
        title_elem = item.find('title')
        title = title_elem.text if title_elem is not None else 'unknown'
        enclosure = item.find('enclosure')
        if enclosure is None or 'url' not in enclosure.attrib:
            print(f"[WARN] No enclosure for: {title}")
            continue
        episodes.append((title, enclosure.attrib['url']))
    return episodes


def download_episode(url: str, title: str, outdir: Path) -> None:
    """Download the MP3 at `url` to outdir/title.mp3."""
    filename = sanitize_filename(title) + ".mp3"
    filepath = outdir / filename
    if filepath.exists():
        print(f"[SKIP] Already have: {filename}")
        return

    print(f"[DOWN] {filename}")
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def main(feed_url: str, output_folder: str):
    outdir = Path(output_folder)
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        episodes = parse_rss(feed_url)
    except Exception as e:
        print("Error parsing feed:", e, file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(episodes)} episodes in the feed.\n")
    for title, url in episodes:
        download_episode(url, title, outdir)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download podcast episodes from RSS.")
    parser.add_argument("feed_url", nargs='?', default="https://anchor.fm/s/1b3c2204/podcast/rss",
                        help="URL of the podcast RSS feed")
    parser.add_argument("output_folder", nargs='?', default="ndm_episodes",
                        help="Directory to save episodes")
    parser.add_argument("--dry-run", action='store_true', help="Only list episodes without downloading")
    parser.add_argument("--test", action='store_true', help="Run internal tests and exit")
    args = parser.parse_args()

    if args.test:
        import unittest

        class TestPodcastDownloader(unittest.TestCase):
            def test_sanitize(self):
                self.assertEqual(sanitize_filename("Hello/World?"), "Hello_World")
                self.assertEqual(sanitize_filename("Good:Morning"), "Good_Morning")
                self.assertEqual(sanitize_filename("A  B   C"), "A_B_C")

            def test_parse_rss(self):
                sample = """<?xml version='1.0'?>
                <rss><channel>
                <item><title>Ep1</title><enclosure url='http://example.com/1.mp3' type='audio/mpeg'/></item>
                <item><title>Ep2</title><enclosure url='http://example.com/2.mp3' type='audio/mpeg'/></item>
                </channel></rss>"""
                class DummyResp:
                    content = sample.encode('utf-8')
                    def raise_for_status(self): pass
                orig_get = requests.get
                requests.get = lambda url: DummyResp()
                eps = parse_rss('unused')
                requests.get = orig_get
                self.assertEqual(eps, [("Ep1", "http://example.com/1.mp3"), ("Ep2", "http://example.com/2.mp3")])

        unittest.main(argv=[sys.argv[0]], exit=False)
        sys.exit(0)

    if args.dry_run:
        episodes = parse_rss(args.feed_url)
        for title, url in episodes:
            print(f"{title} -> {url}")
    else:
        main(args.feed_url, args.output_folder)
