from dataclasses import dataclass


@dataclass
class MessaggioDashboard:
    id: int
    utente_id: str
    testo: str
    timestamp: str
