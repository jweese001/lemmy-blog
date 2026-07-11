#!/usr/bin/env python3
"""Validate the canonical Bluesky reader CTA across Lemmy's Mic posts."""

import argparse
from pathlib import Path


BLOG_ROOT = Path(__file__).parent.parent
DEFAULT_POSTS_DIR = BLOG_ROOT / "content" / "posts"
BLUESKY_CTA = "*Got thoughts? Hit me up on [Bluesky](https://bsky.app/profile/lemmysmic.bsky.social).*"
SOURCES_BLOCK_MARKER = "\n---\n\n**Sources:**"


def audit_posts(posts_dir: Path) -> list[str]:
    """Return CTA violations for Markdown posts in deterministic filename order."""
    violations: list[str] = []
    for post_path in sorted(posts_dir.glob("*.md")):
        content = post_path.read_text(encoding="utf-8")
        cta_index = content.find(BLUESKY_CTA)
        if cta_index == -1:
            violations.append(f"{post_path.name}: missing canonical Bluesky CTA")
            continue

        sources_index = content.find(SOURCES_BLOCK_MARKER)
        if sources_index != -1 and cta_index > sources_index:
            violations.append(f"{post_path.name}: CTA must appear before the Sources block")

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Bluesky CTAs in Lemmy's Mic posts")
    parser.add_argument("--posts-dir", type=Path, default=DEFAULT_POSTS_DIR)
    args = parser.parse_args()

    violations = audit_posts(args.posts_dir)
    if violations:
        print("Bluesky CTA audit failed:")
        print("\n".join(f"- {violation}" for violation in violations))
        return 1

    print(f"Bluesky CTA audit passed: {len(list(args.posts_dir.glob('*.md')))} posts checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
