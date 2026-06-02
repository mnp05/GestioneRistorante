from dataclasses import dataclass

@dataclass
class TransazionePunti:
    id: int
    id_cliente: str
    punti: int
    descrizione: str
    data: str
