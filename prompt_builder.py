from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence


P2P_FORMAT_HINTS = [
    "UPI/DR/<upi>/<desc>",
    "UPI/CR/<upi>/<desc>",
    "IMPS/<name>/<ref>",
    "NEFT/<name>/<bank>/<ref>",
]

MERCHANT_FORMAT_HINTS = [
    "UPI/DR/<merchant>/<order_or_ref>",
    "POS/<merchant>/<txn_or_ref>",
    "UPI/DR/<merchant>/<short_desc>/<ref>",
]

COMMON_UPI_HANDLES = ["okaxis", "oksbi", "okhdfcbank", "ybl", "ibl", "paytm", "upi"]

INDIAN_NAMES = [
    "Rahul",
    "Priya",
    "Ankit",
    "Sneha",
    "Apoorva",
    "Mahendra",
    "Raseel",
    "Yash",
    "Daulat",
    "Kiran",
    "Saurabh",
    "Neha",
    "Vivek",
    "Pooja",
    "Rohit",
    "Amit",
    "Nikhil",
    "Isha",
]

MERCHANTS = [
    "Swiggy",
    "Zomato",
    "Ola",
    "Uber",
    "Amazon",
    "Flipkart",
    "Meesho",
    "JioMart",
    "DMart",
    "IRCTC",
    "Myntra",
    "BookMyShow",
    "BigBasket",
]

NOISE_TOKENS = [
    "TRF",
    "TXN",
    "REF",
    "PMT",
    "PAY",
    "PAID VIA",
    "PAYMENT",
    "UPI TRAN",
    "EXPRESS",
    "ONLY RS",
]


@dataclass(frozen=True)
class PromptConfig:
    few_shot_min: int = 3
    few_shot_max: int = 6


class PromptBuilder:
    def __init__(self, real_examples: Sequence[str], config: PromptConfig | None = None):
        self.real_examples = [e.strip() for e in real_examples if e and e.strip()]
        if len(self.real_examples) < 5:
            raise ValueError("Need at least 5 real examples for style reference")
        self.config = config or PromptConfig()

    def build(self, txn_type: str) -> str:
        txn_type = txn_type.upper().strip()
        if txn_type not in {"P2P", "MERCHANT"}:
            raise ValueError("txn_type must be P2P or MERCHANT")

        k = random.randint(self.config.few_shot_min, self.config.few_shot_max)
        examples = random.sample(self.real_examples, k=k)

        fmt_hint = random.choice(P2P_FORMAT_HINTS if txn_type == "P2P" else MERCHANT_FORMAT_HINTS)
        noise = ", ".join(random.sample(NOISE_TOKENS, k=random.randint(2, 5)))
        upi_hint = f"{random.choice(INDIAN_NAMES).lower()}{random.randint(10,9999)}@{random.choice(COMMON_UPI_HANDLES)}"
        merchant_hint = random.choice(MERCHANTS)

        extra_constraints = []
        extra_constraints.append(f"- Suggested format hint: {fmt_hint}")
        extra_constraints.append("- Output must be a single line (no quotes, no bullets).")
        extra_constraints.append("- Keep it realistic for Indian banking SMS/statement narration.")
        extra_constraints.append("- Add small noise: mixed casing, truncation, extra slashes/spaces, abbreviations.")
        extra_constraints.append(f"- Sprinkle abbreviations like: {noise}")
        if txn_type == "P2P":
            extra_constraints.append(f"- Use realistic Indian person name/UPI handle (e.g. {upi_hint}).")
        else:
            extra_constraints.append(f"- Use realistic Indian merchant brand (e.g. {merchant_hint}).")

        few_shot = "\n".join(f"- {e}" for e in examples)

        return (
            "You are generating a single Indian bank transaction narration.\n\n"
            "Based on the examples below, generate ONE highly realistic transaction narration.\n\n"
            f"Constraints:\n"
            f"- Type: {txn_type}\n"
            "- Follow Indian banking formats (UPI/IMPS/NEFT/RTGS/POS)\n"
            "- Use realistic names, UPI IDs, merchants\n"
            "- Avoid repetition and templates\n"
            + "\n".join(extra_constraints)
            + "\n\n"
            "Return ONLY the narration string. No JSON. No explanation.\n\n"
            "Examples:\n"
            f"{few_shot}\n"
        )


def load_examples_from_csv_rows(rows: List[dict]) -> List[str]:
    # Expected columns: Category, Narration (as in provided transactions.csv)
    out: List[str] = []
    for r in rows:
        val = (r.get("Narration") or "").strip()
        if val:
            out.append(val)
    return out

