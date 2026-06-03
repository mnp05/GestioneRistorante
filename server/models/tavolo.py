from dataclasses import dataclass
from server.models.enums import StatoTavolo


@dataclass
class Tavolo:
    numero: int
    capienza: int
    coordinata_x: int
    coordinata_y: int
    stato: str

    def is_disponibile(self) -> bool:
        return self.stato == StatoTavolo.DISPONIBILE.value

    def cambia_stato(self, nuovo_stato: str) -> None:
        self.stato = nuovo_stato

    def aggiorna_posizione(self, x: int, y: int) -> None:
        self.coordinata_x = x
        self.coordinata_y = y
