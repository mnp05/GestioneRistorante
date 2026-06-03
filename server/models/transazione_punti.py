from dataclasses import dataclass


@dataclass
class TransazionePunti:
    id: int
    cliente_id: str
    punti: int
    descrizione: str
    data: str
