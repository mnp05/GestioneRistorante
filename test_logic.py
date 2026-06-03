import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from server.controllers.booking_controller import BookingController

print("--- TEST LOGICA AUTO-ASSEGNAZIONE TAVOLO ---")
controller = BookingController()

# Simuliamo una richiesta di prenotazione per 5 persone stasera alle 20:30
oggi = datetime.now().strftime("%Y-%m-%d")
dati_prenotazione = {
    "cliente_id": "4",
    "nome_ospite": "",
    "data": oggi,
    "ora": "20:30",
    "numero_persone": "5",
    "allergeni": "Nessuno",
    "note": ""
}

print(f"Tentativo di prenotazione per {dati_prenotazione['numero_persone']} persone in data {oggi}...")
risultato = controller.handle_new_booking(dati_prenotazione)

if risultato["tavolo_id"]:
    print(f"SUCCESSO! Il sistema ha assegnato il tavolo numero: {risultato['tavolo_id']} (Stato: {risultato['stato']})")
else:
    print(f"ATTENZIONE: Nessun tavolo disponibile. La prenotazione è in OVERBOOKING (Stato: {risultato['stato']})")

print("\nStato delle prenotazioni di oggi:")
prenotazioni = [p for p in controller.handle_get_all_bookings() if p.get("data") == oggi]
for p in prenotazioni:
    print(f"- Prenotazione {p['id']}: Tavolo {p['tavolo_id']}, Persone {p['numero_persone']}, Stato {p['stato']}")
