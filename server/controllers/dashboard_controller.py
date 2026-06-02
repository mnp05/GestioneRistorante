from datetime import datetime
from server.repositories.dashboard_repository import DashboardRepository

class DashboardController:
    def __init__(self):
        self.dash_repo = DashboardRepository()

    def get_messaggi(self) -> list[dict]:
        messaggi = self.dash_repo.get_all()
        # Ordiniamo in modo decrescente per avere il più recente in alto
        messaggi.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
        return messaggi

    def pubblica_messaggio(self, autore_id: str, testo: str) -> dict:
        if not testo.strip():
            raise ValueError("Il testo del messaggio non può essere vuoto.")
            
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.dash_repo.create({
            "id_autore": autore_id,
            "testo": testo,
            "timestamp": now
        })

    def modifica_messaggio(self, msg_id: str, autore_id: str, nuovo_testo: str) -> bool:
        msg = self.dash_repo.get_by_id(msg_id)
        if not msg or str(msg.get("id_autore")) != str(autore_id):
            raise PermissionError("Puoi modificare solo i tuoi messaggi.")
            
        return self.dash_repo.update(msg_id, {"testo": nuovo_testo})

    def rimuovi_messaggio(self, msg_id: str, utente_richiedente_id: str, utente_role: str) -> bool:
        msg = self.dash_repo.get_by_id(msg_id)
        if not msg:
            return False
            
        # Solo l'autore originale o un Gestore possono eliminare
        if str(msg.get("id_autore")) == str(utente_richiedente_id) or utente_role == "Gestore":
            return self.dash_repo.delete(msg_id)
        
        raise PermissionError("Non hai i permessi per eliminare questo messaggio.")
