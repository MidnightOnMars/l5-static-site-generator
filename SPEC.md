# L5: Static Site Generator

## Overview

A minimal static site generator that reads Markdown files from a content directory, applies Jinja2 templates, and writes HTML to an output directory. Configuration via a single YAML file. Automatic navigation from directory structure. Syntax highlighting for fenced code blocks.

**Target:** Multi-file Python package (`ssg/`), clean module separation, ~500-800 lines total across all modules.

**Dependencies (allowed):** `jinja2`, `pyyaml`, `pygments`, `markdown`. No other third-party libraries.

**Quality bar:** Architecture should land between makesite's minimalism (~200 lines, everything in one file) and Pelican's over-engineering. Clear separation of concerns. Each module has one job.

## Package Structure

```
ssg/
    __init__.py          # Public API: build(), clean()
    config.py            # Load and validate site configuration
    content.py           # Load Markdown files, parse front matter
    renderer.py          # Jinja2 template rendering + Markdown conversion
    navigation.py        # Build nav tree from content directory structure
    server.py            # Development server with file-watching rebuild
    cli.py               # Command-line interface
```

## Behavioral Specification

### Configuration (`config.py`)

Configuration is loaded from a YAML file (default: `site.yaml` in project root).

| Key | Type | Default | Description |
|---|---|---|---|
| `title` | string | `"My Site"` | Site-wide title |
| `base_url` | string | `"/"` | Base URL for links and assets |
| `content_dir` | string | `"content"` | Path to Markdown content |
| `output_dir` | string | `"output"` | Path for generated HTML |
| `template_dir` | string | `"templates"` | Path to Jinja2 templates |
| `default_template` | string | `"page.html"` | Default template for pages |
| `highlight_style` | string | `"monokai"` | Pygments style for code blocks |

The config loader:
1. Reads YAML file at given path
2. Merges with defaults (config values override defaults)
3. Returns a config object/dict with all keys guaranteed present
4. If the YAML file does not exist, uses all defaults (no error)
5. If the YAML file exists but is malformed, raises `ConfigError` with a clear message

### Content Loading (`content.py`)

Content files are Markdown files (`.md`) in the content directory, optionally nested in subdirectories.

**Front matter** is YAML enclosed in `---` delimiters at the top of the file:

```markdown
---
title: My Page Title
template: custom.html
date: 2025-01-15
draft: true
---

Page content in Markdown here.
```

Front matter fields:
- `title` (string): Page title. If absent, derive from filename (e.g., `about-us.md` -> `"About Us"`).
- `template` (string): Override the default template for this page.
- `date` (string or date): Publication date. Optional.
- `draft` (bool): If `true`, page is excluded from build output. Default: `false`.
- Any other keys are passed through as template variables.

The content loader:
1. Walks `content_dir` recursively
2. Finds all `.md` files
3. Parses front matter (YAML between `---` lines) and body separately
4. Returns a list of page objects, each with: `title`, `template`, `date`, `draft`, `content` (raw markdown body), `slug` (URL path derived from file path), `source_path` (original file path), plus any extra front matter keys
5. Files without front matter are valid -- they get default metadata
6. Subdirectory structure maps to URL structure: `content/blog/post.md` -> slug `blog/post`
7. A file named `index.md` in any directory gets the directory's slug (e.g., `content/blog/index.md` -> slug `blog/`)
8. Draft pages are loaded but flagged; the build step excludes them

### Navigation (`navigation.py`)

Build a navigation tree from the content directory structure:

1. Each directory becomes a navigation section
2. Each non-draft page becomes a navigation item
3. Items within a section are sorted alphabetically by title
4. Top-level pages appear before sections
5. The nav tree is available in all templates as `nav`

Navigation item structure:
- `title`: Page title
- `url`: Relative URL (from base_url + slug)
- `active`: Whether this is the current page (set during rendering)
- `children`: List of child items (for sections)

### Rendering (`renderer.py`)

The renderer:
1. Converts Markdown body to HTML using the `markdown` library with `fenced_code` and `codehilite` extensions (Pygments integration)
2. Loads Jinja2 templates from `template_dir`
3. Renders each page through its template (per-page `template` front matter key, falling back to `default_template` from config)
4. Template variables available during rendering:
   - `page.title` -- page title
   - `page.content` -- rendered HTML content
   - `page.date` -- publication date
   - `page.slug` -- URL slug
   - `page.url` -- full URL (base_url + slug)
   - `page.*` -- any extra front matter keys
   - `site.title` -- site title from config
   - `site.base_url` -- base URL from config
   - `nav` -- navigation tree
5. Writes rendered HTML to `output_dir`, preserving directory structure
   - `content/about.md` -> `output/about/index.html`
   - `content/blog/post.md` -> `output/blog/post/index.html`
   - `content/index.md` -> `output/index.html`

### Syntax Highlighting

Fenced code blocks with language annotation get Pygments syntax highlighting:

````markdown
```python
def hello():
    print("world")
```
````

The renderer uses `markdown`'s `codehilite` extension with `css_class="highlight"` and the Pygments style from config. The generated HTML includes inline Pygments CSS or class-based highlighting (either approach is acceptable).

### Build Pipeline (`__init__.py`)

The `build()` function orchestrates the full pipeline:
1. Load config
2. Load content (all `.md` files with front matter)
3. Filter out drafts
4. Build navigation tree
5. Render each page through its template
6. Write output files
7. Return a summary: number of pages built, output directory

The `clean()` function:
1. Removes the entire output directory
2. Returns confirmation message

### Development Server (`server.py`)

A simple development server for local preview:
1. Runs `build()` on startup
2. Serves files from `output_dir` using `http.server`
3. Polls `content_dir` and `template_dir` for file changes (mtime-based, every 1 second)
4. On change detected, runs `build()` again and logs what changed
5. Runs on configurable host/port (default: `localhost:8000`)

The server is intentionally simple: polling-based (no `watchdog` dependency), no live reload injection, no WebSocket. Just rebuild and re-serve.

### CLI (`cli.py`)

Command-line interface using `argparse`:

```
usage: python -m ssg [-h] {build,clean,serve} ...

Static Site Generator

commands:
  build     Build the site
  clean     Remove output directory
  serve     Start development server

options:
  -h, --help  show this help message and exit
```

Subcommands:
- `build [-c CONFIG]` -- Build site. Default config: `site.yaml`
- `clean [-c CONFIG]` -- Remove output directory
- `serve [-c CONFIG] [--host HOST] [--port PORT]` -- Start dev server

Exit codes: 0 on success, 1 on error. Errors print to stderr with a clear message (no Python tracebacks for user-facing errors).

## Constraints

- Multi-file package with clear module separation (no monolith)
- Each module under 150 lines (enforces separation of concerns)
- Dependencies limited to: `jinja2`, `pyyaml`, `pygments`, `markdown`
- Tests use temporary directories (no fixtures that require specific filesystem state)
- All public functions have type hints
- Clean error messages for common failures (missing template, malformed config, missing content dir)

## What Success Looks Like

Given a project directory with:
```
site.yaml
content/
    index.md
    about.md
    blog/
        first-post.md
        second-post.md
templates/
    base.html
    page.html
```

Running `python -m ssg build` produces:
```
output/
    index.html
    about/
        index.html
    blog/
        first-post/
            index.html
        second-post/
            index.html
```

Each HTML file is a fully rendered page with navigation, syntax-highlighted code blocks, and proper template inheritance. The code reads like it was written by a developer who has built static site generators before.
