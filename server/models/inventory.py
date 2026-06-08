import pandas as pd
from typing import Optional
from server.models.base_repository import CSVRepository

class InventoryRepository(CSVRepository):
    def __init__(self) -> None:
        super().__init__(
            "inventario.csv",
            ["id", "nome", "descrizione", "quantita_disponibile", "unita_misura", "soglia_minima", "categoria_id", "stato"],
        )

    def get_all(self) -> list[dict]:
        return self.read().to_dict("records")

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

    def get_all_categories(self) -> list[str]:
        df = self.read()
        if df.empty or "categoria_id" not in df.columns:
            return []
        unique_cats = df["categoria_id"].dropna().unique()
        return sorted([str(c).strip() for c in unique_cats if str(c).strip() and str(c).strip() != "Nessuna"])

    def bulk_remove_category(self, nome_categoria: str) -> bool:
        df = self.read()
        if df.empty or "categoria_id" not in df.columns:
            return False
        
        mask = df["categoria_id"].astype(str).str.strip() == nome_categoria.strip()
        if mask.any():
            df.loc[mask, "categoria_id"] = ""
            self.write(df)
        return True
