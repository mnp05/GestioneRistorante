from server.repositories.menu_repository import MenuRepository

class MenuController:
    def __init__(self):
        self.menu_repo = MenuRepository()

    def get_menu_attivo(self) -> list[dict]:
        tutti = self.menu_repo.get_all()
        # Restituisce solo i prodotti con attivo=True
        return [p for p in tutti if str(p.get("attivo", "")).lower() in ("true", "1", "t")]

    def get_tutto_il_menu(self) -> list[dict]:
        return self.menu_repo.get_all()

    def aggiungi_piatto(self, dati: dict) -> dict:
        dati["attivo"] = True
        return self.menu_repo.create(dati)

    def modifica_piatto(self, piatto_id: str, nuovi_dati: dict) -> bool:
        return self.menu_repo.update(piatto_id, nuovi_dati)

    def disattiva_piatto(self, piatto_id: str) -> bool:
        return self.menu_repo.update(piatto_id, {"attivo": False})

    def rimuovi_piatto_definitivamente(self, piatto_id: str) -> bool:
        return self.menu_repo.delete(piatto_id)
