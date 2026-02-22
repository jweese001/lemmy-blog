# FlowBoard Image Generation Workflow

## Overview

This document describes the proven workflow for generating images using FlowBoard JSON files and the Gemini 3 Pro API. This is the same approach used by the lemmy-blog 6pm cron job.

## The Collaborative Process

1. **Claude creates FlowBoard workflow JSON files** with image descriptions
2. **Gemini 3 Pro API generates images** based on the workflow prompts
3. **User can edit workflow files** in FlowBoard UI to make adjustments
4. **Claude examines user edits** and applies learnings to other files
5. **Repeat** until images are perfect

This is iterative and collaborative - the FlowBoard files are the source of truth that both human and AI can edit.

---

## Step 1: Create FlowBoard Workflow JSON

Each image needs a `.json` workflow file with this structure:

```json
{
  "version": "1.0.0",
  "project": {
    "id": "unique-project-id",
    "name": "Human-readable name",
    "nodes": [
      {
        "id": "style-1",
        "type": "style",
        "position": {"x": 50, "y": 50},
        "data": {
          "label": "Style",
          "name": "Style Name",
          "description": "Overall visual style, mood, atmosphere, color palette..."
        }
      },
      {
        "id": "action-1",
        "type": "action",
        "position": {"x": 50, "y": 280},
        "data": {
          "label": "Action",
          "content": "Specific scene description, what's happening, composition..."
        }
      },
      {
        "id": "negative-1",
        "type": "negative",
        "position": {"x": 350, "y": 50},
        "data": {
          "label": "Negative",
          "content": "Things to avoid: text, logos, specific unwanted elements..."
        }
      },
      {
        "id": "parameters-1",
        "type": "parameters",
        "position": {"x": 350, "y": 280},
        "data": {
          "label": "Parameters",
          "model": "gemini-pro",
          "aspectRatio": "16:9",
          "resolution": "2K"
        }
      },
      {
        "id": "output-1",
        "type": "output",
        "position": {"x": 650, "y": 165},
        "data": {
          "label": "Output",
          "promptPreview": "",
          "status": "idle",
          "outputPath": "images/filename.png"
        }
      }
    ],
    "edges": [
      {"id": "e-style-output", "source": "style-1", "target": "output-1"},
      {"id": "e-action-output", "source": "action-1", "target": "output-1"},
      {"id": "e-negative-output", "source": "negative-1", "target": "output-1"},
      {"id": "e-params-output", "source": "parameters-1", "target": "output-1", "targetHandle": "config"}
    ],
    "groups": [],
    "createdAt": 1770442000000,
    "updatedAt": 1770442000000
  },
  "exportedAt": 1770442000000
}
```

### Node Types

| Node Type | Purpose |
|-----------|---------|
| `style` | Overall visual style, mood, colors, atmosphere |
| `action` | Specific scene description, what's in the image |
| `negative` | Things to exclude from the image |
| `parameters` | Technical settings: model, aspect ratio, resolution |
| `output` | Where to save the generated image |

---

## Step 2: Valid Gemini 3 Pro Aspect Ratios

**IMPORTANT**: Gemini 3 Pro only supports these aspect ratios:

| Aspect Ratio | Use Case |
|--------------|----------|
| `1:1` | Square (profile photos, icons) |
| `2:3` | Portrait |
| `3:2` | Landscape |
| `3:4` | Portrait |
| `4:3` | Standard landscape |
| `4:5` | Portrait |
| `5:4` | Slight landscape |
| `9:16` | Vertical/mobile |
| `16:9` | Widescreen (hero images, banners) |
| `21:9` | Ultra-wide (cinematic banners) |

**Invalid ratios will fail**: `2:1`, `3:1`, `4:1`, etc.

---

## Step 3: Generate Images with Python Script

### The Generation Script

Create a Python script that:
1. Reads workflow JSON files
2. Builds prompts from style + action + negative nodes
3. Calls Gemini 3 Pro API
4. Saves the resulting image

### Key API Configuration

```python
# Gemini 3 Pro API endpoint
GEMINI_MODEL = "gemini-3-pro-image-preview"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# CORRECT generation config structure
generation_config = {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {
        "aspectRatio": aspect_ratio,  # MUST be inside imageConfig!
        "imageSize": "2K"
    }
}

# Request body
request_body = {
    "contents": [
        {
            "parts": [{"text": prompt}]
        }
    ],
    "generationConfig": generation_config
}

# Make the request
response = requests.post(
    f"{GEMINI_API_URL}?key={api_key}",
    headers={"Content-Type": "application/json"},
    json=request_body,
    timeout=120
)
```

### Building the Prompt

Combine workflow nodes into a single prompt:

```python
def build_prompt_from_workflow(workflow):
    style_desc = ""
    action_desc = ""
    negative_desc = ""
    aspect_ratio = "16:9"  # default

    for node in workflow["project"]["nodes"]:
        if node["type"] == "style":
            style_desc = node["data"].get("description", "")
        elif node["type"] == "action":
            action_desc = node["data"].get("content", "")
        elif node["type"] == "negative":
            negative_desc = node["data"].get("content", "")
        elif node["type"] == "parameters":
            aspect_ratio = node["data"].get("aspectRatio", "16:9")

    # Combine into prompt
    prompt = f"{style_desc}\n\n{action_desc}"
    if negative_desc:
        prompt += f"\n\nAvoid: {negative_desc}"

    return prompt, aspect_ratio
```

### Extracting Image from Response

```python
def extract_image_from_response(response_json):
    """Extract base64 image data from Gemini response."""
    candidates = response_json.get("candidates", [])
    if not candidates:
        return None

    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"])

    return None
```

---

## Step 4: Get API Key

The API key can be loaded from multiple sources (in order of priority):

1. `GEMINI_API_KEY` environment variable
2. File path in `GEMINI_API_KEY_FILE` environment variable
3. `.env` file with `GEMINI_API_KEY_FILE=path/to/key`
4. FlowBoard settings (if applicable)

Reference implementation in `/home/lemmy/lemmy-blog/scripts/generate_hero.py`:

```python
def get_api_key():
    # Try environment variable first
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key.strip()

    # Try loading from key file
    key_file_path = os.environ.get("GEMINI_API_KEY_FILE")
    if not key_file_path:
        # Check .env file
        env_file = PROJECT_DIR / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY_FILE="):
                        key_file_path = line.split("=", 1)[1].strip()
                        break

    if key_file_path:
        key_file = Path(key_file_path)
        if key_file.exists():
            with open(key_file) as f:
                return f.read().strip()

    raise ValueError("No API key found")
```

---

## Complete Example Script

See `/home/lemmy/claude-code-telegram/claude-code-telegram/ObsidianVault/fractional-consulting/site/generate-images.py` for a working implementation.

Key points:
- Import `get_api_key` from lemmy-blog's generate_hero.py
- Process all `.json` files in workflows directory
- Skip non-workflow JSON files gracefully
- Save images to the path specified in output node's `outputPath`

---

## Common Errors and Fixes

### Error: `Unknown name "aspectRatio" at 'generation_config'`

**Cause**: `aspectRatio` is at the wrong level in the config.

**Wrong**:
```python
generation_config = {
    "responseModalities": ["TEXT", "IMAGE"],
    "aspectRatio": "16:9",  # WRONG - top level
}
```

**Correct**:
```python
generation_config = {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {
        "aspectRatio": "16:9",  # CORRECT - inside imageConfig
        "imageSize": "2K"
    }
}
```

### Error: `aspect_ratio must be one of '1:1', '2:3'...`

**Cause**: Using an unsupported aspect ratio like `2:1`, `3:1`, `4:1`.

**Fix**: Use only the supported ratios listed above. Map custom ratios to nearest valid option:
- `2:1` → `16:9`
- `3:1` → `21:9`
- `4:1` → `21:9`

### Error: API key not found

**Fix**: Ensure one of these is set:
- `GEMINI_API_KEY` environment variable
- `GEMINI_API_KEY_FILE` pointing to a file with the key
- `.env` file with the key file path

---

## w33s3 Style Guide Reference

When creating images for w33s3/IAS projects, use these colors:

| Color | Hex | Usage |
|-------|-----|-------|
| Dark background | `rgb(10, 10, 10)` / `#0a0a0a` | Primary background |
| Purple accent | `#c77dcd` | Primary accent, glows |
| Teal accent | `#9dd9d9` | Secondary accent, highlights |
| Dark alt | `rgb(18, 18, 18)` | Card backgrounds |

Style keywords: dark, moody, high contrast, minimalist, sophisticated, cinematic, volumetric lighting, no text, no watermarks.

---

## File Locations

| File | Purpose |
|------|---------|
| `workflows/*.json` | FlowBoard workflow definitions |
| `images/*.png` | Generated output images |
| `generate-images.py` | Python script to run generation |
| `/home/lemmy/lemmy-blog/scripts/generate_hero.py` | Reference implementation with `get_api_key()` |

---

## Summary

1. Create workflow JSON with style, action, negative, parameters, output nodes
2. Use valid Gemini aspect ratios only
3. Put `aspectRatio` inside `imageConfig` in the API request
4. Load API key from environment or file
5. Run the generation script
6. User can edit workflows in FlowBoard UI and regenerate

This workflow enables iterative, collaborative image generation where both human and AI can contribute to refining the visual output.
