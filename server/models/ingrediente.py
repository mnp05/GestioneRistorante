from dataclasses import dataclass

@dataclass
class CategoriaInventario:
    id: int
    nome: str

@dataclass
class IngredienteInventario:
    id: int
    nome: str
    descrizione: str
    quantita_disponibile: float
    unita_misura: str
    soglia_minima: float
    categoria_id: int
    stato: str

    def decrementa(self, quantita: float) -> None:
        self.quantita_disponibile -= quantita

    def incrementa(self, quantita: float) -> None:
        self.quantita_disponibile += quantita
        
    def get_soglia_minima(self) -> float:
        return self.soglia_minima
        
    def get_stato(self) -> str:
        return self.stato
        
    def is_sotto_scorta(self) -> bool:
        return self.quantita_disponibile < self.soglia_minima
        
    def set_quantita(self, quantita: float) -> None:
        self.quantita_disponibile = quantita
        
    def set_stato(self, stato: str) -> None:
        self.stato = stato
