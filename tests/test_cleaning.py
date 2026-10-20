import pandas as pd
from payments_data_platform.cleaning import clean_currency, clean_payments, clean_status,fill_unknown_customer,clean_column_names,remove_duplicates,clean_dates,clean_amount
from datetime import datetime

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
        "Status":     ["paid ", "FAILED", "FAILED"],
    })   
    df = clean_column_names(raw)
    df = clean_status(df)    
    assert list(df["status"]) == ["paid", "failed", "failed"]

def test_fill_unknown_customer():
    raw = pd.DataFrame({
        " Customer ": ["C1", None, None],
    })   
    df = clean_column_names(raw)
    df = fill_unknown_customer(df)    
    assert df.loc[2, "customer_id"] == "UNKNOWN"

def test_remove_duplicates():
    raw = pd.DataFrame({
        "Payment ID": ["PAY1", "PAY2", "PAY2"],                 # PAY2 is an exact duplicate
        " Customer ": ["C1", None, None],
        "Merchant":   ["Shop", "Shop", "Shop"],
        "Amount":     ["75,50", "10.00", "10.00"],
        "Currency":   [" EUR", "gbp", "gbp"],
        "Status":     ["paid ", "FAILED", "FAILED"],
        "Created At": ["2026-08-01 16:19:49", "07.09.2026", "07.09.2026"],
    })   
    df = clean_column_names(raw)
    df = remove_duplicates(df)    
    assert 2 not in df.index



def test_clean_dates_parses_both_formats():
    df = pd.DataFrame({"created_at": ["2026-08-01 16:19:49", "07.09.2026"]})
    result = clean_dates(df)
    assert result.loc[0, "created_at"] == pd.Timestamp("2026-08-01 16:19:49")   # 1 August, not 8 January
    assert result.loc[1, "created_at"] == pd.Timestamp("2026-09-07")            # 7 September

def test_clean_amount():
    
    raw = pd.DataFrame({
        "amount":     ["50,01", "50.01", "1000"],
    })  
    
    result = clean_amount(raw)
    
    assert result.loc[0, "amount"] == 50.01
    assert result.loc[1, "amount"] == 50.01
    assert result.loc[2, "amount"] == 1000