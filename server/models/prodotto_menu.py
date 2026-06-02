from dataclasses import dataclass
from typing import Optional

@dataclass
class CategoriaMenu:
    id: int
    nome: str

@dataclass
class ProdottoMenu:
    id: int
    nome: str
    descrizione: str
    prezzo: float
    allergeni: str
    categoria_id: int
    foto_path: str
    attivo: bool
    
    def aggiorna_attributi(self, nuovi_dati: dict) -> None:
        pass
        
    def disattiva(self) -> None:
        self.attivo = False
