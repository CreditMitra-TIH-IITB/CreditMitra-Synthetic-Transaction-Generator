from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from generator import run_generator


def _configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate synthetic Indian bank transaction narrations.")
    p.add_argument("--input", default="transactions.csv", help="CSV with real narration examples (Category,Narration).")
    p.add_argument("--total", type=int, default=int(os.getenv("TARGET_TOTAL", "10000")), help="Target total narrations.")
    p.add_argument("--output-dir", default=os.getenv("OUTPUT_DIR", "data"), help="Output directory.")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    load_dotenv(override=False)
    _configure_logging()

    args = parse_args(argv)
    try:
        asyncio.run(run_generator(input_csv=args.input, total=args.total, output_dir=args.output_dir))
    except KeyboardInterrupt:
        logging.getLogger("main").warning("Interrupted by user; safe to resume later.")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

