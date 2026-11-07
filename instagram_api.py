"""
Instagram publishing via the Graph API (system-user token, graph.facebook.com).

Two-step flow per Meta's docs:
  1. POST /{ig-user-id}/media          -> creation_id
  2. POST /{ig-user-id}/media_publish  -> published media id

Needs IG_USER_ID + IG_ACCESS_TOKEN (see SETUP.md).

Safety behaviour (deliberate):
  - DRY_RUN=1 never calls Meta's publish endpoints at all.
  - On GitHub Actions, missing secrets are an ERROR, not a silent dry run,
    so a misconfigured pipeline can never look like a green run.
  - The token is verified before every post, and every Graph API failure
    is raised with Meta's own error code + message (never the token).
"""

import os
import time
import requests

GRAPH_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"


class InstagramError(RuntimeError):
    pass


def is_configured() -> bool:
    return bool(os.environ.get("IG_USER_ID") and os.environ.get("IG_ACCESS_TOKEN"))


def dry_run_requested() -> bool:
    return os.environ.get("DRY_RUN", "").strip().lower() in ("1", "true", "yes")


def is_live() -> bool:
    """True only when a real post would actually be made."""
    return is_configured() and not dry_run_requested()


def _request(method: str, url: str, what: str, **kwargs) -> dict:
    """requests wrapper: raises InstagramError with Meta's message, never leaks the token."""
    try:
        resp = requests.request(method, url, timeout=30, **kwargs)
    except requests.RequestException as e:
        raise InstagramError(f"{what} failed: network error ({type(e).__name__})") from None
    if resp.ok:
        return resp.json()
    try:
        err = resp.json().get("error", {})
    except ValueError:
        err = {}
    msg = err.get("message") or resp.text[:300]
    raise InstagramError(
        f"{what} failed: HTTP {resp.status_code}, Graph error code {err.get('code')}: {msg}"
    )


def verify_token() -> str:
    """Confirms the token can see the Instagram account. Returns the username."""
    data = _request(
        "get",
        f"{GRAPH_BASE}/{os.environ['IG_USER_ID']}",
        "Token check",
        params={"fields": "id,username", "access_token": os.environ["IG_ACCESS_TOKEN"]},
    )
    return data.get("username", "?")


def wait_for_image(image_url: str, tries: int = 12, delay: int = 5) -> None:
    """Meta fetches the image itself, so make sure the public URL is serving it first."""
    for _ in range(tries):
        try:
            r = requests.get(image_url, timeout=15, stream=True)
            ok = r.status_code == 200 and r.headers.get("content-type", "").startswith("image/")
            r.close()
            if ok:
                return
        except requests.RequestException:
            pass
        time.sleep(delay)
    raise InstagramError(f"Image is not publicly reachable yet: {image_url}")


def publish_image(image_url: str, caption: str) -> dict:
    ig_user_id = os.environ["IG_USER_ID"]
    token = os.environ["IG_ACCESS_TOKEN"]

    created = _request(
        "post",
        f"{GRAPH_BASE}/{ig_user_id}/media",
        "Create media container",
        data={"image_url": image_url, "caption": caption, "access_token": token},
    )
    creation_id = created["id"]

    status = None
    for _ in range(12):
        s = _request(
            "get",
            f"{GRAPH_BASE}/{creation_id}",
            "Container status check",
            params={"fields": "status_code", "access_token": token},
        )
        status = s.get("status_code")
        if status == "FINISHED":
            break
        if status in ("ERROR", "EXPIRED"):
            raise InstagramError(f"Media container ended in status {status}")
        time.sleep(3)
    else:
        raise InstagramError(f"Media container never finished processing (last status: {status})")

    return _request(
        "post",
        f"{GRAPH_BASE}/{ig_user_id}/media_publish",
        "Publish",
        data={"creation_id": creation_id, "access_token": token},
    )


def _print_dry_run(image_url: str, caption: str, slot: str, why: str) -> None:
    print(f"[{slot}] DRY RUN ({why}) -- would publish:")
    print(f"  image_url: {image_url}")
    print(f"  caption:\n{caption}")


def publish_or_dry_run(image_url: str, caption: str, slot: str) -> None:
    if dry_run_requested():
        _print_dry_run(image_url, caption, slot, "DRY_RUN is set")
        return
    if not is_configured():
        if os.environ.get("GITHUB_ACTIONS") == "true":
            raise InstagramError(
                "IG_USER_ID / IG_ACCESS_TOKEN are not set as repository secrets. "
                "Refusing to treat this as a successful run."
            )
        _print_dry_run(image_url, caption, slot, "IG_USER_ID/IG_ACCESS_TOKEN not set")
        return

    username = verify_token()
    wait_for_image(image_url)
    result = publish_image(image_url, caption)
    print(f"[{slot}] Published to @{username}: {result}")
