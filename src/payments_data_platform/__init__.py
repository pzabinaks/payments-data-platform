import logging
from pathlib import Path

import pandas as pd

from payments_data_platform.cleaning import clean_payments

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s - %(message)s",
    )
    raw_path = Path("data/raw/payments_raw.csv")
    out_path = Path("data/clean/payments.parquet")

    logger.info("reading %s", raw_path)
    raw = pd.read_csv(raw_path)
    logger.info("rows read: %d", len(raw))

    df = clean_payments(raw)
    logger.info("rows after cleaning: %d (removed %d)", len(df), len(raw) - len(df))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    logger.info("written %s", out_path)
