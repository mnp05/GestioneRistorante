import pandas as pd
from typing import Optional
from server.repositories.base_repository import CSVRepository

class TableRepository(CSVRepository):
    def __init__(self) -> None:
        super().__init__(
            "tavoli.csv",
            ["numero", "capienza", "coord_x", "coord_y", "stato"],
        )

    def get_all(self) -> list[dict]:
        return self.read().to_dict("records")

    def get_by_numero(self, numero: str) -> Optional[dict]:
        df = self.read()
        mask = df["numero"].astype(str) == numero
        if mask.any():
            return df[mask].iloc[0].to_dict()
        return None

    def create_or_update(self, table_data: dict) -> dict:
        df = self.read()
        numero = str(table_data.get("numero", ""))
        record = {col: table_data.get(col, "") for col in self.columns}

        mask = df["numero"].astype(str) == numero
        if mask.any():
            idx = df[mask].index[0]
            for col in self.columns:
                df.at[idx, col] = record[col]
        else:
            df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)

        self.write(df)
        return record

    def update_stato(self, numero: str, nuovo_stato: str) -> bool:
        """Aggiorna solo lo stato di un tavolo esistente, preservando gli altri campi."""
        df = self.read()
        mask = df["numero"].astype(str) == numero
        if not mask.any():
            return False
        idx = df[mask].index[0]
        df.at[idx, "stato"] = nuovo_stato
        self.write(df)
        return True

    def delete(self, numero: str) -> bool:
        df = self.read()
        mask = df["numero"].astype(str) == numero
        if not mask.any():
            return False
        df = df[~mask]
        self.write(df)
        return True
