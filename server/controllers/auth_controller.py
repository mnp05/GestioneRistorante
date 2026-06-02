from datetime import datetime
from server.repositories.user_repository import UserRepository

class AuthController:
    def __init__(self):
        self.user_repo = UserRepository()

    def login(self, email: str, password: str) -> dict:
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

    def register_cliente(self, nome: str, cognome: str, email: str, password: str) -> dict:
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

    def crea_dipendente(self, creatore_id: str, nome: str, cognome: str, email: str, password: str, livello_accesso: str) -> dict:
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
        
    def get_all_dipendenti(self) -> list[dict]:
        utenti = self.user_repo.get_all()
        return [u for u in utenti if u.get("ruolo") in ["Dipendente", "Gestore"]]
