# FlowBoard Guide for Lemmy's Mic

This guide teaches you (Lemmy) how to use FlowBoard to generate hero images for blog posts.

---

## The Creative Process: Blog Topic → Hero Image

Before touching FlowBoard, think through these questions:

### 1. What's the post about?
Read your blog post. What's the core theme or feeling?

### 2. What visual represents that?
Don't be literal. A post about "indie games" doesn't need a screenshot - it needs a **mood**.

| Post Topic | Literal (❌) | Evocative (✅) |
|------------|-------------|----------------|
| Indie game review | Screenshot of the game | Pixel art character emerging from glowing CRT |
| E-bike commuting | Photo of an e-bike | Rain-slicked street, bike light cutting through fog |
| Punk album review | Album cover | Sweaty basement show, crowd energy, stage lights |
| Kava bar culture | Cup of kava | Warm gathering, shell ceremony, community moment |
| AI tools article | Robot or code | Abstract neural flow, creative energy visualization |

### 3. Build the scene in your head
Ask yourself:
- **Setting:** Where does this scene take place?
- **Subject:** What's the focal point?
- **Mood:** What emotion should the viewer feel?
- **Lighting:** What time of day? What light sources?

### 4. Write it as a scene description
Write 1-2 sentences describing what you see. Be specific:

**Weak:** "Indie games image"
**Strong:** "Colorful pixel art characters leap from a glowing CRT monitor in a dark room, retro arcade machines visible in the background, neon pink and blue light spilling across the scene"

### 5. Apply the w33s3 aesthetic
Every image should feel:
- Dark and moody
- High contrast
- Cinematic
- Professional, not cheesy

---

## What is FlowBoard?

FlowBoard is a visual prompt-building tool for AI image generation. Instead of writing one long prompt, you build a **node graph** where different aspects of the image (character, setting, style, action) are separate nodes that connect together.

**Key insight:** Only nodes **connected** to an Output node contribute to the prompt. You can have many nodes on the canvas, but only the connected ones matter.

---

## Quick Start: Generating a Blog Hero Image

### Step 1: Open FlowBoard

```bash
cd ~/claude-code-telegram/claude-code-telegram/flow-board/client
npm run dev
# Opens at http://localhost:5173/flow-board/
```

Or use the live version: https://jweese001.github.io/flowboard-demo/

### Step 2: Configure API Key (First Time Only)

1. Click **Settings** in the left sidebar
2. Add your **Gemini API key** from [Google AI Studio](https://aistudio.google.com/apikey)
3. Or use **mock** mode for testing (no key needed)

### Step 3: Build Your Image from Scratch

**Add nodes from the left sidebar (click + button):**

1. **Add Style Node** (purple)
   - Click **Style** in sidebar → click **+**
   - Click the node to select it
   - In Properties panel (right side):
     - Name: `w33s3 Dark`
     - Description: `Dark, moody atmosphere with high contrast lighting. Cinematic composition with neon accent colors against deep blacks. Professional photography feel, dramatic shadows, rich color depth.`

2. **Add Action Node** (orange)
   - Click **Action** in sidebar → click **+**
   - In Properties:
     - Content: `[Your scene description - be specific and evocative]`

3. **Add Parameters Node** (teal)
   - Click **Parameters** in sidebar → click **+**
   - In Properties:
     - Model: `gemini-flash` (or `mock` for testing)
     - Aspect Ratio: `16:9`

4. **Add Output Node** (red)
   - Click **Output** in sidebar → click **+**
   - This is where generation happens

5. **Connect the nodes:**
   - Drag from **right handle** (●) of Style → **left handle** of Output
   - Drag from **right handle** of Action → **left handle** of Output
   - Drag from **right handle** of Parameters → **config handle** (top) of Output

Your graph should look like:
```
Style ──────┐
            ├──→ Output
Action ─────┘       ↑
                    │
Parameters ─────────┘ (config)
```

### Step 4: Generate

1. Click the Output node
2. Click **Generate**
3. Wait for the image
4. Right-click the image → Save As → `~/lemmy-blog/static/images/hero-{slug}.png`

---

## Node Types Reference

### Content Nodes (What's in the image)

| Node | Color | Purpose | Example |
|------|-------|---------|---------|
| **Character** | Blue | Who is in the scene | "A pixel art warrior, 8-bit style, sword raised" |
| **Setting** | Green | Where it takes place | "Neon-lit arcade, retro gaming machines, dark atmosphere" |
| **Prop** | Amber | Important objects | "Vintage synthesizer, glowing keys, cables everywhere" |
| **Extras** | Slate | Background elements | "Crowd of gamers, screens glowing, ambient chatter" |
| **Action** | Orange | What's happening | "Controller in hand, intense focus, screen light on face" |

### Style Nodes (How it looks)

| Node | Color | Purpose | Example |
|------|-------|---------|---------|
| **Style** | Purple | Visual aesthetic | "Dark moody atmosphere, high contrast, neon accents, cinematic" |
| **Shot** | Pink | Camera framing | Preset: close-up, wide, establishing, etc. |

### Technical Nodes (Generation settings)

| Node | Color | Purpose | Example |
|------|-------|---------|---------|
| **Parameters** | Teal | Model, aspect ratio | model: gemini-flash, aspectRatio: 16:9 |
| **Negative** | Rose | What to avoid | "blurry, low quality, text, watermark, signature" |
| **Output** | Red | Generate image | Click Generate button |

---

## The w33s3 Style for Lemmy's Mic

Use this Style node description for all blog hero images:

```
Name: w33s3 Dark
Description: Dark, moody atmosphere with high contrast lighting.
Cinematic composition with neon accent colors against deep blacks.
Professional photography feel, dramatic shadows, rich color depth.
Modern minimalist aesthetic, no text or watermarks.
```

---

## Full Examples: From Blog Post to Image

### Example 1: Indie Games Post

**Blog post:** "February 2026: The Indie Games Worth Your Attention"
- Reviews of 5 indie games releasing this month

**Think through it:**
1. What's the theme? → Discovery, excitement, hidden gems
2. What visual? → Not screenshots. The *feeling* of discovering indie games
3. Setting? → A cozy gaming setup, retro meets modern
4. Mood? → Nostalgic but fresh, inviting, curious
5. Lighting? → Screen glow, neon accents, dark room

**Action node content:**
```
Colorful pixel art characters leap from a glowing CRT monitor,
retro arcade machines in the background, neon pink and cyan light
spilling across a dark room, sense of discovery and wonder
```

**Result:** An evocative image that *feels* like indie gaming culture

---

### Example 2: E-Bike Review

**Blog post:** "The Rad Power RadCity 5 Plus: 6 Months Later"
- Long-term review of an e-bike

**Think through it:**
1. Theme? → Urban freedom, practical adventure
2. Visual? → Not just a bike photo. The *experience* of e-biking
3. Setting? → City at dusk, after work, heading home
4. Mood? → Freedom, capability, modern urban life
5. Lighting? → Golden hour fading to blue, bike lights on

**Action node content:**
```
Sleek e-bike parked on wet city street at dusk, integrated lights
glowing, city skyline silhouette behind, puddles reflecting neon
signs, sense of urban freedom and possibility
```

---

### Example 3: Punk Album Review

**Blog post:** "IDLES 'TANGK' - Raw Energy Meets Vulnerability"
- Album review

**Think through it:**
1. Theme? → Raw energy, emotional honesty, community
2. Visual? → Not the album cover. The *energy* of their music
3. Setting? → Underground venue, intimate show
4. Mood? → Intense, cathartic, sweat and unity
5. Lighting? → Harsh stage lights, silhouettes, smoke

**Action node content:**
```
Silhouette of singer screaming into microphone, harsh spotlight
from behind, crowd hands raised, sweat and smoke in the air,
intimate punk venue, raw emotional energy, high contrast
```

---

## Simpler Workflow (Style + Action Only)

For most blog heroes, you only need:

```
Style ──────┐
            ├──→ Output ←── Parameters (config)
Action ─────┘
```

**Style:** Always the w33s3 dark description
**Action:** Your evocative scene description
**Parameters:** gemini-flash, 16:9

### E-Bikes Post

```
Nodes:
1. Style: "w33s3 Dark"
2. Setting: "Urban street at dusk, wet pavement reflecting city lights"
3. Prop: "Sleek electric bike, integrated lights glowing,
   modern minimalist design"
4. Action: "E-bike parked under streetlight, rain droplets on frame,
   city silhouette behind"
5. Parameters: model=gemini-flash, aspectRatio=16:9
6. Output: Connect all

Connection:
Style ──┐
Setting ─┼──→ Output ←── Parameters
Prop ────┤
Action ──┘
```

### Punk Music Post

```
Nodes:
1. Style: "w33s3 Dark, grain texture, high contrast,
   analog film aesthetic"
2. Setting: "Underground venue, graffiti walls, dim stage lights"
3. Action: "Electric guitar silhouette against spotlight,
   smoke in the air, raw energy"
4. Parameters: model=gemini-flash, aspectRatio=16:9
5. Output: Connect all
```

### Kava Bar Post

```
Nodes:
1. Style: "w33s3 Dark, warm amber undertones, cozy atmosphere"
2. Setting: "Intimate kava bar, wooden furniture, soft lighting,
   tropical plants"
3. Prop: "Traditional kava bowl, coconut shells, ambient candles"
4. Action: "Peaceful gathering, shells raised, warm community vibe"
5. Parameters: model=gemini-flash, aspectRatio=16:9
6. Output: Connect all
```

### AI Art / Tech Post

```
Nodes:
1. Style: "w33s3 Dark, digital aesthetic, circuit patterns,
   data visualization feel"
2. Action: "Abstract flow of glowing nodes and connections,
   neural network visualization, creative energy"
3. Parameters: model=gemini-flash, aspectRatio=16:9
4. Output: Connect all
```

---

## Using the Workflow Generator Script

For quick workflow creation without opening FlowBoard UI:

```bash
cd ~/lemmy-blog

# Generate workflow JSON
.venv/bin/python scripts/generate_workflow.py \
  "February 2026 Indie Games" \
  "Colorful pixel art characters emerging from a retro gaming screen, neon glow" \
  --slug february-2026-indie-games \
  --model gemini-flash

# Output: workflows/blog-february-2026-indie-games.json
```

Then open FlowBoard and load this file to edit or generate.

---

## Tips for Better Images

### Do:
- Be specific with descriptions ("worn leather jacket" not "jacket")
- Include lighting details ("neon glow", "dramatic shadows")
- Use sensory language ("rain-slicked", "glowing", "weathered")
- Keep the w33s3 dark aesthetic consistent
- Use 16:9 aspect ratio for blog heroes

### Don't:
- Include text in images (AI struggles with text)
- Use overly complex scenes (keep it focused)
- Forget the Negative node for quality issues
- Mix conflicting styles

### Negative Prompt (Always Include):
```
blurry, low quality, distorted, watermark, signature, text,
logo, oversaturated, amateur, stock photo
```

---

## Saving Images for Blog

After generating:

1. Right-click the image in the Output node
2. Save As: `~/lemmy-blog/static/images/hero-{slug}.png`
3. Reference in post frontmatter: `image: "/images/hero-{slug}.png"`

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Cmd+S | Save project |
| Cmd+C | Copy selected nodes |
| Cmd+V | Paste |
| Delete | Delete selected |
| Cmd+G | Group nodes |
| Escape | Deselect / exit |

---

## File Locations

| File | Purpose |
|------|---------|
| `~/lemmy-blog/workflows/` | Generated workflow JSONs |
| `~/lemmy-blog/static/images/` | Hero images (hero-{slug}.png) |
| `~/lemmy-blog/scripts/generate_workflow.py` | Workflow generator |
| FlowBoard settings | Stored in browser localStorage |

---

## Troubleshooting

**"API key not configured"**
→ Settings → Add Gemini API key, or use `--model mock` for testing

**Image quality issues**
→ Add Negative node: "blurry, low quality, distorted, text"

**Wrong aspect ratio**
→ Check Parameters node: aspectRatio should be "16:9" for blog headers

**FlowBoard won't start**
→ `cd ~/claude-code-telegram/claude-code-telegram/flow-board/client && npm install && npm run dev`

---

*Now go make some sick hero images for Lemmy's Mic!*
