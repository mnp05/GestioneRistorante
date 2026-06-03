from dataclasses import dataclass
from datetime import date
from server.models.enums import StatoBuono


@dataclass
class BuonoRegalo:
    codice_univoco: str
    valore: float
    stato: str
    acquirente_id: str
    beneficiario_id: str
    data_scadenza: str

    def is_valido(self) -> bool:
        oggi = date.today().isoformat()
        return self.stato == StatoBuono.ATTIVO.value and oggi <= self.data_scadenza

    def riscatta(self, beneficiario_id: str) -> bool:
        if self.stato == StatoBuono.ATTIVO.value:
            self.stato = StatoBuono.RISCATTATO.value
            self.beneficiario_id = beneficiario_id
            return True
        return False
