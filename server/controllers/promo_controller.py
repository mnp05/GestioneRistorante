import uuid
from datetime import datetime
from server.repositories.promo_repository import PromoRepository
from server.repositories.user_repository import UserRepository

class PromoController:
    def __init__(self):
        self.promo_repo = PromoRepository()
        self.user_repo = UserRepository()

    def get_buoni_cliente(self, cliente_id: str) -> list[dict]:
        return self.promo_repo.get_buoni_by_cliente(cliente_id)

    def acquista_buono_regalo(self, id_acquirente: str, valore: float, data_scadenza: str) -> dict:
        codice = f"GIFT-{uuid.uuid4().hex[:6].upper()}"
        dati_buono = {
            "codice_univoco": codice,
            "valore": valore,
            "stato": "ATTIVO",
            "id_acquirente": id_acquirente,
            "id_beneficiario": "",
            "data_scadenza": data_scadenza
        }
        return self.promo_repo.create_buono(dati_buono)

    def riscatta_buono(self, codice: str, id_beneficiario: str) -> dict:
        buono = self.promo_repo.get_buono(codice)
        if not buono:
            raise ValueError("Buono non trovato.")
            
        oggi = datetime.now().strftime("%Y-%m-%d")
        if buono.get("stato") != "ATTIVO" or oggi > str(buono.get("data_scadenza")):
            self.promo_repo.update_buono(codice, {"stato": "SCADUTO"})
            raise ValueError("Buono scaduto o non più attivo.")

        # Riscatto completato
        self.promo_repo.update_buono(codice, {
            "stato": "RISCATTATO",
            "id_beneficiario": id_beneficiario
        })
        buono["stato"] = "RISCATTATO"
        return buono

    def get_storico_punti(self, cliente_id: str) -> list[dict]:
        return self.promo_repo.get_transazioni(cliente_id)

    def aggiungi_punti_spesa(self, cliente_id: str, euro_spesi: float) -> dict:
        # Regola 1 Euro = 1 Punto
        punti_guadagnati = int(euro_spesi)
        
        # Aggiorniamo saldo utente
        cliente = self.user_repo.get_by_id(cliente_id)
        if cliente:
            nuovo_saldo = int(cliente.get("saldo_punti", 0)) + punti_guadagnati
            self.user_repo.update(cliente_id, {"saldo_punti": nuovo_saldo})
            
        # Loggiamo la transazione
        oggi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.promo_repo.create_transazione({
            "id_cliente": cliente_id,
            "punti": punti_guadagnati,
            "descrizione": f"Acquisto di €{euro_spesi:.2f}",
            "data": oggi
        })
