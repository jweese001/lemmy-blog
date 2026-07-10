from scripts.create_post import BLUESKY_CTA, append_bluesky_cta


def test_append_bluesky_cta_adds_link_after_trailing_question():
    content = "What city do you think is quietly building the next great kava scene right now?"

    updated = append_bluesky_cta(content)

    assert content in updated
    assert BLUESKY_CTA in updated
    assert updated.index(BLUESKY_CTA) > updated.index(content)


def test_append_bluesky_cta_does_not_duplicate_existing_link():
    content = "Got thoughts? Hit me up on [Bluesky](https://bsky.app/profile/lemmysmic.bsky.social)."

    updated = append_bluesky_cta(content)

    assert updated == content
