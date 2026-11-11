"""Konsolga salom va dastur versiyasini chiqaradi."""

from pathlib import Path


def read_version() -> str:
    """Versiyani `VERSION` faylidan o'qiydi (reliz skripti shu faylni yangilaydi)."""
    try:
        return Path(__file__).with_name("VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "0.0.0"


def main() -> None:
    print("Hello, World!")
    print(f"Versiya: v{read_version()}")


if __name__ == "__main__":
    main()
