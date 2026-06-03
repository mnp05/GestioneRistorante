import requests

class StaffAPIClient:
    BASE_URL = "http://127.0.0.1:5000/api"

    # --- AUTH ---

    @classmethod
    def login(cls, email, password):
        res = requests.post(f"{cls.BASE_URL}/auth/login", json={"email": email, "password": password})
        if res.status_code == 200:
            return res.json().get("user")
        raise ValueError(res.json().get("message", "Errore di login"))

    @classmethod
    def crea_dipendente(cls, creatore_id, nome, cognome, email, password, livello_accesso):
        res = requests.post(f"{cls.BASE_URL}/auth/dipendente", json={
            "creatore_id": creatore_id, "nome": nome, "cognome": cognome,
            "email": email, "password": password, "livello_accesso": livello_accesso
        })
        if res.status_code == 201:
            return res.json().get("user")
        raise ValueError(res.json().get("message", "Errore creazione dipendente"))

    @classmethod
    def get_dipendenti(cls):
        res = requests.get(f"{cls.BASE_URL}/auth/dipendenti")
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    @classmethod
    def aggiorna_livello_dipendente(cls, creatore_id, dipendente_id, nuovo_livello):
        res = requests.put(f"{cls.BASE_URL}/auth/dipendente/{dipendente_id}", json={
            "creatore_id": creatore_id,
            "livello_accesso": nuovo_livello
        })
        if res.status_code == 200:
            return True
        raise ValueError(res.json().get("message", "Errore aggiornamento dipendente"))

    @classmethod
    def elimina_dipendente(cls, creatore_id, dipendente_id):
        res = requests.delete(f"{cls.BASE_URL}/auth/dipendente/{dipendente_id}", json={
            "creatore_id": creatore_id
        })
        if res.status_code == 200:
            return True
        raise ValueError(res.json().get("message", "Errore eliminazione dipendente"))

    # --- TAVOLI ---

    @classmethod
    def get_tavoli(cls, data=None):
        params = {}
        if data:
            params["data"] = data
        res = requests.get(f"{cls.BASE_URL}/tables", params=params)
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    @classmethod
    def salva_tavolo(cls, dati):
        res = requests.post(f"{cls.BASE_URL}/tables", json=dati)
        if res.status_code == 200:
            return res.json().get("data")
        raise ValueError("Errore salvataggio tavolo")

    @classmethod
    def elimina_tavolo(cls, numero, data=None):
        params = {}
        if data:
            params["data"] = data
        res = requests.delete(f"{cls.BASE_URL}/tables/{numero}", params=params)
        return res.status_code == 200

    @classmethod
    def aggiorna_stato_tavolo(cls, numero, stato, data=None):
        payload = {"stato": stato}
        if data:
            payload["data"] = data
        res = requests.put(f"{cls.BASE_URL}/tables/{numero}", json=payload)
        return res.status_code == 200

    # --- PRENOTAZIONI ---

    @classmethod
    def get_prenotazioni(cls, data=None):
        params = {}
        if data:
            params["data"] = data
        res = requests.get(f"{cls.BASE_URL}/bookings", params=params)
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    @classmethod
    def conferma_prenotazione(cls, booking_id, tavolo_id):
        res = requests.put(f"{cls.BASE_URL}/bookings/{booking_id}", json={
            "stato": "CONFERMATA", "id_tavolo": tavolo_id
        })
        return res.status_code == 200

    @classmethod
    def annulla_prenotazione(cls, booking_id):
        res = requests.delete(f"{cls.BASE_URL}/bookings/{booking_id}")
        return res.status_code == 200

    @classmethod
    def auto_conferma_prenotazione(cls, booking_id):
        res = requests.post(f"{cls.BASE_URL}/bookings/{booking_id}/auto_confirm")
        if res.status_code == 200:
            return True, res.json().get("id_tavolo")
        return False, res.json().get("error_code")

    @classmethod
    def modifica_prenotazione(cls, booking_id, dati):
        res = requests.put(f"{cls.BASE_URL}/bookings/{booking_id}", json=dati)
        return res.status_code == 200

    # --- MENU ---

    @classmethod
    def get_menu(cls):
        res = requests.get(f"{cls.BASE_URL}/menu?all=true")
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    @classmethod
    def aggiungi_piatto(cls, dati):
        res = requests.post(f"{cls.BASE_URL}/menu", json=dati)
        if res.status_code == 201:
            return res.json().get("data")
        raise ValueError("Errore nell'aggiunta del piatto")

    @classmethod
    def modifica_piatto(cls, piatto_id, dati):
        res = requests.put(f"{cls.BASE_URL}/menu/{piatto_id}", json=dati)
        return res.status_code == 200

    @classmethod
    def elimina_piatto(cls, piatto_id):
        res = requests.delete(f"{cls.BASE_URL}/menu/{piatto_id}")
        return res.status_code == 200

    @classmethod
    def attiva_piatto(cls, piatto_id):
        res = requests.put(f"{cls.BASE_URL}/menu/{piatto_id}/activate")
        return res.status_code == 200

    # --- INVENTARIO ---

    @classmethod
    def get_inventario(cls):
        res = requests.get(f"{cls.BASE_URL}/inventory")
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    @classmethod
    def get_categorie_inventario(cls):
        res = requests.get(f"{cls.BASE_URL}/inventory/categories")
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    @classmethod
    def elimina_categoria_inventario(cls, nome):
        res = requests.delete(f"{cls.BASE_URL}/inventory/categories/{nome}")
        return res.status_code == 200

    @classmethod
    def aggiungi_ingrediente(cls, dati):
        res = requests.post(f"{cls.BASE_URL}/inventory", json=dati)
        if res.status_code == 201:
            return res.json().get("data")
        raise ValueError("Errore nell'aggiunta dell'ingrediente")

    @classmethod
    def modifica_ingrediente(cls, item_id, dati):
        res = requests.put(f"{cls.BASE_URL}/inventory/{item_id}/full", json=dati)
        return res.status_code == 200

    @classmethod
    def aggiorna_scorte(cls, item_id, quantita):
        res = requests.put(f"{cls.BASE_URL}/inventory/{item_id}", json={"quantita_disponibile": quantita})
        return res.status_code == 200

    @classmethod
    def elimina_ingrediente(cls, item_id):
        res = requests.delete(f"{cls.BASE_URL}/inventory/{item_id}")
        return res.status_code == 200

    # --- DASHBOARD ---

    @classmethod
    def get_messaggi(cls):
        res = requests.get(f"{cls.BASE_URL}/dashboard")
        if res.status_code == 200:
            return res.json().get("data", [])
        return []

    @classmethod
    def pubblica_messaggio(cls, autore_id, testo):
        res = requests.post(f"{cls.BASE_URL}/dashboard", json={"autore_id": autore_id, "testo": testo})
        if res.status_code == 201:
            return res.json().get("data")
        raise ValueError(res.json().get("message", "Errore pubblicazione messaggio"))

    @classmethod
    def elimina_messaggio(cls, msg_id, utente_id, ruolo):
        res = requests.delete(f"{cls.BASE_URL}/dashboard/{msg_id}", json={
            "utente_id": utente_id, "ruolo": ruolo
        })
        return res.status_code == 200
