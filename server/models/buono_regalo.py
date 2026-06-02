from dataclasses import dataclass
from typing import Optional

@dataclass
class BuonoRegalo:
    codice_univoco: str
    valore: float
    stato: str
    id_acquirente: str
    id_beneficiario: str
    data_scadenza: str

    def is_valido(self, data_odierna: str) -> bool:
        return self.stato == "ATTIVO" and data_odierna <= self.data_scadenza

    def riscatta(self, id_beneficiario: str) -> bool:
        if self.stato == "ATTIVO":
            self.stato = "RISCATTATO"
            # Assegna o verifica il beneficiario a seconda delle regole di business
            self.id_beneficiario = id_beneficiario
            return True
        return False
