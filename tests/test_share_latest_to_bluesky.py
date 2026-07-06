from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

import scripts.share_latest_to_bluesky as share_latest_to_bluesky_module
from scripts.share_latest_to_bluesky import (
    BlueskyCredentials,
    build_post_url,
    compose_share_text,
    is_post_at_least_one_day_old,
    load_credentials,
    load_shared_slugs,
    parse_post_file,
    resolve_latest_post,
    resolve_target_post,
    save_shared_slug,
    share_latest_post,
    ShareResult,
    PostMetadata,
)


def _write_post(
    path: Path,
    *,
    title: str,
    date: str,
    image: str,
    description: str,
    draft: bool = False,
) -> Path:
    path.write_text(
        "\n".join(
            [
                "---",
                f'title: "{title}"',
                f"date: {date}",
                f"draft: {str(draft).lower()}",
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
    assert post.url == "https://jweese001.github.io/lemmy-blog/posts/2026-04-10-cargo-revolution/"
    assert post.image_path == tmp_path / "static" / "images" / "hero-cargo-revolution.jpg"
    assert post.description.startswith("Why cargo e-bikes")
    assert post.is_draft is False


def test_parse_post_file_extracts_draft_state(tmp_path: Path):
    posts_dir = tmp_path / "content" / "posts"
    posts_dir.mkdir(parents=True)
    post_path = _write_post(
        posts_dir / "2026-04-11-draft-post.md",
        title="Draft Post",
        date="2026-04-11T18:00:00-05:00",
        image="/images/hero-draft-post.jpg",
        description="Draft description.",
        draft=True,
    )

    post = parse_post_file(post_path, blog_root=tmp_path)

    assert post.is_draft is True


def test_resolve_latest_post_uses_newest_published_post_date(tmp_path: Path):
    posts_dir = tmp_path / "content" / "posts"
    posts_dir.mkdir(parents=True)
    published_path = _write_post(
        posts_dir / "2026-04-07-earlier.md",
        title="Earlier",
        date="2026-04-07T18:00:00-05:00",
        image="/images/hero-earlier.jpg",
        description="Earlier post.",
    )
    _write_post(
        posts_dir / "2026-04-10-later-draft.md",
        title="Later Draft",
        date="2026-04-10T18:00:00-05:00",
        image="/images/hero-later.jpg",
        description="Later post.",
        draft=True,
    )

    latest = resolve_latest_post(posts_dir, blog_root=tmp_path)

    assert latest.path == published_path
    assert latest.slug == "earlier"


def test_is_post_at_least_one_day_old_uses_calendar_days():
    post_date = datetime.fromisoformat("2026-04-10T18:00:00-05:00")
    now = datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc)

    assert is_post_at_least_one_day_old(post_date, now=now) is True
    assert is_post_at_least_one_day_old(post_date, now=datetime(2026, 4, 12, 12, 0, tzinfo=timezone.utc)) is True
    assert is_post_at_least_one_day_old(post_date, now=datetime(2026, 4, 10, 22, 0, tzinfo=timezone.utc)) is False


def test_compose_share_text_includes_title_description_and_url():
    text = compose_share_text(
        title="Cargo E-Bikes Are Quietly Winning the Commute War",
        description="Why cargo e-bikes are becoming the practical answer to urban mobility—and why you should pay attention.",
        url="https://jweese001.github.io/lemmy-blog/posts/cargo-revolution/",
    )

    assert text.startswith("New on Lemmy's Mic: Cargo E-Bikes Are Quietly Winning the Commute War")
    assert "Continue reading: https://jweese001.github.io/lemmy-blog/posts/cargo-revolution/" in text
    assert len(text) <= 300


def test_shared_slug_ledger_round_trip(tmp_path: Path):
    ledger = tmp_path / "shared_posts.json"

    assert load_shared_slugs(ledger) == set()

    save_shared_slug(ledger, "cargo-revolution")
    save_shared_slug(ledger, "cargo-revolution")
    save_shared_slug(ledger, "later")

    assert load_shared_slugs(ledger) == {"cargo-revolution", "later"}


def test_build_post_url():
    assert build_post_url("2026-04-10-cargo-revolution") == "https://jweese001.github.io/lemmy-blog/posts/2026-04-10-cargo-revolution/"


def test_load_credentials_reads_repo_env_when_explicit_sources_are_missing(tmp_path: Path, monkeypatch):
    blog_root = tmp_path / "blog"
    blog_root.mkdir()
    (blog_root / ".env").write_text(
        "BLUESKY_HANDLE=lemmysmic.bsky.social\nBLUESKY_APP_PASSWORD=app-password\n",
        encoding="utf-8",
    )
    credentials_path = tmp_path / "missing-credentials.json"
    monkeypatch.delenv("BLUESKY_HANDLE", raising=False)
    monkeypatch.delenv("BLUESKY_APP_PASSWORD", raising=False)

    credentials = load_credentials(credentials_path, blog_root=blog_root)

    assert credentials == BlueskyCredentials(
        identifier="lemmysmic.bsky.social",
        password="app-password",
    )


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


def test_resolve_target_post_by_slug(tmp_path: Path):
    posts_dir = tmp_path / "content" / "posts"
    posts_dir.mkdir(parents=True)
    target_path = _write_post(
        posts_dir / "2026-02-08-when-bluegrass-met-the-mosh-pit.md",
        title="When Bluegrass Met the Mosh Pit",
        date="2026-02-08T18:00:00-05:00",
        image="/images/hero-when-bluegrass-met-the-mosh-pit.jpg",
        description="desc",
    )

    post = resolve_target_post(posts_dir, slug="when-bluegrass-met-the-mosh-pit", blog_root=tmp_path)

    assert post.path == target_path
    assert post.slug == "when-bluegrass-met-the-mosh-pit"


def test_parse_post_file_keeps_dated_filename_in_public_url(tmp_path: Path):
    posts_dir = tmp_path / "content" / "posts"
    posts_dir.mkdir(parents=True)
    post_path = _write_post(
        posts_dir / "2026-06-29-steam-next-fest-demo-culture.md",
        title="June's Steam Next Fest Proved Demo Culture Still Rules",
        date="2026-06-29T18:00:00-04:00",
        image="/images/hero-steam-next-fest-demo-culture.jpg",
        description="Steam Next Fest June 2026 felt less like a storefront sale and more like a messy, glorious laboratory for indie game discovery.",
    )

    post = parse_post_file(post_path, blog_root=tmp_path)

    assert post.slug == "steam-next-fest-demo-culture"
    assert post.url == "https://jweese001.github.io/lemmy-blog/posts/2026-06-29-steam-next-fest-demo-culture/"


def test_share_latest_post_skips_when_latest_post_is_draft(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(share_latest_to_bluesky_module, "is_public_post_live", lambda url, timeout=20: True)
    posts_dir = tmp_path / "content" / "posts"
    images_dir = tmp_path / "static" / "images"
    posts_dir.mkdir(parents=True)
    images_dir.mkdir(parents=True)
    Image.new("RGB", (64, 32), color=(10, 20, 30)).save(images_dir / "hero-published.jpg")
    Image.new("RGB", (64, 32), color=(20, 30, 40)).save(images_dir / "hero-draft.jpg")
    _write_post(
        posts_dir / "2026-04-10-published.md",
        title="Published",
        date="2026-04-10T18:00:00-05:00",
        image="/images/hero-published.jpg",
        description="Published description.",
    )
    _write_post(
        posts_dir / "2026-04-11-draft.md",
        title="Draft",
        date="2026-04-11T18:00:00-05:00",
        image="/images/hero-draft.jpg",
        description="Draft description.",
        draft=True,
    )

    result = share_latest_post(
        blog_root=tmp_path,
        posts_dir=posts_dir,
        ledger_path=tmp_path / "shared_posts.json",
        credentials_path=tmp_path / "credentials.json",
        now=datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc),
        dry_run=True,
    )

    assert result.status == "dry_run"
    assert result.slug == "published"
    assert "Published description." in result.message
    assert "https://jweese001.github.io/lemmy-blog/posts/2026-04-10-published/" in result.message


def test_share_latest_post_ignores_newer_post_that_is_not_live_on_site(tmp_path: Path, monkeypatch):
    posts_dir = tmp_path / "content" / "posts"
    images_dir = tmp_path / "static" / "images"
    posts_dir.mkdir(parents=True)
    images_dir.mkdir(parents=True)
    Image.new("RGB", (64, 32), color=(10, 20, 30)).save(images_dir / "hero-live.jpg")
    Image.new("RGB", (64, 32), color=(20, 30, 40)).save(images_dir / "hero-not-live.jpg")
    _write_post(
        posts_dir / "2026-04-10-live.md",
        title="Live",
        date="2026-04-10T18:00:00-05:00",
        image="/images/hero-live.jpg",
        description="Live description.",
    )
    _write_post(
        posts_dir / "2026-04-11-not-live.md",
        title="Not Live",
        date="2026-04-11T18:00:00-05:00",
        image="/images/hero-not-live.jpg",
        description="Not-live description.",
    )
    monkeypatch.setattr(
        share_latest_to_bluesky_module,
        "is_public_post_live",
        lambda url, timeout=20: url.endswith("/2026-04-10-live/"),
    )

    result = share_latest_post(
        blog_root=tmp_path,
        posts_dir=posts_dir,
        ledger_path=tmp_path / "shared_posts.json",
        credentials_path=tmp_path / "credentials.json",
        now=datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc),
        dry_run=True,
    )

    assert result.status == "dry_run"
    assert result.slug == "live"
    assert "Live description." in result.message
    assert "https://jweese001.github.io/lemmy-blog/posts/2026-04-10-live/" in result.message


def test_share_latest_post_allows_latest_published_post_when_it_is_older_than_one_day(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(share_latest_to_bluesky_module, "is_public_post_live", lambda url, timeout=20: True)
    posts_dir = tmp_path / "content" / "posts"
    images_dir = tmp_path / "static" / "images"
    posts_dir.mkdir(parents=True)
    images_dir.mkdir(parents=True)
    Image.new("RGB", (64, 32), color=(10, 20, 30)).save(images_dir / "hero-published.jpg")
    _write_post(
        posts_dir / "2026-04-10-published.md",
        title="Published",
        date="2026-04-10T18:00:00-05:00",
        image="/images/hero-published.jpg",
        description="Published description.",
    )

    result = share_latest_post(
        blog_root=tmp_path,
        posts_dir=posts_dir,
        ledger_path=tmp_path / "shared_posts.json",
        credentials_path=tmp_path / "credentials.json",
        now=datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc),
        dry_run=True,
    )

    assert result.status == "dry_run"
    assert result.slug == "published"
    assert "Published description." in result.message
    assert result.url == "https://jweese001.github.io/lemmy-blog/posts/2026-04-10-published/"


def test_share_latest_post_skips_when_latest_published_post_was_already_shared(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(share_latest_to_bluesky_module, "is_public_post_live", lambda url, timeout=20: True)
    posts_dir = tmp_path / "content" / "posts"
    images_dir = tmp_path / "static" / "images"
    posts_dir.mkdir(parents=True)
    images_dir.mkdir(parents=True)
    Image.new("RGB", (64, 32), color=(10, 20, 30)).save(images_dir / "hero-earlier.jpg")
    Image.new("RGB", (64, 32), color=(20, 30, 40)).save(images_dir / "hero-latest.jpg")
    _write_post(
        posts_dir / "2026-04-08-earlier.md",
        title="Earlier",
        date="2026-04-08T18:00:00-05:00",
        image="/images/hero-earlier.jpg",
        description="Earlier description.",
    )
    _write_post(
        posts_dir / "2026-04-10-latest.md",
        title="Latest",
        date="2026-04-10T18:00:00-05:00",
        image="/images/hero-latest.jpg",
        description="Latest description.",
    )
    save_shared_slug(tmp_path / "shared_posts.json", "latest")

    result = share_latest_post(
        blog_root=tmp_path,
        posts_dir=posts_dir,
        ledger_path=tmp_path / "shared_posts.json",
        credentials_path=tmp_path / "credentials.json",
        now=datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc),
        dry_run=True,
    )

    assert result.status == "skipped"
    assert result.slug == "latest"
    assert "already shared" in result.message.lower()
    assert result.url == "https://jweese001.github.io/lemmy-blog/posts/2026-04-10-latest/"


def test_share_latest_post_does_not_backfill_older_unshared_post_when_latest_was_already_shared(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(share_latest_to_bluesky_module, "is_public_post_live", lambda url, timeout=20: True)
    posts_dir = tmp_path / "content" / "posts"
    images_dir = tmp_path / "static" / "images"
    posts_dir.mkdir(parents=True)
    images_dir.mkdir(parents=True)
    Image.new("RGB", (64, 32), color=(10, 20, 30)).save(images_dir / "hero-earlier.jpg")
    Image.new("RGB", (64, 32), color=(20, 30, 40)).save(images_dir / "hero-latest.jpg")
    _write_post(
        posts_dir / "2026-04-08-earlier.md",
        title="Earlier",
        date="2026-04-08T18:00:00-05:00",
        image="/images/hero-earlier.jpg",
        description="Earlier description.",
    )
    _write_post(
        posts_dir / "2026-04-10-latest.md",
        title="Latest",
        date="2026-04-10T18:00:00-05:00",
        image="/images/hero-latest.jpg",
        description="Latest description.",
    )
    save_shared_slug(tmp_path / "shared_posts.json", "latest")

    result = share_latest_post(
        blog_root=tmp_path,
        posts_dir=posts_dir,
        ledger_path=tmp_path / "shared_posts.json",
        credentials_path=tmp_path / "credentials.json",
        now=datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc),
        dry_run=True,
    )

    assert result.status == "skipped"
    assert result.slug == "latest"
    assert "already shared" in result.message.lower()
    assert result.url == "https://jweese001.github.io/lemmy-blog/posts/2026-04-10-latest/"


def test_share_latest_post_requires_override_for_stale_manual_slug(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(share_latest_to_bluesky_module, "is_public_post_live", lambda url, timeout=20: True)
    posts_dir = tmp_path / "content" / "posts"
    images_dir = tmp_path / "static" / "images"
    posts_dir.mkdir(parents=True)
    images_dir.mkdir(parents=True)
    Image.new("RGB", (64, 32), color=(10, 20, 30)).save(
        images_dir / "hero-when-bluegrass-met-the-mosh-pit.jpg"
    )
    _write_post(
        posts_dir / "2026-04-30-when-bluegrass-met-the-mosh-pit.md",
        title="When Bluegrass Met the Mosh Pit",
        date="2026-04-30T18:00:00-05:00",
        image="/images/hero-when-bluegrass-met-the-mosh-pit.jpg",
        description="A crossover worth sharing.",
    )

    result = share_latest_post(
        blog_root=tmp_path,
        posts_dir=posts_dir,
        ledger_path=tmp_path / "ledger.json",
        credentials_path=tmp_path / "credentials.json",
        now=datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc),
        dry_run=True,
        slug="when-bluegrass-met-the-mosh-pit",
    )

    assert result.status == "skipped"
    assert "override" in result.message.lower()


def test_share_latest_post_skips_manual_slug_when_post_is_not_live(tmp_path: Path, monkeypatch):
    posts_dir = tmp_path / "content" / "posts"
    images_dir = tmp_path / "static" / "images"
    posts_dir.mkdir(parents=True)
    images_dir.mkdir(parents=True)
    Image.new("RGB", (64, 32), color=(10, 20, 30)).save(images_dir / "hero-not-live.jpg")
    _write_post(
        posts_dir / "2026-04-10-not-live.md",
        title="Not Live",
        date="2026-04-10T18:00:00-05:00",
        image="/images/hero-not-live.jpg",
        description="Not-live description.",
    )
    monkeypatch.setattr(share_latest_to_bluesky_module, "is_public_post_live", lambda url, timeout=20: False)

    result = share_latest_post(
        blog_root=tmp_path,
        posts_dir=posts_dir,
        ledger_path=tmp_path / "ledger.json",
        credentials_path=tmp_path / "credentials.json",
        now=datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc),
        dry_run=True,
        slug="not-live",
        allow_stale=True,
    )

    assert result.status == "skipped"
    assert result.slug == "not-live"
    assert "not yet live" in result.message.lower()

def test_share_latest_post_allows_stale_manual_slug_in_dry_run(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(share_latest_to_bluesky_module, "is_public_post_live", lambda url, timeout=20: True)
    posts_dir = tmp_path / "content" / "posts"
    images_dir = tmp_path / "static" / "images"
    posts_dir.mkdir(parents=True)
    images_dir.mkdir(parents=True)
    Image.new("RGB", (64, 32), color=(10, 20, 30)).save(
        images_dir / "hero-when-bluegrass-met-the-mosh-pit.jpg"
    )
    _write_post(
        posts_dir / "2026-02-08-when-bluegrass-met-the-mosh-pit.md",
        title="When Bluegrass Met the Mosh Pit",
        date="2026-02-08T18:00:00-05:00",
        image="/images/hero-when-bluegrass-met-the-mosh-pit.jpg",
        description="A crossover worth sharing.",
    )

    result = share_latest_post(
        blog_root=tmp_path,
        posts_dir=posts_dir,
        ledger_path=tmp_path / "ledger.json",
        credentials_path=tmp_path / "credentials.json",
        now=datetime(2026, 4, 30, 12, 0, tzinfo=timezone.utc),
        dry_run=True,
        slug="when-bluegrass-met-the-mosh-pit",
        allow_stale=True,
    )

    assert result.status == "dry_run"
    assert "When Bluegrass Met the Mosh Pit" in result.message