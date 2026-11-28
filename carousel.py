"""
Publishes the daily 4-slide carousel that the 6:45 Claude scheduled task drops into
carousel/<YYYY-MM-DD>/.

Folder contract (written by the scheduled task, one commit per day):
  carousel/2026-11-29/
    1.jpg 2.jpg 3.jpg 4.jpg     JPEG only (Meta rejects PNG), 1080x1350, slide order = file order
    caption.txt                 the exact Instagram caption
    post.json                   {"date": "2026-11-29", "slides": ["1.jpg", ...]}

Run as:  python3 carousel.py <YYYY-MM-DD>      (DRY_RUN=1 prints instead of posting)

Safety behaviour, same spirit as main.py:
  - only publishes a folder whose date is TODAY in SAST (a late or replayed push never
    posts yesterday's conditions)
  - refuses if 2-10 JPEG slides aren't all present, or the caption is empty / too long /
    trips copy_gen.is_safe_text
  - skips if the same caption is already on the account (instagram_api.already_posted)
  - writes carousel/<date>/published.json after a successful post, and skips if it exists
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

from copy_gen import is_safe_text
from instagram_api import (GRAPH_BASE, InstagramError, _request, already_posted,
                           dry_run_requested, is_configured, verify_token, wait_for_image)

SAST = timezone(timedelta(hours=2))
REPO = os.environ.get("GITHUB_REPOSITORY", "LukeBresler/beach-please-social")
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main"
MAX_CAPTION = 2200  # Instagram's caption limit


class Skip(Exception):
    pass


def _wait_finished(container_id: str, token: str, what: str) -> None:
    status = None
    for _ in range(20):
        s = _request("get", f"{GRAPH_BASE}/{container_id}", f"{what} status check",
                     params={"fields": "status_code", "access_token": token})
        status = s.get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise InstagramError(f"{what} ended in status {status}")
        time.sleep(3)
    raise InstagramError(f"{what} never finished processing (last status: {status})")


def publish_carousel(image_urls: list, caption: str) -> dict:
    ig_user_id = os.environ["IG_USER_ID"]
    token = os.environ["IG_ACCESS_TOKEN"]

    children = []
    for i, url in enumerate(image_urls, 1):
        c = _request("post", f"{GRAPH_BASE}/{ig_user_id}/media", f"Create slide {i} container",
                     data={"image_url": url, "is_carousel_item": "true", "access_token": token})
        _wait_finished(c["id"], token, f"Slide {i} container")
        children.append(c["id"])

    parent = _request("post", f"{GRAPH_BASE}/{ig_user_id}/media", "Create carousel container",
                      data={"media_type": "CAROUSEL", "children": ",".join(children),
                            "caption": caption, "access_token": token})
    _wait_finished(parent["id"], token, "Carousel container")

    return _request("post", f"{GRAPH_BASE}/{ig_user_id}/media_publish", "Publish carousel",
                    data={"creation_id": parent["id"], "access_token": token})


def load(date: str) -> tuple:
    folder = f"carousel/{date}"
    today = datetime.now(SAST).strftime("%Y-%m-%d")
    if date != today:
        raise Skip(f"folder is for {date} but today (SAST) is {today}; not posting stale conditions")
    if os.path.exists(f"{folder}/published.json"):
        raise Skip(f"{folder} was already published")

    with open(f"{folder}/post.json") as f:
        meta = json.load(f)
    slides = meta.get("slides") or []
    if not 2 <= len(slides) <= 10:
        raise Skip(f"need 2-10 slides, got {len(slides)}")
    for s in slides:
        if not s.lower().endswith((".jpg", ".jpeg")):
            raise Skip(f"{s} is not a JPEG (Meta only accepts JPEG)")
        if not os.path.exists(f"{folder}/{s}"):
            raise Skip(f"{folder}/{s} is missing")

    with open(f"{folder}/caption.txt") as f:
        caption = f.read().strip()
    if not caption:
        raise Skip("caption.txt is empty")
    if len(caption) > MAX_CAPTION:
        raise Skip(f"caption is {len(caption)} characters (limit {MAX_CAPTION})")
    if not is_safe_text(caption):
        raise Skip("caption tripped the tone-guide safety filter")

    return [f"{RAW_BASE}/{folder}/{s}" for s in slides], caption


def main(date: str) -> None:
    try:
        urls, caption = load(date)
    except Skip as why:
        print(f"::warning::[carousel {date}] SKIPPED, nothing posted: {why}")
        return

    if dry_run_requested():
        print(f"[carousel {date}] DRY RUN -- would publish {len(urls)} slides:")
        print("\n".join(f"  {u}" for u in urls))
        print(f"  caption:\n{caption}")
        return
    if not is_configured():
        raise InstagramError("IG_USER_ID / IG_ACCESS_TOKEN are not set. Refusing to treat this as a success.")

    username = verify_token()
    if already_posted(caption):
        print(f"::warning::[carousel {date}] SKIPPED: this exact caption is already on @{username}")
        return
    for u in urls:
        wait_for_image(u)
    result = publish_carousel(urls, caption)
    with open(f"carousel/{date}/published.json", "w") as f:
        json.dump({"media_id": result.get("id"), "published_at": datetime.now(SAST).isoformat()}, f)
    print(f"[carousel {date}] Published to @{username}: {result}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 carousel.py <YYYY-MM-DD>")
        sys.exit(1)
    main(sys.argv[1])
