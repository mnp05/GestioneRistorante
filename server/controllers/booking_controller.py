from typing import Optional
from server.repositories.booking_repository import BookingRepository
from server.repositories.table_repository import TableRepository
from server.repositories.user_repository import UserRepository

class BookingController:
    def __init__(self):
        self.booking_repo = BookingRepository()
        self.table_repo = TableRepository()
        self.user_repo = UserRepository()

    def get_all_bookings(self, data_filtro: Optional[str] = None) -> list[dict]:
        tutte = self.booking_repo.get_all()
        if data_filtro:
            tutte = [p for p in tutte if str(p.get("data")) == data_filtro]
            
        for b in tutte:
            if b.get("nome_ospite"):
                b["nome_cliente"] = b["nome_ospite"]
            elif b.get("id_cliente"):
                user = self.user_repo.get_by_id(str(b["id_cliente"]))
                if user:
                    b["nome_cliente"] = f"{user.get('nome', '')} {user.get('cognome', '')}".strip()
                else:
                    b["nome_cliente"] = f"Utente ID {b['id_cliente']}"
            else:
                b["nome_cliente"] = "Sconosciuto"
                
        return tutte

    def effettua_prenotazione(self, dati: dict) -> dict:
        """
        Crea la prenotazione in stato RICHIESTA. L'assegnazione automatica avverrà 
        solo alla conferma da parte del dipendente.
        """
        dati["id_tavolo"] = ""
        dati["stato"] = "RICHIESTA"
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
        def _clean(val):
            s = str(val).strip()
            return s[:-2] if s.endswith('.0') else s

        tavoli_occupati = [_clean(p.get("id_tavolo")) for p in prenotazioni_conflitto if p.get("id_tavolo")]
        
        for tavolo in tavoli_idonei:
            if _clean(tavolo["numero"]) not in tavoli_occupati:
                return _clean(tavolo["numero"])
        
        return "" # Nessun tavolo disponibile

    def conferma_prenotazione(self, booking_id: str, tavolo_id: str) -> bool:
        return self.booking_repo.update(booking_id, {"stato": "CONFERMATA", "id_tavolo": tavolo_id})

    def modifica_prenotazione(self, booking_id: str, data: dict) -> bool:
        return self.booking_repo.update(booking_id, data)

    def tenta_auto_conferma(self, booking_id: str) -> Optional[str]:
        """Tenta l'assegnazione automatica. Restituisce l'ID del tavolo se OK, None se overbooking."""
        prenotazione = self.booking_repo.get_by_id(booking_id)
        if not prenotazione:
            return None
        
        data = str(prenotazione.get("data", ""))
        ora = str(prenotazione.get("ora", ""))
        try:
            numero_persone = int(prenotazione.get("numero_persone", 1))
        except ValueError:
            numero_persone = 1
            
        tavolo_id = self.auto_assegnazione_tavolo(data, ora, numero_persone)
        if tavolo_id:
            self.conferma_prenotazione(booking_id, tavolo_id)
            return tavolo_id
        return None

    def annulla_prenotazione(self, booking_id: str) -> bool:
        return self.booking_repo.update(booking_id, {"stato": "DISDETTA", "id_tavolo": ""})
        
    def get_tavoli(self, data_filtro: Optional[str] = None) -> list[dict]:
        target_date = data_filtro if data_filtro else "DEFAULT"
        tavoli = self.table_repo.get_for_date(target_date)
        
        if data_filtro:
            prenotazioni_del_giorno = self.get_all_bookings(data_filtro)
            
            def _clean(val):
                s = str(val).strip()
                return s[:-2] if s.endswith('.0') else s
                
            tavoli_prenotati = [_clean(p.get("id_tavolo")) for p in prenotazioni_del_giorno if p.get("stato") in ["CONFERMATA", "RICHIESTA"] and p.get("id_tavolo")]
            
            for t in tavoli:
                if _clean(t.get("numero")) in tavoli_prenotati:
                    t["stato"] = "PRENOTATO"
                    
        return tavoli
        
    def aggiorna_stato_tavolo(self, numero_tavolo: str, nuovo_stato: str, target_date: str = "DEFAULT") -> bool:
        return self.table_repo.update_stato(numero_tavolo, nuovo_stato, target_date)

    def salva_tavolo(self, dati: dict) -> dict:
        return self.table_repo.create_or_update(dati)

    def rimuovi_tavolo(self, numero: str, target_date: str = "DEFAULT") -> bool:
        return self.table_repo.delete(numero, target_date)
