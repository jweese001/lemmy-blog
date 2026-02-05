# R&R Kava Bar Site - Style Guide

*Based on w33s3.com design system*

---

## Fonts

| Purpose | Font Family | Fallback |
|---------|-------------|----------|
| Display/Headings | Instrument Serif | Georgia, serif |
| Body | Sora | system-ui, sans-serif |
| Mono/Labels | JetBrains Mono | SF Mono, monospace |

### Google Fonts Import
```css
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600&family=Sora:wght@300;400;500;600&display=swap');
```

---

## Colors

### Core Palette

| Name | Variable | Value | Usage |
|------|----------|-------|-------|
| Ink (Primary Text) | `--ink` | `#1a1a1a` | Body text on light |
| Ink Muted | `--ink-muted` | `#374151` | Secondary text |
| Ink Subtle | `--ink-subtle` | `#6b7280` | Tertiary text |
| Paper (Background) | `--paper` | `#ffffff` | Light backgrounds |
| Paper Muted | `--paper-muted` | `#f3f4f6` | Alt light backgrounds |
| Paper Subtle | `--paper-subtle` | `#e5e7eb` | Borders, dividers |

### Dark Mode Colors

| Name | Variable | Value | Usage |
|------|----------|-------|-------|
| Dark Section BG | N/A | `rgb(10, 10, 10)` | Dark sections |
| Text on Dark | `--text-on-dark` | `#ffffff` | Headings on dark |
| Text on Dark Muted | `--text-on-dark-muted` | `rgba(255, 255, 255, .7)` | Body on dark |

### Accent Colors

| Name | Variable | Value | Usage |
|------|----------|-------|-------|
| Primary Accent | `--accent` | `#c77dcd` | Purple/pink |
| Accent Muted | `--accent-muted` | `#b46aba` | Hover states |
| Accent Teal | `--accent-teal` | `#9dd9d9` | H2 labels |
| Accent Sage | `--accent-sage` | `#c4c67a` | Alt accent |
| Accent Glow | `--accent-glow` | `rgba(199, 125, 205, .15)` | Glow effects |

### For R&R Kava Bar - Adapted Palette

We'll adapt the palette with earthy/botanical tones while keeping the structure:

| Name | Variable | Value | Usage |
|------|----------|-------|-------|
| Primary Accent | `--accent` | `#8B7355` | Warm brown (kava) |
| Accent Alt | `--accent-alt` | `#6B8E6B` | Sage green (botanical) |
| Accent Teal | `--accent-teal` | `#7BA7A7` | Muted teal (labels) |
| Dark BG | `--dark-bg` | `#1a1612` | Warm dark |

---

## Typography Scale

| Name | Variable | Value |
|------|----------|-------|
| 5XL | `--text-5xl` | `clamp(3rem, 2rem + 5vw, 6rem)` |
| 4XL | `--text-4xl` | `clamp(2.5rem, 2rem + 2.5vw, 4rem)` |
| 3XL | `--text-3xl` | `clamp(2rem, 1.5rem + 2.5vw, 3rem)` |
| 2XL | `--text-2xl` | `clamp(1.5rem, 1.25rem + 1.25vw, 2rem)` |
| XL | `--text-xl` | `clamp(1.25rem, 1.1rem + .75vw, 1.5rem)` |
| LG | `--text-lg` | `clamp(1.1rem, 1rem + .5vw, 1.25rem)` |
| Base | `--text-base` | `clamp(.95rem, .9rem + .25vw, 1.05rem)` |
| SM | `--text-sm` | `clamp(.8rem, .75rem + .25vw, .9rem)` |
| XS | `--text-xs` | `clamp(.7rem, .65rem + .25vw, .8rem)` |

---

## Spacing Scale

| Name | Variable | Value |
|------|----------|-------|
| XS | `--space-xs` | `.25rem` |
| SM | `--space-sm` | `.5rem` |
| MD | `--space-md` | `1rem` |
| LG | `--space-lg` | `1.5rem` |
| XL | `--space-xl` | `2rem` |
| 2XL | `--space-2xl` | `3rem` |
| 3XL | `--space-3xl` | `4rem` |
| 4XL | `--space-4xl` | `6rem` |
| 5XL | `--space-5xl` | `8rem` |

---

## Layout

| Property | Variable | Value |
|----------|----------|-------|
| Max Width | `--max-width` | `1400px` |
| Content Width | `--content-width` | `900px` |
| Nav Height | `--nav-height` | `72px` |
| Container Padding | N/A | `0 32px` |

---

## Borders & Shadows

### Borders (Light)
```css
--border-subtle: 1px solid rgba(0,0,0,.06);
--border-muted: 1px solid rgba(0,0,0,.1);
```

### Borders (Dark)
```css
--border-dark-subtle: 1px solid rgba(255,255,255,.08);
--border-dark-muted: 1px solid rgba(255,255,255,.15);
```

### Shadows
```css
--shadow-sm: 0 1px 2px rgba(0,0,0,.04);
--shadow-md: 0 4px 12px rgba(0,0,0,.06);
--shadow-lg: 0 12px 40px rgba(0,0,0,.08);
--shadow-glow: 0 0 40px rgba(199, 125, 205, .15);
```

---

## Animation

| Name | Variable | Value |
|------|----------|-------|
| Fast | `--duration-fast` | `.15s` |
| Normal | `--duration-normal` | `.3s` |
| Slow | `--duration-slow` | `.5s` |
| Ease Out | `--ease-out` | `cubic-bezier(.22, 1, .36, 1)` |
| Ease In Out | `--ease-in-out` | `cubic-bezier(.65, 0, .35, 1)` |

---

## Component Patterns

### Section Structure
```html
<section id="section-name" class="section section-dark">
  <div class="section-background"></div>
  <div class="section-content">
    <!-- Content -->
  </div>
</section>
```

### Navigation
- Sticky nav with semi-transparent background
- Nav background: `rgba(250, 250, 249, 0.85)`
- Height: 72px

### Buttons
- Background: `#1a1a1a`
- Text: `#ffffff`
- Font: JetBrains Mono, 12.8px
- Padding: `8px 16px`
- No border radius (sharp corners)

### H1 (Hero)
- Font: Instrument Serif
- Size: 96px
- Weight: 400
- Color: White (on dark bg)
- Line height: 1

### H2 (Section Labels)
- Font: JetBrains Mono
- Size: 14.4px
- Color: Teal accent (`#9dd9d9`)
- Uppercase tracking likely
- Margin bottom: 48px

### H3 (Content Headings)
- Font: Sora
- Size: 20px
- Weight: 600
- Color: Ink (`#1a1a1a`)

---

## Page Structure (Single Page)

Based on w33s3.com:
1. **Hero** - Full viewport, dark background
2. **Overview** - Light section
3. **Details** - Dark section
4. **Features/Content** - Alternating light/dark
5. **Footer**

For R&R Kava Bar:
1. **Hero** - R&R Kava Bar intro
2. **Executive Summary** - Key highlights
3. **Financials** - Pro forma, assumptions
4. **Investment** - Scenarios for Randy
5. **Risk Analysis** - Kratom impact
6. **Full Plan** - Detailed business plan
7. **Contact/Footer**

---

*Last Updated: February 2026*
