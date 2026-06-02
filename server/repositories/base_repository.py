import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

class CSVRepository:
    """Classe base astratta per l'accesso ai file CSV tramite Pandas."""
    def __init__(self, filename: str, columns: list[str]):
        self.path = DATA_DIR / filename
        self.columns = columns
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            pd.DataFrame(columns=self.columns).to_csv(self.path, index=False)

    def read(self) -> pd.DataFrame:
        if not self.path.exists():
            return pd.DataFrame(columns=self.columns)
        df = pd.read_csv(self.path, dtype=str).fillna("")
        for column in self.columns:
            if column not in df.columns:
                df[column] = ""
        return df[self.columns].copy()

    def write(self, df: pd.DataFrame) -> None:
        normalized = df.copy().fillna("")
        for column in self.columns:
            if column not in normalized.columns:
                normalized[column] = ""
        normalized[self.columns].to_csv(self.path, index=False)
        
    def get_next_id(self) -> int:
        df = self.read()
        if df.empty or "id" not in df.columns:
            return 1
        try:
            max_id = pd.to_numeric(df["id"]).max()
            return int(max_id) + 1 if pd.notna(max_id) else 1
        except Exception:
            return 1
