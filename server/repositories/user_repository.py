import pandas as pd
from typing import Optional
from server.repositories.base_repository import CSVRepository

class UserRepository(CSVRepository):
    def __init__(self) -> None:
        super().__init__(
            "utenti.csv",
            ["id", "nome", "cognome", "email", "password", "ruolo", "livello_accesso", "stato_account", "ultimo_accesso", "saldo_punti", "piatti_preferiti"],
        )

    def get_all(self) -> list[dict]:
        df = self.read()
        return df.to_dict("records")

    def get_by_id(self, user_id: str) -> Optional[dict]:
        df = self.read()
        mask = df["id"].astype(str) == user_id
        matches = df[mask]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()

    def get_by_email(self, email: str) -> Optional[dict]:
        df = self.read()
        mask = df["email"].str.lower() == email.strip().lower()
        matches = df[mask]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()

    def authenticate(self, email: str, password: str) -> Optional[dict]:
        user = self.get_by_email(email)
        if user and user.get("password") == password:
            return user
        return None

    def create(self, user_data: dict) -> dict:
        df = self.read()
        if not df.empty and (df["email"].str.lower() == user_data.get("email", "").lower()).any():
            raise ValueError("Email già registrata. Inserisci una diversa email o effettua il login.")
            
        user_id = self.get_next_id()
        user_data["id"] = user_id
        
        # Ensure all columns are present
        record = {col: user_data.get(col, "") for col in self.columns}
        
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        self.write(df)
        return record

    def update(self, user_id: str, update_data: dict) -> bool:
        df = self.read()
        mask = df["id"].astype(str) == user_id
        if not mask.any():
            return False
            
        idx = df[mask].index[0]
        for key, value in update_data.items():
            if key in df.columns:
                df.at[idx, key] = value
                
        self.write(df)
        return True

    def delete(self, user_id: str) -> bool:
        df = self.read()
        mask = df["id"].astype(str) == user_id
        if not mask.any():
            return False
            
        df = df[~mask]
        self.write(df)
        return True
