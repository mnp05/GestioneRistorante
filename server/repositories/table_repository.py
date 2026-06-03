import pandas as pd
from typing import Optional
from server.repositories.base_repository import CSVRepository

class TableRepository(CSVRepository):
    def __init__(self) -> None:
        super().__init__(
            "tavoli.csv",
            ["numero", "capienza", "coord_x", "coord_y", "stato", "data"],
        )

    def _ensure_layout_cloned(self, target_date: str, df: pd.DataFrame) -> pd.DataFrame:
        if target_date == "DEFAULT":
            return df
        mask = df["data"].astype(str) == target_date
        if not mask.any():
            mask_default = df["data"].astype(str) == "DEFAULT"
            if mask_default.any():
                default_tables = df[mask_default].copy()
                default_tables["data"] = target_date
                df = pd.concat([df, default_tables], ignore_index=True)
        return df

    def get_for_date(self, target_date: str) -> list[dict]:
        df = self.read()
        mask_date = df["data"].astype(str) == target_date
        if mask_date.any():
            return df[mask_date].to_dict("records")
        mask_default = df["data"].astype(str) == "DEFAULT"
        if mask_default.any():
            return df[mask_default].to_dict("records")
        return []

    def get_all(self) -> list[dict]:
        return self.read().to_dict("records")

    def get_by_numero(self, numero: str, target_date: str = "DEFAULT") -> Optional[dict]:
        df = self.read()
        mask = (df["numero"].astype(str) == numero) & (df["data"].astype(str) == target_date)
        if mask.any():
            return df[mask].iloc[0].to_dict()
        return None

    def create_or_update(self, table_data: dict) -> dict:
        df = self.read()
        if "data" not in df.columns:
            df["data"] = "DEFAULT"
            
        target_date = str(table_data.get("data", "DEFAULT"))
        if not target_date:
            target_date = "DEFAULT"
            
        df = self._ensure_layout_cloned(target_date, df)
        
        numero = str(table_data.get("numero", ""))
        record = {col: table_data.get(col, "") for col in self.columns}
        record["data"] = target_date

        mask = (df["numero"].astype(str) == numero) & (df["data"].astype(str) == target_date)
        if mask.any():
            idx = df[mask].index[0]
            for col in self.columns:
                df.at[idx, col] = record[col]
        else:
            df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)

        self.write(df)
        return record

    def update_stato(self, numero: str, nuovo_stato: str, target_date: str = "DEFAULT") -> bool:
        """Aggiorna solo lo stato di un tavolo esistente, preservando gli altri campi."""
        df = self.read()
        df = self._ensure_layout_cloned(target_date, df)
        mask = (df["numero"].astype(str) == numero) & (df["data"].astype(str) == target_date)
        if not mask.any():
            return False
        idx = df[mask].index[0]
        df.at[idx, "stato"] = nuovo_stato
        self.write(df)
        return True

    def delete(self, numero: str, target_date: str = "DEFAULT") -> bool:
        df = self.read()
        df = self._ensure_layout_cloned(target_date, df)
        mask = (df["numero"].astype(str) == numero) & (df["data"].astype(str) == target_date)
        if not mask.any():
            return False
        df = df[~mask]
        self.write(df)
        return True
