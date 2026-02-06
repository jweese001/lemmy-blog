#!/home/lemmy/lemmy-blog/.venv/bin/python
"""
Generate hero images for Lemmy's Mic blog posts using Gemini API.

This script:
1. Creates a FlowBoard workflow JSON file (source of truth)
2. Uses that workflow to generate the image via Gemini API

The workflow file can be opened in FlowBoard UI to inspect or edit.

Usage:
    python generate_hero.py "Post Title" "Scene description" --slug my-post-slug
    python generate_hero.py "February 2026 Indie Games" "Pixel art characters" --template indie-games
    python generate_hero.py "Title" "Scene" --dry-run  # Create workflow only, no image
    python generate_hero.py --list-templates  # Show available templates
"""

import argparse
import base64
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

# Directories
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
WORKFLOW_DIR = PROJECT_DIR / "workflows"
TEMPLATE_DIR = WORKFLOW_DIR / "templates"
IMAGE_DIR = PROJECT_DIR / "static" / "images"

# w33s3 style - consistent dark aesthetic
W33S3_STYLE = {
    "name": "w33s3 Dark",
    "description": "Dark, moody atmosphere with high contrast lighting. Cinematic composition with neon accent colors against deep blacks. Professional photography feel, dramatic shadows, rich color depth. Modern minimalist aesthetic, no text or watermarks."
}

# Gemini API config
GEMINI_MODEL = "gemini-3-pro-image-preview"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def slugify(title: str) -> str:
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


# =============================================================================
# Template Functions
# =============================================================================

def list_templates() -> list[dict]:
    """List available templates with their descriptions."""
    templates = []
    if not TEMPLATE_DIR.exists():
        return templates

    for f in sorted(TEMPLATE_DIR.glob("*.json")):
        try:
            with open(f) as fp:
                data = json.load(fp)
                templates.append({
                    "name": f.stem,
                    "description": data.get("description", "No description"),
                    "path": f
                })
        except (json.JSONDecodeError, IOError):
            continue

    return templates


def load_template(template_name: str) -> dict:
    """Load a template by name (without .json extension)."""
    template_path = TEMPLATE_DIR / f"{template_name}.json"
    if not template_path.exists():
        available = [t["name"] for t in list_templates()]
        raise ValueError(
            f"Template '{template_name}' not found. "
            f"Available: {', '.join(available) if available else 'none'}"
        )

    with open(template_path) as f:
        return json.load(f)


def create_workflow_from_template(
    template: dict,
    title: str,
    scene: str,
    slug: str
) -> dict:
    """Create a new workflow by customizing a template."""
    import copy
    timestamp = int(time.time() * 1000)

    workflow = copy.deepcopy(template)

    # Remove template-only fields
    workflow.pop("template", None)
    workflow.pop("description", None)

    # Update project metadata
    workflow["exportedAt"] = timestamp
    workflow["project"]["id"] = f"blog-{slug}-{timestamp}"
    workflow["project"]["name"] = f"Hero: {title}"
    workflow["project"]["createdAt"] = timestamp
    workflow["project"]["updatedAt"] = timestamp

    # Find and update the action node with the scene
    for node in workflow["project"]["nodes"]:
        if node["type"] == "action":
            node["data"]["content"] = scene
            break

    return workflow


def get_api_key() -> str:
    """Get Gemini API key from environment, file, or FlowBoard settings."""
    # Try environment variable first
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key.strip()

    # Try loading from key file (referenced in .env or directly)
    key_file_path = os.environ.get("GEMINI_API_KEY_FILE")
    if not key_file_path:
        # Check .env file for key file path
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
                api_key = f.read().strip()
                if api_key:
                    return api_key

    # Try FlowBoard's localStorage export (if available)
    flowboard_settings = Path.home() / ".flowboard" / "settings.json"
    if flowboard_settings.exists():
        try:
            with open(flowboard_settings) as f:
                settings = json.load(f)
                api_key = settings.get("apiKeys", {}).get("gemini")
                if api_key:
                    return api_key
        except (json.JSONDecodeError, KeyError):
            pass

    raise ValueError(
        "Gemini API key not found. Set GEMINI_API_KEY environment variable, "
        "GEMINI_API_KEY_FILE path, or configure in FlowBoard settings."
    )


# =============================================================================
# Workflow Creation (Step 1)
# =============================================================================

def create_workflow(title: str, scene: str, slug: str, aspect_ratio: str = "16:9") -> dict:
    """Create a FlowBoard workflow JSON for a hero image."""
    timestamp = int(time.time() * 1000)
    project_id = f"blog-{slug}-{timestamp}"

    workflow = {
        "version": "1.0",
        "exportedAt": timestamp,
        "project": {
            "id": project_id,
            "name": f"Hero: {title}",
            "nodes": [
                {
                    "id": "style-1",
                    "type": "style",
                    "position": {"x": 50, "y": 100},
                    "data": {
                        "label": "Style",
                        "name": W33S3_STYLE["name"],
                        "description": W33S3_STYLE["description"]
                    }
                },
                {
                    "id": "action-1",
                    "type": "action",
                    "position": {"x": 50, "y": 300},
                    "data": {
                        "label": "Action",
                        "content": scene
                    }
                },
                {
                    "id": "parameters-1",
                    "type": "parameters",
                    "position": {"x": 350, "y": 100},
                    "data": {
                        "label": "Parameters",
                        "model": "gemini-flash",
                        "aspectRatio": aspect_ratio,
                        "resolution": "2K"
                    }
                },
                {
                    "id": "output-1",
                    "type": "output",
                    "position": {"x": 350, "y": 300},
                    "data": {
                        "label": "Output",
                        "promptPreview": "",
                        "status": "idle"
                    }
                }
            ],
            "edges": [
                {"id": "e-style-output", "source": "style-1", "target": "output-1"},
                {"id": "e-action-output", "source": "action-1", "target": "output-1"},
                {"id": "e-params-output", "source": "parameters-1", "target": "output-1", "targetHandle": "config"}
            ],
            "createdAt": timestamp,
            "updatedAt": timestamp
        }
    }

    return workflow


def save_workflow(workflow: dict, slug: str) -> Path:
    """Save workflow JSON to the workflows directory."""
    WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"blog-{slug}.json"
    filepath = WORKFLOW_DIR / filename

    with open(filepath, "w") as f:
        json.dump(workflow, f, indent=2)

    print(f"Workflow saved: {filepath}")
    return filepath


# =============================================================================
# Image Generation (Step 2 - reads from workflow)
# =============================================================================

def build_prompt_from_workflow(workflow: dict) -> tuple[str, str]:
    """
    Build the full prompt from a workflow's connected nodes.
    Returns (prompt, aspect_ratio).
    """
    nodes = {n["id"]: n for n in workflow["project"]["nodes"]}
    edges = workflow["project"]["edges"]

    # Find output node and what connects to it
    output_node = None
    connected_node_ids = []
    aspect_ratio = "16:9"

    for node in workflow["project"]["nodes"]:
        if node["type"] == "output":
            output_node = node
            break

    if not output_node:
        raise ValueError("No output node in workflow")

    # Find nodes connected to output
    for edge in edges:
        if edge["target"] == output_node["id"]:
            connected_node_ids.append(edge["source"])

    # Build prompt from connected nodes
    prompt_parts = []

    for node_id in connected_node_ids:
        node = nodes.get(node_id)
        if not node:
            continue

        node_type = node["type"]
        data = node["data"]

        if node_type == "style":
            prompt_parts.append(data.get("description", ""))
        elif node_type == "action":
            prompt_parts.append(f"Scene: {data.get('content', '')}")
        elif node_type == "character":
            prompt_parts.append(f"Character: {data.get('description', '')}")
        elif node_type == "setting":
            prompt_parts.append(f"Setting: {data.get('description', '')}")
        elif node_type == "prop":
            prompt_parts.append(f"Props: {data.get('description', '')}")
        elif node_type == "negative":
            prompt_parts.append(f"Avoid: {data.get('content', '')}")
        elif node_type == "parameters":
            aspect_ratio = data.get("aspectRatio", "16:9")

    full_prompt = "\n\n".join(filter(None, prompt_parts))

    # Add aspect ratio hint to prompt (API doesn't support it as config)
    full_prompt = f"{full_prompt}\n\nAspect ratio: {aspect_ratio} (wide cinematic format)"

    return full_prompt, aspect_ratio


def generate_image_from_workflow(workflow: dict, api_key: str) -> bytes:
    """Generate an image using the prompt built from a workflow."""
    prompt, aspect_ratio = build_prompt_from_workflow(workflow)

    print(f"Generating image with prompt:\n{prompt[:300]}...")
    print(f"Aspect ratio: {aspect_ratio}")

    generation_config = {
        "responseModalities": ["Text", "Image"]
    }

    # Add aspect ratio (supported by gemini-3-pro-image-preview)
    if aspect_ratio:
        generation_config["aspectRatio"] = aspect_ratio

    request_body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": generation_config
    }

    response = requests.post(
        f"{GEMINI_API_URL}?key={api_key}",
        headers={"Content-Type": "application/json"},
        json=request_body,
        timeout=120
    )

    if not response.ok:
        error_text = response.text
        raise RuntimeError(f"Gemini API error ({response.status_code}): {error_text[:500]}")

    data = response.json()

    # Extract image from response
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("No response from Gemini")

    for candidate in candidates:
        parts = candidate.get("content", {}).get("parts", [])
        for part in parts:
            if "inlineData" in part:
                image_data = part["inlineData"]["data"]
                return base64.b64decode(image_data)

    # Check for text response explaining failure
    for candidate in candidates:
        parts = candidate.get("content", {}).get("parts", [])
        for part in parts:
            if "text" in part:
                raise RuntimeError(f"Gemini response: {part['text']}")

    raise RuntimeError("No image in Gemini response")


def save_image(image_bytes: bytes, slug: str) -> Path:
    """Save image to the static/images directory."""
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"hero-{slug}.png"
    output_path = IMAGE_DIR / filename

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"Image saved: {output_path}")
    return output_path


def create_gradient_fallback(slug: str) -> Path:
    """Create a simple gradient fallback image if generation fails."""
    try:
        from PIL import Image, ImageDraw

        # w33s3 dark gradient
        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), '#0a0a0b')
        draw = ImageDraw.Draw(img)

        # Add subtle gradient
        for y in range(height):
            alpha = int(255 * (1 - y / height) * 0.1)
            draw.line([(0, y), (width, y)], fill=(59, 130, 246, alpha))

        output_path = IMAGE_DIR / f"hero-{slug}.png"
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        print(f"Created fallback gradient: {output_path}")
        return output_path

    except ImportError:
        print("PIL not available for fallback generation")
        return None


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate hero images for Lemmy's Mic blog posts"
    )
    parser.add_argument("title", nargs="?", help="Post title")
    parser.add_argument("scene", nargs="?", help="Scene description for the image")
    parser.add_argument("--slug", help="URL slug (auto-generated from title if not provided)")
    parser.add_argument("--aspect", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument("--template", "-t", help="Use a template (e.g., indie-games, ebikes, punk-music, tech)")
    parser.add_argument("--list-templates", action="store_true", help="List available templates")
    parser.add_argument("--dry-run", action="store_true", help="Create workflow only, don't generate image")

    args = parser.parse_args()

    # Handle --list-templates
    if args.list_templates:
        templates = list_templates()
        if not templates:
            print("No templates found in workflows/templates/")
            return
        print("Available templates:\n")
        for t in templates:
            print(f"  {t['name']}")
            print(f"    {t['description']}\n")
        return

    # Validate required args
    if not args.title or not args.scene:
        parser.error("title and scene are required (unless using --list-templates)")

    slug = args.slug or slugify(args.title)

    # Step 1: Create and save workflow (from template or scratch)
    print("=" * 60)
    print("Step 1: Creating workflow file")
    print("=" * 60)

    if args.template:
        print(f"Using template: {args.template}")
        template = load_template(args.template)
        workflow = create_workflow_from_template(
            template=template,
            title=args.title,
            scene=args.scene,
            slug=slug
        )
    else:
        workflow = create_workflow(
            title=args.title,
            scene=args.scene,
            slug=slug,
            aspect_ratio=args.aspect
        )

    workflow_path = save_workflow(workflow, slug)

    print(f"\nFlowBoard file: {workflow_path}")
    print("You can open this in FlowBoard UI to inspect or edit before regenerating.")

    if args.dry_run:
        print("\n[Dry run - skipping image generation]")
        prompt, _ = build_prompt_from_workflow(workflow)
        print(f"\nPrompt that would be used:\n{prompt}")
        return

    # Step 2: Generate image from workflow
    print("\n" + "=" * 60)
    print("Step 2: Generating image from workflow")
    print("=" * 60)

    try:
        api_key = get_api_key()
        image_bytes = generate_image_from_workflow(workflow, api_key)
        output_path = save_image(image_bytes, slug)

        print("\n" + "=" * 60)
        print("Success!")
        print("=" * 60)
        print(f"Workflow: {workflow_path}")
        print(f"Image:    {output_path}")
        print(f'\nAdd to post frontmatter: image: "/images/hero-{slug}.png"')

    except Exception as e:
        print(f"\nError generating image: {e}", file=sys.stderr)
        print("Creating fallback gradient...", file=sys.stderr)

        fallback_path = create_gradient_fallback(slug)
        if fallback_path:
            print(f"\nFallback created: {fallback_path}")
            print(f"Workflow saved: {workflow_path}")
            print("\nYou can edit the workflow in FlowBoard and regenerate manually.")

        sys.exit(1)


if __name__ == "__main__":
    main()
