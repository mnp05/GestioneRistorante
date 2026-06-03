from datetime import datetime
from server.repositories.user_repository import UserRepository


class AuthController:
    def __init__(self):
        self.user_repo = UserRepository()

    def handle_login(self, email: str, password: str) -> dict:
        user = self.user_repo.authenticate(email, password)
        if user:
            if user.get("stato_account") != "ATTIVO":
                raise ValueError("Account non attivo.")
            # Aggiorna ultimo accesso
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.user_repo.update(user["id"], {"ultimo_accesso": now})
            user["ultimo_accesso"] = now
            return user
        raise ValueError("Credenziali non valide.")

    def handle_signup(self, nome: str, cognome: str, email: str, password: str) -> dict:
        dati_cliente = {
            "nome": nome.strip(),
            "cognome": cognome.strip(),
            "email": email.strip(),
            "password": password, # In futuro aggiungere l'hash qui
            "ruolo": "Cliente",
            "livello_accesso": "",
            "stato_account": "ATTIVO",
            "ultimo_accesso": "",
            "saldo_punti": 0
        }
        return self.user_repo.create(dati_cliente)

    def handle_create_employee(self, creatore_id: str, nome: str, cognome: str, email: str, password: str, livello_accesso: str) -> dict:
        creatore = self.user_repo.get_by_id(creatore_id)
        if not creatore or creatore.get("ruolo") != "Gestore":
            raise PermissionError("Solo il Gestore può creare account dipendenti.")
            
        dati_dipendente = {
            "nome": nome.strip(),
            "cognome": cognome.strip(),
            "email": email.strip(),
            "password": password, # In futuro aggiungere l'hash qui
            "ruolo": "Dipendente",
            "livello_accesso": livello_accesso,
            "stato_account": "ATTIVO",
            "ultimo_accesso": "",
            "saldo_punti": 0
        }
        return self.user_repo.create(dati_dipendente)
        
    def handle_get_all_employees(self) -> list[dict]:
        utenti = self.user_repo.get_all()
        return [u for u in utenti if u.get("ruolo") in ["Dipendente", "Gestore"]]

    def handle_remove_employee(self, creatore_id: str, dipendente_id: str) -> bool:
        creatore = self.user_repo.get_by_id(creatore_id)
        if not creatore or creatore.get("ruolo") != "Gestore":
            raise PermissionError("Solo il Gestore può eliminare account dipendenti.")
        
        # Non permettere l'auto-eliminazione o l'eliminazione di un altro gestore (per sicurezza base)
        target = self.user_repo.get_by_id(dipendente_id)
        if not target or target.get("ruolo") == "Gestore":
            raise ValueError("Impossibile eliminare l'account specificato.")
            
        return self.user_repo.delete(dipendente_id)

    def handle_modify_access_level(self, creatore_id: str, dipendente_id: str, nuovo_livello: str) -> bool:
        creatore = self.user_repo.get_by_id(creatore_id)
        if not creatore or creatore.get("ruolo") != "Gestore":
            raise PermissionError("Solo il Gestore può modificare i livelli di accesso.")
            
        target = self.user_repo.get_by_id(dipendente_id)
        if not target or target.get("ruolo") == "Gestore":
            raise ValueError("Impossibile modificare l'account specificato.")
            
        return self.user_repo.update(dipendente_id, {"livello_accesso": nuovo_livello})

    def handle_logout(self) -> None:
        # Il logout viene gestito lato client svuotando la sessione corrente.
        # Lato server non è necessaria alcuna azione persistente.
        pass
