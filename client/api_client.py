import requests

class APIClient:
    BASE_URL = "http://127.0.0.1:5000/api"

    @classmethod
    def login(cls, email, password):
        res = requests.post(f"{cls.BASE_URL}/auth/login", json={"email": email, "password": password})
        if res.status_code == 200:
            return res.json().get("user")
        raise ValueError(res.json().get("message", "Errore di login"))

    @classmethod
    def register(cls, nome, cognome, email, password):
        res = requests.post(f"{cls.BASE_URL}/auth/register", json={
            "nome": nome,
            "cognome": cognome,
            "email": email,
            "password": password
        })
        if res.status_code == 201:
            return res.json().get("user")
        raise ValueError(res.json().get("message", "Errore di registrazione"))

    @classmethod
    def cancella_account(cls, cliente_id, password):
        res = requests.delete(f"{cls.BASE_URL}/auth/clienti/{cliente_id}", json={
            "password": password
        })
        if res.status_code == 200:
            return True
        raise ValueError(res.json().get("message", "Errore durante l'eliminazione dell'account"))

    @classmethod
    def cambia_password(cls, user_id, old_pw, new_pw):
        res = requests.put(f"{cls.BASE_URL}/auth/password/{user_id}", json={
            "old_password": old_pw,
            "new_password": new_pw
        })
        if res.status_code == 200:
            return True
        raise ValueError(res.json().get("message", "Errore durante il cambio password"))

    @classmethod
    def recupera_password(cls, email):
        res = requests.post(f"{cls.BASE_URL}/auth/recover", json={"email": email})
        if res.status_code == 200:
            return res.json().get("password")
        raise ValueError(res.json().get("message", "Impossibile recuperare la password"))

    @classmethod
    def get_menu(cls):
        res = requests.get(f"{cls.BASE_URL}/menu")
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    @classmethod
    def get_preferiti(cls, cliente_id):
        res = requests.get(f"{cls.BASE_URL}/menu/preferiti/{cliente_id}")
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    @classmethod
    def toggle_preferito(cls, cliente_id, piatto_id):
        res = requests.post(f"{cls.BASE_URL}/menu/preferiti/{cliente_id}", json={
            "piatto_id": piatto_id
        })
        if res.status_code == 200:
            return res.json().get("is_added")
        raise ValueError("Errore aggiornamento preferiti")

    @classmethod
    def get_punti_fedelta(cls, user_id):
        # Cerchiamo lo storico dei punti
        res = requests.get(f"{cls.BASE_URL}/promo/punti/{user_id}")
        if res.status_code == 200:
            # Per semplicità calcoliamo il saldo qui o assumiamo di avere il dato
            # (Nel backend abbiamo salvato saldo_punti dentro l'oggetto utente, usiamo quello)
            pass
        return 0 # Placeholder: usiamo user.get('saldo_punti') nell'interfaccia

    @classmethod
    def riscatta_buono(cls, codice, user_id):
        res = requests.post(f"{cls.BASE_URL}/promo/riscatta", json={
            "codice": codice,
            "beneficiario_id": user_id
        })
        if res.status_code == 200:
            return True
        raise ValueError(res.json().get("message", "Errore riscatto buono"))

    @classmethod
    def get_buoni(cls, user_id):
        res = requests.get(f"{cls.BASE_URL}/promo/buoni/{user_id}")
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    @classmethod
    def acquista_buono(cls, id_acquirente, valore, data_scadenza):
        res = requests.post(f"{cls.BASE_URL}/promo/buoni", json={
            "acquirente_id": id_acquirente,
            "valore": valore,
            "data_scadenza": data_scadenza
        })
        if res.status_code == 201:
            return res.json().get("data")
        raise ValueError(res.json().get("message", "Errore acquisto buono"))

    # --- PRENOTAZIONI ---

    @classmethod
    def get_prenotazioni_utente(cls, user_id):
        res = requests.get(f"{cls.BASE_URL}/bookings", params={"clienteId": user_id})
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    @classmethod
    def effettua_prenotazione(cls, dati):
        res = requests.post(f"{cls.BASE_URL}/bookings", json=dati)
        if res.status_code == 201:
            return res.json().get("data")
        raise ValueError(res.json().get("message", "Errore durante la prenotazione"))

    @classmethod
    def cancella_prenotazione(cls, booking_id):
        res = requests.delete(f"{cls.BASE_URL}/bookings/{booking_id}")
        if res.status_code == 200:
            return True
        return False

    @classmethod
    def modifica_prenotazione(cls, booking_id, dati):
        res = requests.put(f"{cls.BASE_URL}/bookings/{booking_id}", json=dati)
        if res.status_code == 200:
            return True
        return False
