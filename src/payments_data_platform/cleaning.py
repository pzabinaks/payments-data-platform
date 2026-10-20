"""Cleaning rules for the raw payments export."""
import pandas as pd

def clean_column_names(df):
    """Clean column names. Replace space with _"""
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df.rename(columns={"customer": "customer_id"})

def clean_amount(df):
    """Convert to float. Replace , with ."""
    df["amount"] = df["amount"].str.replace(",", ".").astype(float)
    return df

def clean_currency(df):
    """Truncate spaces for currency"""
    df["currency"] = df["currency"].str.upper().str.strip().astype("category")
    return df

def clean_status(df):
    """Truncate spaces for status"""
    df["status"] = df["status"].str.strip().str.lower().astype("category")
    return df

def clean_dates(df):
    """Convert correct date formats (iso,eu)"""
    iso = pd.to_datetime(df["created_at"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    eu  = pd.to_datetime(df["created_at"], format="%d.%m.%Y", errors="coerce")
    df["created_at"] = iso.fillna(eu)
    return df

def remove_duplicates(df):
    """Removes duplicates"""
    return df.drop_duplicates()

def fill_unknown_customer(df):
    """Fill non defined customer_ids with phrase UNKNOWN"""
    df["customer_id"] = df["customer_id"].fillna("UNKNOWN")
    return df

def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all cleaning steps in the correct order and return a clean DataFrame."""
    df = clean_column_names(df)
    df = clean_amount(df)
    df = clean_currency(df)
    df = clean_status(df)
    #df = clean_dates(df)
    df = remove_duplicates(df)
    df = fill_unknown_customer(df)

    return df