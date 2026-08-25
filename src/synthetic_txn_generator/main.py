from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from .generator import run_generator
from .labeler import run_labeler


def _configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Synthetic transaction narration pipeline.")
    p.add_argument(
        "--mode",
        choices=["generate", "label"],
        default="generate",
        help="Pipeline mode: 'generate' to create dataset, 'label' to extract payee names.",
    )
    p.add_argument(
        "--input",
        default="transactions.csv",
        help="CSV with real narration examples (Category,Narration) for generation mode.",
    )
    p.add_argument(
        "--total",
        type=int,
        default=int(os.getenv("TARGET_TOTAL", "10000")),
        help="Target total narrations for generation mode.",
    )
    p.add_argument(
        "--output-dir",
        default=os.getenv("OUTPUT_DIR", "data"),
        help="Output directory for all artifacts (output.jsonl, labels.jsonl, checkpoint files).",
    )
    p.add_argument(
        "--output-jsonl",
        default=None,
        help="Optional path to output.jsonl to label (defaults to <output-dir>/output.jsonl).",
    )
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    load_dotenv(override=False)
    _configure_logging()

    args = parse_args(argv)
    try:
        if args.mode == "generate":
            asyncio.run(
                run_generator(
                    input_csv=args.input, total=args.total, output_dir=args.output_dir
                )
            )
        else:
            asyncio.run(
                run_labeler(output_dir=args.output_dir, output_jsonl=args.output_jsonl)
            )
    except KeyboardInterrupt:
        logging.getLogger("main").warning("Interrupted by user; safe to resume later.")
        return 130
    return 0


def entrypoint() -> None:
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
