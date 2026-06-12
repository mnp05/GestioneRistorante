from datetime import datetime
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from server.models.user import UserRepository
from server.models.enums import RuoloUtente, LivelloAccesso

class AuthController:
    def __init__(self):
        self.user_repo = UserRepository()
        self.reset_tokens = {}

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
            "password": generate_password_hash(password),
            "ruolo": RuoloUtente.CLIENTE.value,
            "livello_accesso": "",
            "stato_account": "ATTIVO",
            "ultimo_accesso": "",
            "saldo_punti": 0
        }
        return self.user_repo.create(dati_cliente)

    def handle_create_employee(self, creatore_id: str, nome: str, cognome: str, email: str, password: str, livello_accesso: str) -> dict:
        creatore = self.user_repo.get_by_id(creatore_id)
        if not creatore or creatore.get("ruolo") != RuoloUtente.GESTORE.value:
            raise PermissionError("Solo il Gestore può creare account dipendenti.")
            
        dati_dipendente = {
            "nome": nome.strip(),
            "cognome": cognome.strip(),
            "email": email.strip(),
            "password": generate_password_hash(password),
            "ruolo": RuoloUtente.DIPENDENTE.value,
            "livello_accesso": livello_accesso,
            "stato_account": "ATTIVO",
            "ultimo_accesso": "",
            "saldo_punti": 0
        }
        return self.user_repo.create(dati_dipendente)
        
    def handle_get_all_employees(self) -> list[dict]:
        utenti = self.user_repo.get_all()
        return [u for u in utenti if u.get("ruolo") in [RuoloUtente.DIPENDENTE.value, RuoloUtente.GESTORE.value]]

    def handle_get_all_clients(self) -> list[dict]:
        utenti = self.user_repo.get_all()
        return [u for u in utenti if u.get("ruolo") == RuoloUtente.CLIENTE.value]

    def handle_remove_employee(self, creatore_id: str, dipendente_id: str) -> bool:
        creatore = self.user_repo.get_by_id(creatore_id)
        if not creatore or creatore.get("ruolo") != RuoloUtente.GESTORE.value:
            raise PermissionError("Solo il Gestore può eliminare account dipendenti.")
        
        # Non permettere l'auto-eliminazione o l'eliminazione di un altro gestore (per sicurezza base)
        target = self.user_repo.get_by_id(dipendente_id)
        if not target or target.get("ruolo") == RuoloUtente.GESTORE.value:
            raise ValueError("Impossibile eliminare l'account specificato.")
            
        return self.user_repo.delete(dipendente_id)

    def handle_remove_client(self, cliente_id: str, password: str) -> bool:
        cliente = self.user_repo.get_by_id(cliente_id)
        if not cliente or cliente.get("ruolo") != RuoloUtente.CLIENTE.value:
            raise ValueError("Account cliente non trovato.")
            
        # Verifica della password crittografata
        if not check_password_hash(str(cliente.get("password", "")), password):
            raise ValueError("Password errata. Impossibile cancellare l'account.")
            
        # Elimina a cascata le prenotazioni del cliente
        from server.models.booking import BookingRepository
        booking_repo = BookingRepository()
        for b in booking_repo.get_all():
            if str(b.get("cliente_id")) == cliente_id:
                booking_repo.delete(str(b.get("id")))
                
        return self.user_repo.delete(cliente_id)

    def handle_modify_access_level(self, creatore_id: str, dipendente_id: str, nuovo_livello: str) -> bool:
        creatore = self.user_repo.get_by_id(creatore_id)
        if not creatore or creatore.get("ruolo") != RuoloUtente.GESTORE.value:
            raise PermissionError("Solo il Gestore può modificare i livelli di accesso.")
            
        target = self.user_repo.get_by_id(dipendente_id)
        if not target or target.get("ruolo") == RuoloUtente.GESTORE.value:
            raise ValueError("Impossibile modificare l'account specificato.")
            
        return self.user_repo.update(dipendente_id, {"livello_accesso": nuovo_livello})

    def handle_logout(self) -> None:
        # Il logout viene gestito lato client svuotando la sessione corrente.
        # Lato server non è necessaria alcuna azione persistente.
        pass

    def handle_change_password(self, user_id: str, old_pw: str, new_pw: str) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("Utente non trovato.")
            
        if not check_password_hash(str(user.get("password", "")), old_pw):
            raise ValueError("Vecchia password errata.")
            
        return self.user_repo.update(user_id, {"password": generate_password_hash(new_pw)})

    def handle_recover_password(self, email: str) -> str:
        user = self.user_repo.get_by_email(email)
        if user:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.reset_tokens[email] = code
            return code
        raise ValueError("Nessun account associato a questa email.")

    def handle_reset_password(self, email: str, code: str, new_pw: str) -> bool:
        if email not in self.reset_tokens or self.reset_tokens[email] != code:
            raise ValueError("Codice temporaneo non valido.")
        
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Utente non trovato.")
            
        success = self.user_repo.update(user["id"], {"password": generate_password_hash(new_pw)})
        if success:
            del self.reset_tokens[email]
            return True
        return False
