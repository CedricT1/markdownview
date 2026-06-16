# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Web app to live-preview Markdown and export it to HTML, PDF, and ODT. Flask backend, vanilla-JS frontend, Docker-deployed. UI strings and code comments are in French.

## Commands

```bash
# Local dev server (Flask debug, hot reload, http://localhost:5000)
python run.py

# Production-style run (matches Dockerfile CMD)
gunicorn --bind 0.0.0.0:5000 run:app

# Docker Compose (recommended; serves on host port 5050 -> container 5000)
docker-compose up -d --build
docker-compose down

# Plain Docker (host port 5000)
docker build -t markdownview-app .
docker run -p 5000:5000 markdownview-app
```

There is no test suite, linter, or CI. The two `utils` modules each have an `if __name__ == '__main__'` block usable for manual smoke-testing, e.g. `python -m app.utils.markdown_processor`.

## Architecture

Request flow: browser → Flask route → `app/utils/` module → response.

- **`run.py`** — entry point; builds the app via `create_app()` and exposes module-level `app` (referenced as `run:app` by Gunicorn).
- **`app/__init__.py`** — `create_app()` factory. Routes are registered by calling `routes.init_app(app)` (Blueprints are deliberately *not* used). When adding routes, add them inside `init_app`, not as standalone decorators.
- **`app/routes.py`** — three endpoints:
  - `GET /` renders `templates/index.html`
  - `POST /render` — takes `markdown` form field, returns rendered HTML fragment (used by the live preview)
  - `POST /export/<format_type>` — `format_type` is `html`, `pdf`, or `odt`; returns a downloadable file
- **`app/utils/markdown_processor.py`** — `to_html()` is the single conversion function used by both preview and export. Uses `markdown-it-py` (`commonmark` preset) with `breaks` + `linkify` options, the `table`/`strikethrough` core rules enabled, and `mdit-py-plugins` for footnote/deflist/front_matter. If the source contains a ```` ```mermaid ```` fence, a Mermaid CDN `<script>` is appended to the output HTML so diagrams render client-side.
- **`app/utils/export_service.py`** — wraps `to_html()`:
  - PDF via **WeasyPrint** (wraps the fragment in a full HTML doc, writes to a `BytesIO`)
  - ODT via a **Pandoc** subprocess (`pandoc --from=markdown --to=odt`); failures are caught and the error text is returned *inside* the downloaded file rather than as an HTTP error
- **Frontend** (`app/static/js/main.js`, `templates/index.html`, `static/css/style.css`) — vanilla JS. Posts to `/render` on every `input` event and swaps `innerHTML` of the preview pane. Theme toggle adds/removes `theme-dark` on `<body>` and persists to `localStorage`. Export submits a form whose hidden field is populated with the editor content on submit.

## System dependencies

PDF and ODT export depend on native binaries, not just pip packages: WeasyPrint needs Pango/Cairo/gdk-pixbuf libs, and ODT needs the `pandoc` binary on `PATH`. These are installed in the Dockerfile's final image — `/render` and HTML export work without them, but PDF/ODT will fail outside Docker unless you install them locally.

## Notes

- Markdown is rendered and sent to the browser without sanitization; raw HTML in user input reaches the preview. Keep this in mind before exposing the app publicly.
- The Dockerfile is multi-stage (builder installs pip deps, final image copies site-packages + adds runtime libs) and runs as non-root `appuser`.
