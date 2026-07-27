from __future__ import annotations

import sys


def main() -> int:
    try:
        from demucs.separate import main as demucs_main
        result = demucs_main()
        return int(result or 0)
    except Exception as exc:
        print(f"Demucs failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
