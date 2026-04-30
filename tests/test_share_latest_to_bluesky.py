from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from scripts.share_latest_to_bluesky import (
    build_post_url,
    compose_share_text,
    is_post_one_day_old,
    load_shared_slugs,
    parse_post_file,
    resolve_latest_post,
    save_shared_slug,
)


def _write_post(path: Path, *, title: str, date: str, image: str, description: str) -> Path:
    path.write_text(
        "\n".join(
            [
                "---",
                f'title: "{title}"',
                f"date: {date}",
                "draft: false",
                "tags: [\"tech\"]",
                f'image: "{image}"',
                f'description: "{description}"',
                "---",
                "",
                "Body.",
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_parse_post_file_extracts_metadata(tmp_path: Path):
    posts_dir = tmp_path / "content" / "posts"
    posts_dir.mkdir(parents=True)
    post_path = _write_post(
        posts_dir / "2026-04-10-cargo-revolution.md",
        title="Cargo E-Bikes Are Quietly Winning the Commute War",
        date="2026-04-10T18:00:00-05:00",
        image="/images/hero-cargo-revolution.jpg",
        description="Why cargo e-bikes are becoming the practical answer to urban mobility.",
    )

    post = parse_post_file(post_path, blog_root=tmp_path)

    assert post.slug == "cargo-revolution"
    assert post.url == "https://jweese001.github.io/lemmy-blog/posts/cargo-revolution/"
    assert post.image_path == tmp_path / "static" / "images" / "hero-cargo-revolution.jpg"
    assert post.description.startswith("Why cargo e-bikes")


def test_resolve_latest_post_uses_newest_post_date(tmp_path: Path):
    posts_dir = tmp_path / "content" / "posts"
    posts_dir.mkdir(parents=True)
    _write_post(
        posts_dir / "2026-04-07-earlier.md",
        title="Earlier",
        date="2026-04-07T18:00:00-05:00",
        image="/images/hero-earlier.jpg",
        description="Earlier post.",
    )
    latest_path = _write_post(
        posts_dir / "2026-04-10-later.md",
        title="Later",
        date="2026-04-10T18:00:00-05:00",
        image="/images/hero-later.jpg",
        description="Later post.",
    )

    latest = resolve_latest_post(posts_dir, blog_root=tmp_path)

    assert latest.path == latest_path
    assert latest.slug == "later"


def test_is_post_one_day_old_uses_calendar_days():
    post_date = datetime.fromisoformat("2026-04-10T18:00:00-05:00")
    now = datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc)

    assert is_post_one_day_old(post_date, now=now) is True
    assert is_post_one_day_old(post_date, now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc)) is False


def test_compose_share_text_includes_title_description_and_url():
    text = compose_share_text(
        title="Cargo E-Bikes Are Quietly Winning the Commute War",
        description="Why cargo e-bikes are becoming the practical answer to urban mobility—and why you should pay attention.",
        url="https://jweese001.github.io/lemmy-blog/posts/cargo-revolution/",
    )

    assert text.startswith("New on Lemmy's Mic: Cargo E-Bikes Are Quietly Winning the Commute War")
    assert "https://jweese001.github.io/lemmy-blog/posts/cargo-revolution/" in text
    assert len(text) <= 300


def test_shared_slug_ledger_round_trip(tmp_path: Path):
    ledger = tmp_path / "shared_posts.json"

    assert load_shared_slugs(ledger) == set()

    save_shared_slug(ledger, "cargo-revolution")
    save_shared_slug(ledger, "cargo-revolution")
    save_shared_slug(ledger, "later")

    assert load_shared_slugs(ledger) == {"cargo-revolution", "later"}


def test_build_post_url():
    assert build_post_url("cargo-revolution") == "https://jweese001.github.io/lemmy-blog/posts/cargo-revolution/"


def test_parse_post_file_requires_image_frontmatter(tmp_path: Path):
    posts_dir = tmp_path / "content" / "posts"
    posts_dir.mkdir(parents=True)
    post_path = posts_dir / "2026-04-10-no-image.md"
    post_path.write_text(
        "\n".join(
            [
                "---",
                'title: "No Image"',
                "date: 2026-04-10T18:00:00-05:00",
                'description: "desc"',
                "---",
            ]
        ),
        encoding="utf-8",
    )

    try:
        parse_post_file(post_path, blog_root=tmp_path)
    except ValueError as exc:
        assert "image" in str(exc)
    else:
        raise AssertionError("Expected parse_post_file to reject posts without an image")


def test_parse_post_file_resolves_existing_image_file(tmp_path: Path):
    posts_dir = tmp_path / "content" / "posts"
    images_dir = tmp_path / "static" / "images"
    posts_dir.mkdir(parents=True)
    images_dir.mkdir(parents=True)
    image_path = images_dir / "hero-cargo-revolution.jpg"
    Image.new("RGB", (64, 32), color=(10, 20, 30)).save(image_path)
    post_path = _write_post(
        posts_dir / "2026-04-10-cargo-revolution.md",
        title="Cargo",
        date="2026-04-10T18:00:00-05:00",
        image="/images/hero-cargo-revolution.jpg",
        description="desc",
    )

    post = parse_post_file(post_path, blog_root=tmp_path)

    assert post.image_path == image_path
