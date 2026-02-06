# Lemmy's Mic - Blog Critique & Improvements

*Self-critique by Lemmy - February 2026*

---

## What's Working Well

- Dark theme is on-point for the subject matter (punk, indie games, kava bars)
- Header illustration is striking and establishes personality immediately
- Typography is clean and readable (Instrument Serif + Sora is a solid combo)
- Topic category pills help with navigation
- About page is honest and charming - the Lemmy Kilmister reference is a nice touch
- Hero images have a cohesive moody aesthetic

---

## Areas for Improvement

### 1. Visual Hierarchy on Homepage
The posts all look the same weight. The most recent post should POP more.

**Fix:** Make the first post a featured card with a larger hero image, then stack the rest below in a tighter grid.

### 2. Hero Images Need More Variety
The punk band illustration (black & white linework) is fantastic. The kava bar image is moody and atmospheric. But they're stylistically different.

**Fix:** Establish 2-3 illustration "modes":
- **Documentary/Photorealistic** - for kava, e-bikes (lifestyle stuff)
- **Raw/Graphic** - for punk (that B&W illustration style is perfect)
- **Pixel/Retro** - for indie games

Then be consistent within each topic.

### 3. The "Read More" Buttons Feel Weak
They're there but don't invite clicks.

**Fix:** Make them more prominent or switch to a "Continue reading →" text link that feels more editorial.

### 4. No Author Personality in Posts
The writing is good but there's no avatar, no "Lemmy says" callouts, no personality flourishes within the content.

**Fix:** Add a small Lemmy avatar/illustration that appears in posts. Maybe a sidebar callout box for hot takes.

### 5. Sources Section is Buried
As a reader, I actually appreciate the sourced journalism. But it's hidden at the bottom in plain text.

**Fix:** Style the sources section distinctively - maybe a left border accent, slightly different background, or an icon.

### 6. No Social/Engagement Layer
The posts ask questions ("Have you tried kava yet?") but there's nowhere to respond.

**Fix:** Add a comments system (Disqus, Giscus for GitHub-based) or at minimum link to a Discord/community.

### 7. Mobile Experience
Desktop-only review. Mobile is where most readers are - needs testing.

### 8. The About Page Date Says "January 1, 0001"
That's a Hugo default date bug. Minor but looks unpolished.

---

## Illustration-Specific Feedback

The punk band hero is the strongest piece - it has energy, texture, and tells a story. Art direction recommendations:

1. **More illustrations like the punk one** - that hand-drawn, high-contrast, slightly chaotic energy fits the blog's voice
2. **Custom spot illustrations** - small icons or drawings for each topic category
3. **A Lemmy mascot** - a simple character (robot? microphone with attitude?) that could appear across the site
4. **Pull quotes with illustrated frames** - for the best lines in each post

---

## Quick Wins (Things You Could Do Today)

- [x] Fix the About page date
- [x] Add a favicon (mic icon in teal)
- [x] Style the Sources section with a left border accent
- [ ] Test mobile experience

---

## Implementation Priority

| Priority | Item | Effort | Status |
|----------|------|--------|--------|
| High | Fix About page date bug | Low | ✅ Done |
| High | Featured post on homepage | Medium | ✅ Done |
| Medium | Style sources section | Low | ✅ Done |
| Medium | Tags index page (no images) | Low | ✅ Done |
| Medium | Consistent illustration modes | High | Pending |
| Low | Comments/engagement | Medium | Pending |
| Low | Lemmy mascot | High | ✅ Done (avatar on About) |

---

## Session Log - Feb 6, 2026

### Completed This Session:
- Featured post layout: 16:9 image on top, compact text below
- "Continue reading →" links with arrow animation
- 2-column grid for remaining posts with equal-height cards
- More spacing between excerpt and footer in all cards
- Tags index page: clean grid without image placeholders
- Gemini 3 Pro with 16:9 aspect ratio for all image generation
- Updated all FlowBoard templates to use gemini-pro
- Fixed FlowBoard gemini.ts to pass aspectRatio parameter
- Lemmy avatar image restored on About page

### Pending:
- Test mobile responsiveness
- Consistent illustration modes per topic
- Comments/engagement system
