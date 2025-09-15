# assignment3.py
# Week 3 – Text Processing Assignment

import argparse
import csv
import io
import re
from urllib import request, error
from collections import Counter, defaultdict
from datetime import datetime

# Regex to detect image requests (.jpg/.jpeg/.gif/.png)
IMG_RE = re.compile(r".*\.(jpg|jpeg|gif|png)$", re.IGNORECASE)


def download_text(url: str) -> str:
    """Download text from a given URL and return as UTF-8 string."""
    with request.urlopen(url) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_rows(csv_text: str):

    f = io.StringIO(csv_text)
    reader = csv.reader(f)
    for row in reader:
        if not row:
            continue
        yield row


def detect_browser(user_agent: str) -> str:

    ua = user_agent or ""
    if "Firefox" in ua:
        return "Firefox"
    if "Chrome" in ua and "Chromium" not in ua:
        return "Chrome"
    if "MSIE" in ua or "Trident" in ua:
        return "Internet Explorer"
    if "Safari" in ua and "Chrome" not in ua:
        return "Safari"
    return "Other"


def run(url: str, show_hours: bool) -> None:

    try:
        csv_text = download_text(url)
    except error.URLError as e:
        print(f"Error downloading file: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

    total_hits = 0
    image_hits = 0
    browser_counts = Counter()
    hour_counts = defaultdict(int)

    for row in parse_rows(csv_text):
        path = row[0].strip() if len(row) > 0 else ""
        dt_str = row[1].strip() if len(row) > 1 else ""
        ua_str = row[2].strip() if len(row) > 2 else ""

        total_hits += 1

        if IMG_RE.match(path):
            image_hits += 1

        browser = detect_browser(ua_str)
        browser_counts[browser] += 1

        if show_hours:
            try:
                ts = datetime.strptime(dt_str, "%m/%d/%Y %H:%M:%S")
                hour_counts[ts.hour] += 1
            except Exception:
                pass

    if total_hits == 0:
        print("No requests found.")
        return
    pct = image_hits * 100.0 / total_hits
    print(f"Image requests account for {pct:.1f}% of all requests")

    focus = ["Firefox", "Chrome", "Internet Explorer", "Safari"]
    sub_counts = {k: browser_counts.get(k, 0) for k in focus}
    if sum(sub_counts.values()) == 0:
        most_pop = browser_counts.most_common(1)[0][0] if browser_counts else "Unknown"
    else:
        most_pop = max(sub_counts, key=sub_counts.get)
    print(f"The most popular browser today is: {most_pop}")

    if show_hours:
        for h in range(24):
            hour_counts[h] += 0
        items = sorted(hour_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        for h, cnt in items:
            print(f"Hour {h:02d} has {cnt} hits")


def main():
    parser = argparse.ArgumentParser(description="IS211 Assignment 3 - Text Processing")
    parser.add_argument("--url", help="URL to the datafile (http/https or file://)", type=str, required=True)
    parser.add_argument("--show-hours", action="store_true", help="Show hourly hit counts (extra credit)")
    args = parser.parse_args()
    run(args.url, args.show_hours)


if __name__ == "__main__":
    main()
