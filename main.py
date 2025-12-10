import sys
from pathlib import Path
from app import app


def _maybe_load_dotenv() -> None:
    """try loading env vars from the file (used in development)"""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    if Path(".env").exists():
        load_dotenv(override=False)


def main():
    """ENTRYPOINT"""
    _maybe_load_dotenv()

    from settings import Settings

    sys.exit(app.run_notifier(Settings.from_env()))


if __name__ == "__main__":
    main()
