import pandas as pd
from typing import Optional
from server.repositories.base_repository import CSVRepository

class PromoRepository:
    def __init__(self) -> None:
        self.buoni_repo = CSVRepository(
            "buoni_regalo.csv",
            ["codice_univoco", "valore", "stato", "id_acquirente", "id_beneficiario", "data_scadenza"]
        )
        self.transazioni_repo = CSVRepository(
            "transazioni.csv",
            ["id", "id_cliente", "punti", "descrizione", "data"]
        )

    # METODI BUONI
    def get_buoni_by_cliente(self, cliente_id: str) -> list[dict]:
        df = self.buoni_repo.read()
        mask = (df["id_acquirente"].astype(str) == str(cliente_id)) | (df["id_beneficiario"].astype(str) == str(cliente_id))
        return df[mask].to_dict("records")

    def get_buono(self, codice: str) -> Optional[dict]:
        df = self.buoni_repo.read()
        mask = df["codice_univoco"].str.lower() == codice.strip().lower()
        if mask.any():
            return df[mask].iloc[0].to_dict()
        return None

    def create_buono(self, data: dict) -> dict:
        df = self.buoni_repo.read()
        record = {col: data.get(col, "") for col in self.buoni_repo.columns}
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        self.buoni_repo.write(df)
        return record

    def update_buono(self, codice: str, data: dict) -> bool:
        df = self.buoni_repo.read()
        mask = df["codice_univoco"].str.lower() == codice.strip().lower()
        if not mask.any():
            return False
        idx = df[mask].index[0]
        for key, value in data.items():
            if key in self.buoni_repo.columns:
                df.at[idx, key] = value
        self.buoni_repo.write(df)
        return True

    # METODI TRANSAZIONI PUNTI
    def get_transazioni(self, cliente_id: str) -> list[dict]:
        df = self.transazioni_repo.read()
        mask = df["id_cliente"].astype(str) == str(cliente_id)
        return df[mask].to_dict("records")

    def create_transazione(self, data: dict) -> dict:
        df = self.transazioni_repo.read()
        data["id"] = self.transazioni_repo.get_next_id()
        record = {col: data.get(col, "") for col in self.transazioni_repo.columns}
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        self.transazioni_repo.write(df)
        return record
