from dataclasses import dataclass
from typing import Optional

@dataclass
class Prenotazione:
    id: int
    id_cliente: str
    nome_ospite: str
    data: str
    ora: str
    numero_persone: int
    allergeni: str
    note: str
    id_tavolo: str
    stato: str
