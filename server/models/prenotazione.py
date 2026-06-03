from dataclasses import dataclass
from typing import Optional
from server.models.enums import StatoPrenotazione


@dataclass
class Prenotazione:
    id: int
    cliente_id: str
    nome_ospite: str
    data: str
    ora: str
    numero_persone: int
    allergeni: str
    note: str
    tavolo_id: str
    stato: str

    def conferma(self) -> None:
        self.stato = StatoPrenotazione.CONFERMATA.value

    def disdici(self) -> None:
        self.stato = StatoPrenotazione.DISDETTA.value

    def segna_in_corso(self) -> None:
        self.stato = StatoPrenotazione.IN_CORSO.value

    def concludi(self) -> None:
        self.stato = StatoPrenotazione.CONCLUSA.value

    def is_attiva(self) -> bool:
        stati_attivi = {
            StatoPrenotazione.RICHIESTA.value,
            StatoPrenotazione.CONFERMATA.value,
            StatoPrenotazione.IN_CORSO.value,
        }
        return self.stato in stati_attivi

    def associa_tavolo(self, tavolo_id: int) -> None:
        self.tavolo_id = tavolo_id
