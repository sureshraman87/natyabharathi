"""Helpers for turning a pasted YouTube/Vimeo link into an embeddable URL."""

import re
from urllib.parse import parse_qs, urlparse

YOUTUBE_HOSTS = {"www.youtube.com", "youtube.com", "m.youtube.com", "youtu.be"}
VIMEO_HOSTS = {"vimeo.com", "www.vimeo.com", "player.vimeo.com"}


def get_embed_url(url: str) -> str:
    """Return a player-embeddable URL for a YouTube or Vimeo link.

    Falls back to the original URL unchanged if the host isn't recognised,
    so self-hosted or other provider links still work in an <iframe>/<video>.
    """
    if not url:
        return ""

    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if host in YOUTUBE_HOSTS:
        video_id = None
        if host == "youtu.be":
            video_id = parsed.path.lstrip("/")
        elif parsed.path.startswith("/embed/"):
            return url
        elif parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/")[-1]
        else:
            query = parse_qs(parsed.query)
            video_id = query.get("v", [None])[0]

        if video_id:
            video_id = re.split(r"[?&]", video_id)[0]
            return f"https://www.youtube-nocookie.com/embed/{video_id}"
        return url

    if host in VIMEO_HOSTS:
        if host == "player.vimeo.com":
            return url
        match = re.search(r"vimeo\.com/(\d+)", url)
        if match:
            return f"https://player.vimeo.com/video/{match.group(1)}"
        return url

    return url
