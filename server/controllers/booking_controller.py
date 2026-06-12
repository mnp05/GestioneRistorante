from typing import Optional
from datetime import datetime, timedelta
from server.models.booking import BookingRepository
from server.models.table import TableRepository
from server.models.user import UserRepository
from server.models.enums import StatoPrenotazione, StatoTavolo


class BookingController:
    def __init__(self):
        self.booking_repo = BookingRepository()
        self.table_repo = TableRepository()
        self.user_repo = UserRepository()

    def _is_time_overlap(self, ora1_str: str, ora2_str: str, duration_hours: int = 3) -> bool:
        try:
            t1 = datetime.strptime(ora1_str, "%H:%M")
            t2 = datetime.strptime(ora2_str, "%H:%M")
            t1_end = t1 + timedelta(hours=duration_hours)
            t2_end = t2 + timedelta(hours=duration_hours)
            return max(t1, t2) < min(t1_end, t2_end)
        except ValueError:
            return ora1_str == ora2_str

    def handle_get_all_bookings(self, data_filtro: Optional[str] = None) -> list[dict]:
        tutte = self.booking_repo.get_all()
        if data_filtro:
            tutte = [p for p in tutte if str(p.get("data")) == data_filtro]
            
        for b in tutte:
            if b.get("nome_ospite"):
                b["nome_cliente"] = b["nome_ospite"]
            elif b.get("cliente_id"):
                user = self.user_repo.get_by_id(str(b["cliente_id"]))
                if user:
                    b["nome_cliente"] = f"{user.get('nome', '')} {user.get('cognome', '')}".strip()
                else:
                    b["nome_cliente"] = f"Utente ID {b['cliente_id']}"
            else:
                b["nome_cliente"] = "Sconosciuto"
                
        return tutte

    def handle_new_booking(self, dati: dict) -> dict:
        """
        Crea la prenotazione in stato RICHIESTA. L'assegnazione automatica avverrà 
        solo alla conferma da parte del dipendente.
        """
        dati["tavolo_id"] = ""
        dati["stato"] = StatoPrenotazione.RICHIESTA.value
        return self.booking_repo.create(dati)

    def get_available_seats(self, data: str, ora: str) -> int:
        tutti_i_tavoli = self.table_repo.get_all()
        tutte_le_prenotazioni = self.booking_repo.get_all()
        
        prenotazioni_conflitto = [
            p for p in tutte_le_prenotazioni 
            if p.get("data") == data and self._is_time_overlap(str(p.get("ora")), ora) and p.get("stato") not in [StatoPrenotazione.ANNULLATA.value, StatoPrenotazione.DISDETTA.value]
        ]
        
        def _clean(val):
            s = str(val).strip()
            return s[:-2] if s.endswith('.0') else s

        tavoli_occupati = [_clean(p.get("tavolo_id")) for p in prenotazioni_conflitto if p.get("tavolo_id")]
        
        posti_liberi = 0
        for tavolo in tutti_i_tavoli:
            if _clean(tavolo["numero"]) not in tavoli_occupati:
                try:
                    posti_liberi += int(float(tavolo.get("capienza", 0)))
                except ValueError:
                    pass
                    
        return posti_liberi

    def handle_auto_assignment(self, data: str, ora: str, coperti: int, exclude_booking_id: Optional[str] = None) -> str:
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
        prenotazioni_conflitto = [
            p for p in tutte_le_prenotazioni 
            if p.get("data") == data and self._is_time_overlap(str(p.get("ora")), ora) and p.get("stato") not in [StatoPrenotazione.ANNULLATA.value, StatoPrenotazione.DISDETTA.value]
        ]
        
        if exclude_booking_id:
            prenotazioni_conflitto = [p for p in prenotazioni_conflitto if str(p.get("id")) != exclude_booking_id]
            
        def _clean(val):
            s = str(val).strip()
            return s[:-2] if s.endswith('.0') else s

        tavoli_occupati = [_clean(p.get("tavolo_id")) for p in prenotazioni_conflitto if p.get("tavolo_id")]
        
        for tavolo in tavoli_idonei:
            if _clean(tavolo["numero"]) not in tavoli_occupati:
                return _clean(tavolo["numero"])
        
        return "" # Nessun tavolo disponibile

    def handle_confirm_booking(self, booking_id: str, tavolo_id: str) -> bool:
        return self.booking_repo.update(booking_id, {"stato": StatoPrenotazione.CONFERMATA.value, "tavolo_id": tavolo_id})

    def handle_edit_booking(self, booking_id: str, data: dict) -> bool:
        vecchia_prenotazione = self.booking_repo.get_by_id(booking_id)
        if not vecchia_prenotazione:
            raise ValueError("Prenotazione non trovata.")
            
        # Se la prenotazione è CONFERMATA e stiamo cambiando data/ora/persone, dobbiamo verificare
        stato_attuale = vecchia_prenotazione.get("stato")
        if stato_attuale == StatoPrenotazione.CONFERMATA.value:
            nuova_data = data.get("data", vecchia_prenotazione.get("data"))
            nuova_ora = data.get("ora", vecchia_prenotazione.get("ora"))
            
            try:
                # Usiamo str() per placare il linter, garantendo che int() riceva una stringa.
                # Se il valore è None, diventerà "None" e int() solleverà correttamente un ValueError.
                persone = int(str(data.get("numero_persone", vecchia_prenotazione.get("numero_persone", 1))))
            except (ValueError, TypeError):
                persone = int(str(vecchia_prenotazione.get("numero_persone", 1)))
                
            if (nuova_data != vecchia_prenotazione.get("data") or 
                nuova_ora != vecchia_prenotazione.get("ora") or 
                str(persone) != str(vecchia_prenotazione.get("numero_persone", 1))):
                
                nuovo_tavolo = self.handle_auto_assignment(str(nuova_data), str(nuova_ora), persone, exclude_booking_id=booking_id)
                if not nuovo_tavolo:
                    raise ValueError("Nessun tavolo compatibile libero per i nuovi dati scelti.")
                    
                data["tavolo_id"] = nuovo_tavolo

        return self.booking_repo.update(booking_id, data)

    def handle_try_auto_confirm(self, booking_id: str) -> Optional[str]:
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
            
        tavolo_id = self.handle_auto_assignment(data, ora, numero_persone)
        if tavolo_id:
            self.handle_confirm_booking(booking_id, tavolo_id)
            return tavolo_id
        return None

    def handle_cancel_booking(self, booking_id: str) -> bool:
        return self.booking_repo.update(booking_id, {"stato": StatoPrenotazione.DISDETTA.value, "tavolo_id": ""})
        
    def handle_get_tables(self, data_filtro: Optional[str] = None) -> list[dict]:
        target_date = data_filtro if data_filtro else "DEFAULT"
        tavoli = self.table_repo.get_for_date(target_date)
        
        if data_filtro:
            prenotazioni_del_giorno = self.handle_get_all_bookings(data_filtro)
            
            def _clean(val):
                s = str(val).strip()
                return s[:-2] if s.endswith('.0') else s
                
            tavoli_prenotati = [_clean(p.get("tavolo_id")) for p in prenotazioni_del_giorno if p.get("stato") in [StatoPrenotazione.CONFERMATA.value, StatoPrenotazione.RICHIESTA.value] and p.get("tavolo_id")]
            
            for t in tavoli:
                if _clean(t.get("numero")) in tavoli_prenotati:
                    t["stato"] = StatoTavolo.PRENOTATO.value
                    
        return tavoli
        
    def handle_table_status_update(self, numero_tavolo: str, nuovo_stato: str, target_date: str = "DEFAULT") -> bool:
        return self.table_repo.update_stato(numero_tavolo, nuovo_stato, target_date)

    def handle_table_layout_update(self, dati: dict) -> dict:
        return self.table_repo.create_or_update(dati)

    def handle_remove_table(self, numero: str, target_date: str = "DEFAULT") -> bool:
        return self.table_repo.delete(numero, target_date)
