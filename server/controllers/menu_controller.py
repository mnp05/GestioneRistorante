from server.models.menu import MenuRepository
from server.models.user import UserRepository


class MenuController:
    def __init__(self):
        self.menu_repo = MenuRepository()
        self.user_repo = UserRepository()

    def get_filtered_menu(self) -> list[dict]:
        tutti = self.menu_repo.get_all()
        # Restituisce solo i prodotti con attivo=True
        return [p for p in tutti if str(p.get("attivo", "")).lower() in ("true", "1", "t")]

    def get_all_menu(self) -> list[dict]:
        return self.menu_repo.get_all()

    def add_product(self, dati: dict) -> dict:
        dati["attivo"] = True
        return self.menu_repo.create(dati)

    def edit_product(self, piatto_id: str, nuovi_dati: dict) -> bool:
        return self.menu_repo.update(piatto_id, nuovi_dati)

    def deactivate_product(self, piatto_id: str) -> bool:
        return self.menu_repo.update(piatto_id, {"attivo": False})

    def activate_product(self, piatto_id: str) -> bool:
        return self.menu_repo.update(piatto_id, {"attivo": True})

    def delete_product(self, piatto_id: str) -> bool:
        return self.menu_repo.delete(piatto_id)

    # --- PREFERITI ---
    
    def toggle_favorite(self, cliente_id: str, piatto_id: str) -> bool:
        user = self.user_repo.get_by_id(cliente_id)
        if not user:
            raise ValueError("Utente non trovato")
        
        piatti_str = str(user.get("piatti_preferiti", ""))
        preferiti = [p.strip() for p in piatti_str.split(",") if p.strip()]
        
        piatto_id = piatto_id
        is_added = False
        if piatto_id in preferiti:
            preferiti.remove(piatto_id)
        else:
            preferiti.append(piatto_id)
            is_added = True
            
        new_str = ",".join(preferiti)
        self.user_repo.update(cliente_id, {"piatti_preferiti": new_str})
        return is_added

    def get_favorites(self, cliente_id: str) -> list[dict]:
        user = self.user_repo.get_by_id(cliente_id)
        if not user:
            return []
            
        piatti_str = str(user.get("piatti_preferiti", ""))
        preferiti_ids = [p.strip() for p in piatti_str.split(",") if p.strip()]
        
        if not preferiti_ids:
            return []
            
        tutti_i_piatti = self.get_filtered_menu()
        return [p for p in tutti_i_piatti if str(p.get("id")) in preferiti_ids]
