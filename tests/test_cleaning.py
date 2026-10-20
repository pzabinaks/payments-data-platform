import pandas as pd
from payments_data_platform.cleaning import clean_currency, clean_payments, clean_status,fill_unknown_customer



def test_clean_currency_strips_and_uppercases():
    df = pd.DataFrame({"currency": [" EUR", "eur", "GBP"]})
    result = clean_currency(df)
    assert list(result["currency"]) == ["EUR", "EUR", "GBP"]

def test_clean_payments_end_to_end():
    raw = pd.DataFrame({
        "Payment ID": ["PAY1", "PAY2", "PAY2"],                 # PAY2 is an exact duplicate
        " Customer ": ["C1", None, None],
        "Merchant":   ["Shop", "Shop", "Shop"],
        "Amount":     ["75,50", "10.00", "10.00"],
        "Currency":   [" EUR", "gbp", "gbp"],
        "Status":     ["paid ", "FAILED", "FAILED"],
        "Created At": ["2026-08-01 16:19:49", "07.09.2026", "07.09.2026"],
    })
    df = clean_payments(raw)

    assert len(df) == 2
    assert list(df.columns) == ["payment_id", "customer_id", "merchant", "amount",
                                "currency", "status", "created_at"]
    assert df["created_at"].dtype.kind == "M"       # "M" = datetime type
    assert df.loc[0, "amount"] == 75.5
 
    assert df.loc[1, "customer_id"] == "UNKNOWN"
    assert df.loc[0, "created_at"] == pd.Timestamp("2026-08-01 16:19:49")   # 1 August, not 8 January
    assert df.loc[1, "created_at"] == pd.Timestamp("2026-09-07")            # 7 September

def test_clean_status():
    raw = pd.DataFrame({
        "Payment ID": ["PAY1", "PAY2", "PAY2"],                 # PAY2 is an exact duplicate
        " Customer ": ["C1", None, None],
        "Merchant":   ["Shop", "Shop", "Shop"],
        "Amount":     ["75,50", "10.00", "10.00"],
        "Currency":   [" EUR", "gbp", "gbp"],
        "Status":     ["paid ", "FAILED", "FAILED"],
        "Created At": ["2026-08-01 16:19:49", "07.09.2026", "07.09.2026"],
    })   
    df = clean_status(raw)    
    assert df.loc[1, "Status"] == "paid"

