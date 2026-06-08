import pandas as pd
from typing import Optional
from server.models.base_repository import CSVRepository

class MenuRepository(CSVRepository):
    def __init__(self) -> None:
        super().__init__(
            "menu.csv",
            ["id", "nome", "descrizione", "prezzo", "allergeni", "categoria_id", "foto_path", "attivo"],
        )

    def get_all(self) -> list[dict]:
        df = self.read()
        return df.to_dict("records")

    def get_by_id(self, item_id: str) -> Optional[dict]:
        df = self.read()
        mask = df["id"].astype(str) == item_id
        if mask.any():
            return df[mask].iloc[0].to_dict()
        return None

    def create(self, data: dict) -> dict:
        df = self.read()
        data["id"] = self.get_next_id()
        record = {col: data.get(col, "") for col in self.columns}
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        self.write(df)
        return record

    def update(self, item_id: str, data: dict) -> bool:
        df = self.read()
        mask = df["id"].astype(str) == item_id
        if not mask.any():
            return False
        idx = df[mask].index[0]
        for key, value in data.items():
            if key in df.columns:
                df.at[idx, key] = value
        self.write(df)
        return True

    def delete(self, item_id: str) -> bool:
        df = self.read()
        mask = df["id"].astype(str) == item_id
        if not mask.any():
            return False
        df = df[~mask]
        self.write(df)
        return True
