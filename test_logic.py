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
    "id_cliente": "4",
    "nome_ospite": "",
    "data": oggi,
    "ora": "20:30",
    "numero_persone": "5",
    "allergeni": "Nessuno",
    "note": ""
}

print(f"Tentativo di prenotazione per {dati_prenotazione['numero_persone']} persone in data {oggi}...")
risultato = controller.effettua_prenotazione(dati_prenotazione)

if risultato["id_tavolo"]:
    print(f"SUCCESSO! Il sistema ha assegnato il tavolo numero: {risultato['id_tavolo']} (Stato: {risultato['stato']})")
else:
    print(f"ATTENZIONE: Nessun tavolo disponibile. La prenotazione è in OVERBOOKING (Stato: {risultato['stato']})")

print("\nVerifica nel database CSV (prenotazioni attive oggi):")
prenotazioni = [p for p in controller.get_all_bookings() if p.get("data") == oggi]
for p in prenotazioni:
    print(f"- Prenotazione {p['id']}: Tavolo {p['id_tavolo']}, Persone {p['numero_persone']}, Stato {p['stato']}")
