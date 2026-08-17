#!/usr/bin/env python3
"""Verify that the generated WASM bindings export the character-positioning APIs."""

import argparse
import sys
from pathlib import Path

REQUIRED_FUNCTIONS = [
    "_FPDFText_GetCharBox",
    "_FPDFText_GetLooseCharBox",
    "_FPDFText_GetCharOrigin",
    "_FPDFText_GetFontSize",
    "_FPDFText_GetFontInfo",
    "_FPDFText_GetCharAngle",
    "_FPDFText_GetCharIndexAtPos",
    "_FPDFText_GetTextRenderMode",
    "_FPDFText_GetMatrix",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify generated WASM bindings expose the character-positioning APIs"
    )
    parser.add_argument("paths", nargs="+", help="One or more generated JS files to inspect")
    args = parser.parse_args()

    missing = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.exists():
            missing.append(f"{path}: file not found")
            continue

        content = path.read_text(encoding="utf-8", errors="ignore")
        for func_name in REQUIRED_FUNCTIONS:
            if func_name not in content:
                missing.append(f"{path}: missing {func_name}")

    if missing:
        print("WASM export verification failed:")
        for item in missing:
            print(f" - {item}")
        return 1

    print("WASM character-positioning exports verified:")
    for func_name in REQUIRED_FUNCTIONS:
        print(f" - {func_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
