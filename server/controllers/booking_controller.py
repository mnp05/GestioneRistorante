from server.repositories.booking_repository import BookingRepository
from server.repositories.table_repository import TableRepository

class BookingController:
    def __init__(self):
        self.booking_repo = BookingRepository()
        self.table_repo = TableRepository()

    def get_all_bookings(self) -> list[dict]:
        return self.booking_repo.get_all()

    def effettua_prenotazione(self, dati: dict) -> dict:
        """
        Crea la prenotazione e tenta l'assegnazione automatica del tavolo.
        """
        data = dati.get("data")
        ora = dati.get("ora")
        numero_persone = int(dati.get("numero_persone", 1))
        
        # Tentativo di auto-assegnazione del tavolo
        tavolo_id = self.auto_assegnazione_tavolo(data, ora, numero_persone)
        
        if tavolo_id:
            dati["id_tavolo"] = tavolo_id
            dati["stato"] = "CONFERMATA"
        else:
            dati["id_tavolo"] = ""
            dati["stato"] = "RICHIESTA" # Overbooking, da gestire manualmente
            
        return self.booking_repo.create(dati)

    def auto_assegnazione_tavolo(self, data: str, ora: str, coperti: int) -> str:
        """
        Trova il primo tavolo libero in quella data/ora con capienza sufficiente.
        Ottimizza cercando la capienza minima necessaria.
        """
        tutti_i_tavoli = self.table_repo.get_all()
        tutte_le_prenotazioni = self.booking_repo.get_all()
        
        # Filtra tavoli per capienza
        tavoli_idonei = [t for t in tutti_i_tavoli if int(t.get("capienza", 0)) >= coperti]
        # Ordina per capienza crescente (ottimizzazione dei posti)
        tavoli_idonei.sort(key=lambda t: int(t.get("capienza", 0)))
        
        # Trova tavoli già occupati in quella data e fascia oraria approssimativa
        # (Per semplicità in questa fase assumiamo che 'ora' identifichi il turno intero)
        prenotazioni_conflitto = [
            p for p in tutte_le_prenotazioni 
            if p.get("data") == data and p.get("ora") == ora and p.get("stato") not in ["ANNULLATA", "DISDETTA"]
        ]
        tavoli_occupati = [p.get("id_tavolo") for p in prenotazioni_conflitto if p.get("id_tavolo")]
        
        for tavolo in tavoli_idonei:
            if str(tavolo["numero"]) not in tavoli_occupati:
                return str(tavolo["numero"])
        
        return "" # Nessun tavolo disponibile

    def conferma_prenotazione(self, booking_id: str, tavolo_id: str) -> bool:
        return self.booking_repo.update(booking_id, {"stato": "CONFERMATA", "id_tavolo": tavolo_id})

    def annulla_prenotazione(self, booking_id: str) -> bool:
        return self.booking_repo.update(booking_id, {"stato": "DISDETTA", "id_tavolo": ""})
        
    def get_tavoli(self) -> list[dict]:
        return self.table_repo.get_all()
        
    def aggiorna_stato_tavolo(self, numero_tavolo: str, nuovo_stato: str) -> bool:
        return self.table_repo.create_or_update({"numero": numero_tavolo, "stato": nuovo_stato})
