from typing import Dict, List, Any
import pandas as pd
import json
from datetime import datetime

def create_dataframe(tweets: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert tweets list to pandas DataFrame
    """
    return pd.DataFrame(tweets)

def export_to_csv(df: pd.DataFrame, filename: str) -> str:
    """
    Export DataFrame to CSV
    """
    return df.to_csv(index=False)

def export_to_json(tweets: List[Dict[str, Any]]) -> str:
    """
    Export tweets to JSON
    """
    return json.dumps(tweets, default=str)