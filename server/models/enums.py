from enum import Enum

class LivelloAccesso(str, Enum):
    GESTIONE_PRENOTAZIONI = "GESTIONE_PRENOTAZIONI"
    GESTIONE_INVENTARIO = "GESTIONE_INVENTARIO"
    GESTIONE_MENU = "GESTIONE_MENU"
    ACCESSO_COMPLETO = "ACCESSO_COMPLETO"

class RuoloUtente(str, Enum):
    GESTORE = "Gestore"
    DIPENDENTE = "Dipendente"
    CLIENTE = "Cliente"

class StatoPrenotazione(str, Enum):
    RICHIESTA = "RICHIESTA"
    CONFERMATA = "CONFERMATA"
    ANNULLATA = "ANNULLATA"
    DISDETTA = "DISDETTA"

class StatoTavolo(str, Enum):
    LIBERO = "LIBERO"
    OCCUPATO = "OCCUPATO"
    PRENOTATO = "PRENOTATO"

class StatoBuono(str, Enum):
    ATTIVO = "ATTIVO"
    SCADUTO = "SCADUTO"
    RISCATTATO = "RISCATTATO"
