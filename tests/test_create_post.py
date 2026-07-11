from scripts.create_post import BLUESKY_CTA, ensure_bluesky_cta


def test_ensure_bluesky_cta_adds_link_after_trailing_question_before_sources():
    content = (
        "What city do you think is quietly building the next great kava scene right now?\n\n"
        "---\n\n"
        "**Sources:**\n"
        "- https://example.com/source\n"
    )

    updated = ensure_bluesky_cta(content)

    assert BLUESKY_CTA in updated
    assert updated.index(BLUESKY_CTA) > updated.index("What city do you think")
    assert updated.index(BLUESKY_CTA) < updated.index("**Sources:**")


def test_ensure_bluesky_cta_does_not_duplicate_existing_canonical_link():
    content = "Got thoughts? Hit me up on [Bluesky](https://bsky.app/profile/lemmysmic.bsky.social)."

    updated = ensure_bluesky_cta(content)

    assert updated == content


def test_ensure_bluesky_cta_does_not_treat_plain_bluesky_mention_as_existing_cta():
    content = "I posted a note about Bluesky moderation trends today."

    updated = ensure_bluesky_cta(content)

    assert BLUESKY_CTA in updated
    assert updated.count("https://bsky.app/profile/lemmysmic.bsky.social") == 1
