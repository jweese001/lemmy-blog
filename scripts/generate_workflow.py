#!/home/lemmy/lemmy-blog/.venv/bin/python
"""
Generate FlowBoard workflow JSON files for blog hero images.

Creates workflow files that can be:
1. Loaded in FlowBoard UI for manual editing/generation
2. Used programmatically to generate images

Usage:
    python generate_workflow.py "Post Title" "Scene description" --slug my-post
    python generate_workflow.py "Post Title" "Scene description" --model mock  # Testing

Output:
    workflows/blog-{slug}.json
"""

import argparse
import json
import re
import time
from pathlib import Path

# w33s3 style - consistent dark aesthetic
W33S3_STYLE = {
    "name": "w33s3 Dark",
    "description": "Dark, moody atmosphere with high contrast lighting. Cinematic composition with neon accent colors against deep blacks. Professional photography feel, dramatic shadows, rich color depth. Modern minimalist aesthetic."
}

# FlowBoard workflow root
WORKFLOW_DIR = Path(__file__).parent.parent / "workflows"


def slugify(title: str) -> str:
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def create_workflow(
    title: str,
    scene: str,
    slug: str,
    model: str = "gemini-flash",
    aspect_ratio: str = "16:9"
) -> dict:
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
                        "model": model,
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

    print(f"Created workflow: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Generate FlowBoard workflow for blog hero image"
    )
    parser.add_argument("title", help="Post title")
    parser.add_argument("scene", help="Scene description for the image")
    parser.add_argument("--slug", help="URL slug (auto-generated if not provided)")
    parser.add_argument(
        "--model",
        default="gemini-flash",
        choices=["mock", "gemini-flash", "gemini-pro", "flux-schnell", "flux-dev"],
        help="Image generation model (default: gemini-flash, use 'mock' for testing)"
    )
    parser.add_argument(
        "--aspect",
        default="16:9",
        choices=["1:1", "16:9", "9:16", "2:3", "3:2"],
        help="Aspect ratio (default: 16:9)"
    )

    args = parser.parse_args()

    slug = args.slug or slugify(args.title)

    workflow = create_workflow(
        title=args.title,
        scene=args.scene,
        slug=slug,
        model=args.model,
        aspect_ratio=args.aspect
    )

    filepath = save_workflow(workflow, slug)

    print(f"\nTo use this workflow:")
    print(f"1. Open FlowBoard: cd ~/claude-code-telegram/claude-code-telegram/flow-board/client && npm run dev")
    print(f"2. Load the workflow file: {filepath}")
    print(f"3. Click Generate on the Output node")
    print(f"4. Save the image to: ~/lemmy-blog/static/images/hero-{slug}.png")

    if args.model == "mock":
        print(f"\nNote: Using 'mock' model - will generate random test images")


if __name__ == "__main__":
    main()
