from server.repositories.inventory_repository import InventoryRepository

class InventoryController:
    def __init__(self):
        self.inv_repo = InventoryRepository()

    def get_inventario(self) -> list[dict]:
        return self.inv_repo.get_all()

    def aggiungi_ingrediente(self, dati: dict) -> dict:
        quantita = float(dati.get("quantita_disponibile", 0))
        soglia = float(dati.get("soglia_minima", 0))
        dati["stato"] = self._calcola_stato(quantita, soglia)
        return self.inv_repo.create(dati)

    def aggiorna_scorte(self, ingrediente_id: str, nuova_quantita: float) -> bool:
        ingrediente = self.inv_repo.get_by_id(ingrediente_id)
        if not ingrediente:
            return False
            
        soglia = float(ingrediente.get("soglia_minima", 0))
        nuovo_stato = self._calcola_stato(nuova_quantita, soglia)
        
        return self.inv_repo.update(ingrediente_id, {
            "quantita_disponibile": nuova_quantita,
            "stato": nuovo_stato
        })

    def rimuovi_ingrediente(self, ingrediente_id: str) -> bool:
        return self.inv_repo.delete(ingrediente_id)

    def _calcola_stato(self, quantita: float, soglia: float) -> str:
        if quantita <= 0:
            return "ESAURITO"
        elif quantita < soglia:
            return "IN_ESAURIMENTO"
        else:
            return "SUFFICIENTE"
