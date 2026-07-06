

import json
from pathlib import Path
from typing import Dict, Optional

# -- Core Shariah constants (shared by every module) -------------------------
ZAKAT_RATE: float = 0.025  # 2.5%, agreed upon by the majority of scholars
HAUL_MONTHS: int = 12      # one full (lunar) year holding period
STATE_NAME: str = "Selangor"

# Asnaf income-ratio thresholds, relative to Had Kifayah. Per LZS's published
# criteria: Fakir = income covers less than 50% of Had Kifayah; Miskin =
# income covers 50%-99% of Had Kifayah (still short of full sufficiency).
FAKIR_INCOME_RATIO: float = 0.50
MISKIN_INCOME_RATIO: float = 1.00

_DATA_DIR = Path(__file__).parent


def _load_json(filename: str) -> Dict:
    """Read one reference-data file from the database/ folder."""
    with open(_DATA_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def get_nisab_config() -> Dict:
    """Load the current gold/silver price and nisab configuration."""
    return _load_json("nisab.json")


def get_had_kifayah_config() -> Dict:
    """Load the Had Kifayah (basic subsistence) rate configuration."""
    return _load_json("had_kifayah.json")


def calculate_nisab_value(gold_price_per_gram: Optional[float] = None) -> float:
    """
    Compute the current Ringgit nisab value (85 grams of gold).

    Accepts an optional price override so callers (or unit tests) can
    simulate different market conditions without editing the JSON file.
    """
    config = get_nisab_config()
    price = gold_price_per_gram if gold_price_per_gram is not None else config["gold_price_per_gram_24k"]
    return round(config["nisab_gold_grams"] * price, 2)


def calculate_had_kifayah(num_adults: int, num_children: int) -> float:
    """
    Compute the monthly Had Kifayah (minimum sufficiency) threshold for a
    household, using the base-adult + additional-adult + per-child formula.

    See had_kifayah.json for an important note on the provenance of these
    figures -- they are reference placeholders, not an official LZS table.
    """
    config = get_had_kifayah_config()
    adults = max(num_adults, 1)  # every household has at least the applicant

    total = config["base_amount_first_adult"]
    total += config["additional_adult"] * max(adults - 1, 0)
    total += config["child_amount"] * max(num_children, 0)
    return round(total, 2)
