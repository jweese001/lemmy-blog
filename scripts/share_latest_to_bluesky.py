#!/home/lemmy/lemmy-blog/.venv/bin/python
"""Share the latest Lemmy's Mic post to Bluesky one day after publication."""

from __future__ import annotations

import argparse
import io
import json
import mimetypes
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from PIL import Image

BLOG_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = BLOG_ROOT / "content" / "posts"
BLUESKY_API_URL = "https://bsky.social"
BLUESKY_HANDLE_ENV = "BLUESKY_HANDLE"
BLUESKY_PASSWORD_ENV = "BLUESKY_APP_PASSWORD"
DEFAULT_CREDENTIALS_PATH = Path.home() / ".config" / "bluesky" / "credentials.json"
DEFAULT_LEDGER_PATH = Path.home() / ".config" / "bluesky" / "shared_posts.json"
MAX_POST_LENGTH = 300
LINK_RE = re.compile(r"https?://\S+")


@dataclass(frozen=True)
class PostMetadata:
    path: Path
    title: str
    slug: str
    date: datetime
    image_path: Path
    image_web_path: str
    description: str
    url: str


@dataclass(frozen=True)
class ShareResult:
    status: str
    message: str
    slug: str | None = None
    url: str | None = None
    bluesky_uri: str | None = None


@dataclass(frozen=True)
class BlueskyCredentials:
    identifier: str
    password: str


def build_post_url(slug: str) -> str:
    return f"https://jweese001.github.io/lemmy-blog/posts/{slug}/"


def parse_simple_frontmatter(frontmatter: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in frontmatter.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def parse_post_file(path: Path, *, blog_root: Path = BLOG_ROOT) -> PostMetadata:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        raise ValueError(f"Post {path} is missing frontmatter")

    try:
        _, frontmatter, _ = content.split("---", 2)
    except ValueError as exc:
        raise ValueError(f"Post {path} has malformed frontmatter") from exc

    values = parse_simple_frontmatter(frontmatter)
    title = values.get("title")
    date_str = values.get("date")
    image_web_path = values.get("image")
    description = values.get("description")

    if not title:
        raise ValueError(f"Post {path} is missing title frontmatter")
    if not date_str:
        raise ValueError(f"Post {path} is missing date frontmatter")
    if not image_web_path:
        raise ValueError(f"Post {path} is missing image frontmatter")
    if not description:
        raise ValueError(f"Post {path} is missing description frontmatter")

    slug = path.stem
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
    image_path = blog_root / "static" / image_web_path.lstrip("/")

    return PostMetadata(
        path=path,
        title=title,
        slug=slug,
        date=datetime.fromisoformat(date_str),
        image_path=image_path,
        image_web_path=image_web_path,
        description=description,
        url=build_post_url(slug),
    )


def resolve_latest_post(posts_dir: Path = POSTS_DIR, *, blog_root: Path = BLOG_ROOT) -> PostMetadata:
    candidates = [parse_post_file(path, blog_root=blog_root) for path in posts_dir.glob("*.md")]
    if not candidates:
        raise FileNotFoundError(f"No posts found in {posts_dir}")
    return max(candidates, key=lambda post: post.date)


def is_post_one_day_old(post_date: datetime, *, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    normalized_now = now.astimezone(post_date.tzinfo)
    return (normalized_now.date() - post_date.date()).days == 1


def compose_share_text(title: str, description: str, url: str, *, max_length: int = MAX_POST_LENGTH) -> str:
    prefix = f"New on Lemmy's Mic: {title}"
    suffix = url
    separator = "\n\n"
    base = f"{prefix}{separator}{description}{separator}{suffix}"
    if len(base) <= max_length:
        return base

    available = max_length - len(prefix) - len(suffix) - (len(separator) * 2)
    if available <= 1:
        return f"{prefix}{separator}{suffix}"[:max_length]

    trimmed_description = description[: max(available - 1, 0)].rstrip()
    if len(trimmed_description) < len(description):
        trimmed_description = trimmed_description.rstrip(" .,;:!?-") + "…"
    return f"{prefix}{separator}{trimmed_description}{separator}{suffix}"


def load_shared_slugs(ledger_path: Path = DEFAULT_LEDGER_PATH) -> set[str]:
    if not ledger_path.exists():
        return set()
    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Ledger at {ledger_path} must contain a JSON list")
    return {str(item) for item in data}


def save_shared_slug(ledger_path: Path, slug: str) -> None:
    existing = load_shared_slugs(ledger_path)
    existing.add(slug)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(json.dumps(sorted(existing), indent=2) + "\n", encoding="utf-8")


def load_credentials(credentials_path: Path = DEFAULT_CREDENTIALS_PATH) -> BlueskyCredentials:
    env_identifier = os.getenv(BLUESKY_HANDLE_ENV)
    env_password = os.getenv(BLUESKY_PASSWORD_ENV)
    if env_identifier and env_password:
        return BlueskyCredentials(identifier=env_identifier, password=env_password)

    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Bluesky credentials not found. Set {BLUESKY_HANDLE_ENV}/{BLUESKY_PASSWORD_ENV} or create {credentials_path}"
        )

    data = json.loads(credentials_path.read_text(encoding="utf-8"))
    identifier = data.get("identifier") or data.get("handle") or data.get("username")
    password = data.get("app_password") or data.get("appPassword") or data.get("password")
    if not identifier or not password:
        raise ValueError(f"Bluesky credentials file {credentials_path} is missing identifier/password fields")
    return BlueskyCredentials(identifier=str(identifier), password=str(password))


def parse_link_facets(text: str) -> list[dict[str, Any]]:
    facets: list[dict[str, Any]] = []
    text_bytes = text.encode("utf-8")
    for match in LINK_RE.finditer(text):
        url = match.group(0)
        byte_start = len(text[: match.start()].encode("utf-8"))
        byte_end = byte_start + len(url.encode("utf-8"))
        facets.append(
            {
                "index": {"byteStart": byte_start, "byteEnd": byte_end},
                "features": [
                    {"$type": "app.bsky.richtext.facet#link", "uri": url},
                ],
            }
        )
    return facets


def create_session(credentials: BlueskyCredentials) -> dict[str, Any]:
    response = requests.post(
        f"{BLUESKY_API_URL}/xrpc/com.atproto.server.createSession",
        json={"identifier": credentials.identifier, "password": credentials.password},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def sanitize_image_bytes(image_path: Path) -> tuple[bytes, str, int, int]:
    with Image.open(image_path) as image:
        width, height = image.size
        format_name = (image.format or image_path.suffix.lstrip(".") or "png").upper()
        mime_type = Image.MIME.get(format_name, mimetypes.guess_type(image_path.name)[0] or "image/png")
        save_format = "PNG" if format_name == "PNG" else "JPEG"
        if save_format == "JPEG" and image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")
        output = io.BytesIO()
        image.save(output, format=save_format, optimize=True)
        return output.getvalue(), mime_type, width, height


def upload_image_blob(access_token: str, image_path: Path) -> tuple[dict[str, Any], int, int]:
    image_bytes, mime_type, width, height = sanitize_image_bytes(image_path)
    if len(image_bytes) > 1_000_000:
        raise ValueError(f"Image {image_path} exceeds Bluesky 1,000,000 byte limit after sanitization")

    response = requests.post(
        f"{BLUESKY_API_URL}/xrpc/com.atproto.repo.uploadBlob",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": mime_type,
        },
        data=image_bytes,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["blob"], width, height


def create_bluesky_post(access_token: str, did: str, text: str, post: PostMetadata) -> dict[str, Any]:
    blob, width, height = upload_image_blob(access_token, post.image_path)
    record: dict[str, Any] = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "langs": ["en-US"],
        "facets": parse_link_facets(text),
        "embed": {
            "$type": "app.bsky.embed.images",
            "images": [
                {
                    "alt": post.description,
                    "image": blob,
                    "aspectRatio": {"width": width, "height": height},
                }
            ],
        },
    }

    response = requests.post(
        f"{BLUESKY_API_URL}/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": record,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def share_latest_post(
    *,
    blog_root: Path = BLOG_ROOT,
    posts_dir: Path = POSTS_DIR,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    credentials_path: Path = DEFAULT_CREDENTIALS_PATH,
    now: datetime | None = None,
    dry_run: bool = False,
) -> ShareResult:
    latest = resolve_latest_post(posts_dir, blog_root=blog_root)
    if not latest.image_path.exists():
        raise FileNotFoundError(f"Hero image not found for latest post: {latest.image_path}")

    if not is_post_one_day_old(latest.date, now=now):
        return ShareResult(
            status="skipped",
            message=f"Latest post {latest.slug} is not exactly one day old; skipping share.",
            slug=latest.slug,
            url=latest.url,
        )

    shared = load_shared_slugs(ledger_path)
    if latest.slug in shared:
        return ShareResult(
            status="skipped",
            message=f"Latest post {latest.slug} was already shared to Bluesky.",
            slug=latest.slug,
            url=latest.url,
        )

    text = compose_share_text(latest.title, latest.description, latest.url)
    if dry_run:
        return ShareResult(
            status="dry_run",
            message=text,
            slug=latest.slug,
            url=latest.url,
        )

    credentials = load_credentials(credentials_path)
    session = create_session(credentials)
    response = create_bluesky_post(session["accessJwt"], session["did"], text, latest)
    save_shared_slug(ledger_path, latest.slug)
    return ShareResult(
        status="posted",
        message="Posted latest Lemmy's Mic article to Bluesky.",
        slug=latest.slug,
        url=latest.url,
        bluesky_uri=response.get("uri"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Share the latest Lemmy's Mic post to Bluesky")
    parser.add_argument("--blog-root", default=str(BLOG_ROOT), help="Override blog root path")
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER_PATH), help="Path to shared-post ledger JSON")
    parser.add_argument("--credentials", default=str(DEFAULT_CREDENTIALS_PATH), help="Path to Bluesky credentials JSON")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be posted without publishing")
    args = parser.parse_args()

    result = share_latest_post(
        blog_root=Path(args.blog_root),
        posts_dir=Path(args.blog_root) / "content" / "posts",
        ledger_path=Path(args.ledger),
        credentials_path=Path(args.credentials),
        dry_run=args.dry_run,
    )

    payload = {
        "status": result.status,
        "message": result.message,
        "slug": result.slug,
        "url": result.url,
        "bluesky_uri": result.bluesky_uri,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
