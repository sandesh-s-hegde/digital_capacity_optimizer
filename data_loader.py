"""
data_loader.py
Handles ingestion of raw usage logs and cleaning for analysis.
"""
import pandas as pd


def load_data(filepath: str) -> pd.DataFrame:
    """
    Reads CSV data and returns a cleaned Pandas DataFrame.

    Args:
        filepath (str): Path to the CSV file (e.g., 'mock_data.csv')

    Returns:
        pd.DataFrame: The usage data. Returns empty DataFrame if file missing.
    """
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Successfully loaded {len(df)} records from {filepath}.")
        return df
    except FileNotFoundError:
        print(f"❌ Error: File '{filepath}' not found. Please check the path.")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return pd.DataFrame()