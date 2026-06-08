import uuid
from datetime import datetime
from server.models.promo import PromoRepository
from server.models.user import UserRepository


class PromoController:
    def __init__(self):
        self.promo_repo = PromoRepository()
        self.user_repo = UserRepository()

    def get_user_gift_cards(self, cliente_id: str) -> list[dict]:
        return self.promo_repo.get_buoni_by_cliente(cliente_id)

    def buy_gift_card(self, acquirente_id: str, valore: float, data_scadenza: str) -> dict:
        codice = f"GIFT-{uuid.uuid4().hex[:6].upper()}"
        dati_buono = {
            "codice_univoco": codice,
            "valore": valore,
            "stato": "ATTIVO",
            "acquirente_id": acquirente_id,
            "beneficiario_id": "",
            "data_scadenza": data_scadenza
        }
        return self.promo_repo.create_buono(dati_buono)

    def redeem_gift_card(self, codice: str, beneficiario_id: str) -> dict:
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
            "beneficiario_id": beneficiario_id
        })
        buono["stato"] = "RISCATTATO"
        return buono

    def get_accumulated_points(self, cliente_id: str) -> list[dict]:
        return self.promo_repo.get_transazioni(cliente_id)

    def add_spending_points(self, cliente_id: str, euro_spesi: float) -> dict:
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
            "cliente_id": cliente_id,
            "punti": punti_guadagnati,
            "descrizione": f"Acquisto di €{euro_spesi:.2f}",
            "data": oggi
        })

    def apply_gift_card_discount(self, codice: str, totale: float) -> float:
        """Applica lo sconto di un buono regalo attivo al totale.
        Restituisce il nuovo totale dopo la detrazione."""
        buono = self.promo_repo.get_buono(codice)
        if not buono:
            raise ValueError("Buono non trovato.")
        
        oggi = datetime.now().strftime("%Y-%m-%d")
        if buono.get("stato") != "ATTIVO" or oggi > str(buono.get("data_scadenza")):
            raise ValueError("Buono scaduto o non più attivo.")
        
        valore_buono = float(buono.get("valore", 0))
        nuovo_totale = max(0.0, totale - valore_buono)
        
        # Segna il buono come utilizzato
        self.promo_repo.update_buono(codice, {"stato": "RISCATTATO"})
        
        return nuovo_totale
