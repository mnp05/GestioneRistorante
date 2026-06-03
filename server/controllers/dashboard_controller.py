from datetime import datetime
from server.repositories.dashboard_repository import DashboardRepository
from server.repositories.user_repository import UserRepository


class DashboardController:
    def __init__(self):
        self.dash_repo = DashboardRepository()
        self.user_repo = UserRepository()

    def get_all_messages(self) -> list[dict]:
        messaggi = self.dash_repo.get_all()
        users = {str(u["id"]): u for u in self.user_repo.get_all()}
        for msg in messaggi:
            author_id = str(msg.get("utente_id", ""))
            if author_id in users:
                msg["nome_autore"] = users[author_id].get("nome", "")
                msg["cognome_autore"] = users[author_id].get("cognome", "")
                msg["ruolo_autore"] = users[author_id].get("ruolo", "Dipendente")
            else:
                msg["nome_autore"] = "Utente rimosso"
                msg["cognome_autore"] = ""
                msg["ruolo_autore"] = "Sconosciuto"

        # Ordiniamo in modo decrescente per avere il più recente in alto
        messaggi.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
        return messaggi

    def add_message(self, testo: str, utente_id: str) -> dict:
        if not testo.strip():
            raise ValueError("Il testo del messaggio non può essere vuoto.")
            
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.dash_repo.create({
            "utente_id": utente_id,
            "testo": testo,
            "timestamp": now
        })

    def edit_message(self, msg_id: str, utente_id: str, nuovo_testo: str) -> bool:
        msg = self.dash_repo.get_by_id(msg_id)
        if not msg or str(msg.get("utente_id")) != utente_id:
            raise PermissionError("Puoi modificare solo i tuoi messaggi.")
            
        return self.dash_repo.update(msg_id, {"testo": nuovo_testo})

    def remove_message(self, msg_id: str, utente_richiedente_id: str, utente_role: str) -> bool:
        msg = self.dash_repo.get_by_id(msg_id)
        if not msg:
            return False
            
        # Solo l'autore originale o un Gestore possono eliminare
        if str(msg.get("utente_id")) == utente_richiedente_id or utente_role == "Gestore":
            return self.dash_repo.delete(msg_id)
        
        raise PermissionError("Non hai i permessi per eliminare questo messaggio.")
