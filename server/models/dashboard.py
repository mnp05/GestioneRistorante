import pandas as pd
from typing import Optional
from server.models.base_repository import CSVRepository

class DashboardRepository(CSVRepository):
    def __init__(self) -> None:
        super().__init__(
            "dashboard.csv",
            ["id", "utente_id", "testo", "timestamp"],
        )

    def get_all(self) -> list[dict]:
        return self.read().to_dict("records")

    def get_by_id(self, msg_id: str) -> Optional[dict]:
        df = self.read()
        mask = df["id"].astype(str) == msg_id
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

    def update(self, msg_id: str, data: dict) -> bool:
        df = self.read()
        mask = df["id"].astype(str) == msg_id
        if not mask.any():
            return False
        idx = df[mask].index[0]
        for key, value in data.items():
            if key in df.columns:
                df.at[idx, key] = value
        self.write(df)
        return True

    def delete(self, msg_id: str) -> bool:
        df = self.read()
        mask = df["id"].astype(str) == msg_id
        if not mask.any():
            return False
        df = df[~mask]
        self.write(df)
        return True
