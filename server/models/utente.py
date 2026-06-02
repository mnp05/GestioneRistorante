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
        # 1 punto per ogni euro intero speso
        punti_guadagnati = int(importo_speso)
        self.saldo_punti += punti_guadagnati
        return punti_guadagnati

    def acquista_buono_regalo(self, valore: float, data_scadenza: str) -> None:
        pass

    def effettua_prenotazione(self, data: str, ora: str, coperti: int, note: str) -> None:
        pass

    def get_saldo_punti(self) -> int:
        return self.saldo_punti

    def riscatta_buono(self, buono_id: int) -> bool:
        # Logica base (da espandere): presumiamo sempre True per ora
        return True

    def riscatta_premio(self, punti_premio: int) -> bool:
        if self.saldo_punti >= punti_premio:
            self.saldo_punti -= punti_premio
            return True
        return False

    def salva_prodotto_preferito(self, prodotto_id: int) -> None:
        pass

@dataclass
class Dipendente(Utente):
    livello_accesso: str

    def get_livello_accesso(self) -> str:
        return self.livello_accesso

    def has_permesso(self, azione: str) -> bool:
        if self.livello_accesso == "ACCESSO_COMPLETO":
            return True
        return azione == self.livello_accesso

    def scrivi_messaggio(self, testo: str) -> None:
        pass

@dataclass
class Gestore(Utente):
    def crea_dipendente(self, nome: str, cognome: str, email: str, livello_accesso: str) -> Dipendente:
        return Dipendente(
            id=0,  # ID provvisorio, verrà assegnato dal database
            nome=nome,
            cognome=cognome,
            email=email,
            password="password_generata",
            stato_account="ATTIVO",
            ultimo_accesso="",
            livello_accesso=livello_accesso
        )
