# AGENTS.md

## Overview
Two independent "Hello, World!" demos: `hello.py` (Python) and `index.html` (static page). There is no package manifest, build step, test suite, linter, or CI — do not add or assume one unless asked.

## Commands
- Python: `python hello.py` (also `py hello.py` on Windows) — prints the greeting and the version from `VERSION`
- HTML: open `index.html` directly in a browser; no server needed
- Release: `python release.py patch|minor|major|X.Y.Z` (see below)
- No test/lint step exists; confirming script output and page rendering is the only check.

## Versioning
- `VERSION` (plain semver, e.g. `1.1.0`) is the single source of truth. `hello.py` reads it at runtime; `index.html` gets it stamped into `<span class="version-number">`.
- `release.py` bumps `VERSION`, updates `index.html`, commits `Release vX.Y.Z`, tags, pushes `main` + tag, and runs `gh release create`. It refuses to run on a dirty tree or off `main`; `--dry-run` previews, `--skip-release` stops before GitHub.
- Never hand-edit version strings in `index.html`; run the script instead so the tag, `VERSION`, and page stay in sync.
- Git tags are `vX.Y.Z` (annotated). Note the historical `v1.0` tag predates semver and has no `VERSION` equivalent.

## Conventions
- `index.html` is a single self-contained file with inline CSS, kept directly openable and deployable to GitHub Pages. Do not split it into external CSS/JS or add a bundler without being asked.
- User-facing text (README, page copy, script messages) is in Uzbek; keep new prose in Uzbek for consistency, though code identifiers stay English.
