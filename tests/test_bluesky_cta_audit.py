from pathlib import Path

from scripts.validate_bluesky_ctas import audit_posts


CTA = "*Got thoughts? Hit me up on [Bluesky](https://bsky.app/profile/lemmysmic.bsky.social).*"


def write_post(path: Path, body: str) -> None:
    path.write_text(
        "---\ntitle: Test\ndraft: false\n---\n\n" + body,
        encoding="utf-8",
    )


def test_audit_posts_accepts_cta_between_article_body_and_sources(tmp_path):
    posts = tmp_path / "posts"
    posts.mkdir()
    write_post(posts / "good.md", f"Closing thought.\n\n{CTA}\n\n---\n\n**Sources:**\n- example")

    assert audit_posts(posts) == []


def test_audit_posts_reports_missing_or_misplaced_cta(tmp_path):
    posts = tmp_path / "posts"
    posts.mkdir()
    write_post(posts / "missing.md", "Closing thought.\n\n---\n\n**Sources:**\n- example")
    write_post(posts / "misplaced.md", f"Closing thought.\n\n---\n\n**Sources:**\n- example\n\n{CTA}")

    assert audit_posts(posts) == [
        "misplaced.md: CTA must appear before the Sources block",
        "missing.md: missing canonical Bluesky CTA",
    ]
