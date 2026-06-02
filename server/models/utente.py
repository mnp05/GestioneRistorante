from dataclasses import dataclass
from typing import Optional

@dataclass
class Utente:
    id: int
    nome: str
    cognome: str
    email: str
    password: str
    stato_account: str
    ultimo_accesso: str

@dataclass
class Cliente(Utente):
    saldo_punti: int

    def accumula_punti(self, importo_speso: float) -> int:
        pass

    def acquista_buono_regalo(self, valore: float, data_scadenza: str) -> None:
        pass

    def effettua_prenotazione(self, data: str, ora: str, coperti: int, note: str) -> None:
        pass

    def get_saldo_punti(self) -> int:
        return self.saldo_punti

    def riscatta_buono(self, buono_id: int) -> bool:
        pass

    def riscatta_premio(self, punti_premio: int) -> bool:
        pass

    def salva_prodotto_preferito(self, prodotto_id: int) -> None:
        pass

@dataclass
class Dipendente(Utente):
    livello_accesso: str

    def get_livello_accesso(self) -> str:
        return self.livello_accesso

    def has_permesso(self, azione: str) -> bool:
        pass

    def scrivi_messaggio(self, testo: str) -> None:
        pass

@dataclass
class Gestore(Utente):
    def crea_dipendente(self, nome: str, cognome: str, email: str, livello_accesso: str) -> Dipendente:
        pass
