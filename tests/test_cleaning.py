import pandas as pd
from payments_data_platform.cleaning import clean_currency


def test_clean_currency_strips_and_uppercases():
    df = pd.DataFrame({"currency": [" EUR", "eur", "GBP"]})
    result = clean_currency(df)
    assert list(result["currency"]) == ["EUR", "EUR", "GBP"]