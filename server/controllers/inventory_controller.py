from server.models.inventory import InventoryRepository


class InventoryController:
    def __init__(self):
        self.inv_repo = InventoryRepository()

    def get_inventory(self) -> list[dict]:
        return self.inv_repo.get_all()

    def _to_float(self, val, default=0.0) -> float:
        try:
            if val is None or str(val).strip() == "":
                return float(default)
            return float(val)
        except (ValueError, TypeError):
            return float(default)

    def add_stock_item(self, dati: dict) -> dict:
        quantita = self._to_float(dati.get("quantita_disponibile", 0))
        soglia = self._to_float(dati.get("soglia_minima", 0))
        dati["stato"] = self._calcola_stato(quantita, soglia)
        return self.inv_repo.create(dati)

    def update_stock_quantity(self, ingrediente_id: str, nuova_quantita: float) -> bool:
        ingrediente = self.inv_repo.get_by_id(ingrediente_id)
        if not ingrediente:
            return False
            
        soglia = self._to_float(ingrediente.get("soglia_minima", 0))
        nuovo_stato = self._calcola_stato(nuova_quantita, soglia)
        
        return self.inv_repo.update(ingrediente_id, {
            "quantita_disponibile": nuova_quantita,
            "stato": nuovo_stato
        })

    def edit_stock_item(self, ingrediente_id: str, nuovi_dati: dict) -> bool:
        ingrediente = self.inv_repo.get_by_id(ingrediente_id)
        if not ingrediente:
            return False
            
        q_val = nuovi_dati.get("quantita_disponibile") if "quantita_disponibile" in nuovi_dati else ingrediente.get("quantita_disponibile", 0)
        s_val = nuovi_dati.get("soglia_minima") if "soglia_minima" in nuovi_dati else ingrediente.get("soglia_minima", 0)
        
        quantita = self._to_float(q_val)
        soglia = self._to_float(s_val)
        nuovi_dati["stato"] = self._calcola_stato(quantita, soglia)
        
        return self.inv_repo.update(ingrediente_id, nuovi_dati)

    def remove_stock_item(self, ingrediente_id: str) -> bool:
        return self.inv_repo.delete(ingrediente_id)

    def _calcola_stato(self, quantita: float, soglia: float) -> str:
        if quantita <= 0:
            return "ESAURITO"
        elif quantita < soglia:
            return "IN_ESAURIMENTO"
        else:
            return "SUFFICIENTE"

    def get_categories(self) -> list[str]:
        return self.inv_repo.get_all_categories()

    def remove_category(self, nome_categoria: str) -> bool:
        return self.inv_repo.bulk_remove_category(nome_categoria)
