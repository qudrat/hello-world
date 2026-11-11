#!/usr/bin/env python3
"""Reliz skripti: versiyani oshiradi, commit qiladi, teg qo'yadi, push qiladi va GitHub release yaratadi.

Ishlatish:
    python release.py patch          # 1.1.0 -> 1.1.1
    python release.py minor          # 1.1.0 -> 1.2.0
    python release.py major          # 1.1.0 -> 2.0.0
    python release.py 1.3.2          # aniq versiya
    python release.py minor --dry-run

Versiya yagona manbasi — `VERSION` fayli. Skript `index.html` dagi
`<span class="version-number">` qiymatini ham shu fayldan yangilaydi.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "VERSION"
INDEX_FILE = ROOT / "index.html"
INDEX_VERSION_RE = re.compile(r'(<span class="version-number">)v?[^<]*(</span>)')
BRANCH = "main"


def fail(message: str) -> None:
    print(f"XATO: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(*args: str, capture: bool = False) -> str:
    print(f"$ {' '.join(args)}")
    result = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=capture,
    )
    if result.returncode != 0:
        if capture and result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        fail(f"buyruq muvaffaqiyatsiz tugadi: {' '.join(args)}")
    return (result.stdout or "").strip() if capture else ""


def read_version() -> str:
    if not VERSION_FILE.is_file():
        fail("VERSION fayli topilmadi")
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def bump(current: str, part: str) -> str:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", current)
    if not match:
        fail(f"VERSION noto'g'ri formatda: {current!r} (kutilgan: 1.2.3)")
    major, minor, patch = (int(x) for x in match.groups())
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if re.fullmatch(r"\d+\.\d+\.\d+", part):
        return part
    fail("versiya qismi noto'g'ri: major | minor | patch | 1.2.3")


def write_version(version: str) -> None:
    VERSION_FILE.write_text(f"{version}\n", encoding="utf-8", newline="\n")


def stamp_index(version: str) -> None:
    html = INDEX_FILE.read_text(encoding="utf-8")
    updated, count = INDEX_VERSION_RE.subn(rf"\g<1>v{version}\g<2>", html)
    if count != 1:
        fail(
            "index.html ichida '<span class=\"version-number\">' topilmadi "
            "yoki bir nechta marta uchradi"
        )
    # Mavjud qator oxirlarini saqlab qolamiz.
    INDEX_FILE.write_text(updated, encoding="utf-8", newline="")


def git_output(*args: str) -> str:
    return run("git", *args, capture=True)


def previous_tag() -> str | None:
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    return result.stdout.strip() or None if result.returncode == 0 else None


def changelog(since: str | None) -> str:
    args = ["log", "--pretty=format:- %s", "--reverse"]
    if since:
        args.append(f"{since}..HEAD")
    entries = git_output(*args).splitlines()
    # Reliz commit'larining o'zi changelog'ga tushmasin.
    entries = [line for line in entries if line.strip() and not line.startswith("- Release v")]
    return "\n".join(entries) or "- O'zgarishlar yo'q"


def main() -> int:
    parser = argparse.ArgumentParser(description="Yangi reliz yaratish")
    parser.add_argument("bump", help="major | minor | patch | 1.2.3")
    parser.add_argument("--dry-run", action="store_true", help="faqat ko'rsatish, o'zgartirmaslik")
    parser.add_argument("--skip-release", action="store_true", help="GitHub release yaratmaslik")
    args = parser.parse_args()

    if shutil.which("git") is None:
        fail("git topilmadi")

    current = read_version()
    version = bump(current, args.bump)
    tag = f"v{version}"

    # --- Oldindan tekshiruvlar (hech narsa o'zgartirilmasdan) ---
    branch = git_output("rev-parse", "--abbrev-ref", "HEAD")
    if branch != BRANCH:
        fail(f"hozirgi branch {branch!r}; reliz faqat {BRANCH!r} da qilinadi")

    dirty = git_output("status", "--porcelain")
    if dirty and not args.dry_run:
        fail("ishchi papka toza emas; avval commit yoki stash qiling:\n" + dirty)

    existing = subprocess.run(
        ["git", "tag", "--list", tag], cwd=ROOT, text=True, capture_output=True
    ).stdout.strip()
    if existing:
        fail(f"{tag} tegi allaqachon mavjud")

    gh = shutil.which("gh")
    if not args.skip_release and not args.dry_run and not gh:
        fail("gh (GitHub CLI) topilmadi; --skip-release bilan qayta urinib ko'ring")

    print(f"\nVersiya: {current} -> {version}  (teg: {tag})")
    if args.dry_run:
        print("Dry-run: hech narsa o'zgartirilmadi.")
        return 0

    # --- Fayllarni yangilash ---
    write_version(version)
    stamp_index(version)

    since = previous_tag()

    run("git", "add", "VERSION", "index.html")
    run("git", "commit", "-m", f"Release {tag}")
    run("git", "tag", "-a", tag, "-m", f"Reliz {tag}")
    run("git", "push", "origin", BRANCH)
    run("git", "push", "origin", tag)

    if not args.skip_release:
        notes = f"Reliz {tag}\n\n{changelog(since)}\n"
        with tempfile.NamedTemporaryFile(
            "w", suffix=".md", delete=False, encoding="utf-8", newline="\n"
        ) as handle:
            handle.write(notes)
            notes_path = handle.name
        try:
            run(gh, "release", "create", tag, "--title", tag, "--notes-file", notes_path)
        finally:
            Path(notes_path).unlink(missing_ok=True)

    print(f"\nTayyor: {tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
