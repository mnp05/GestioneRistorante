import requests
import time
import subprocess

print("Avvio del server Flask in background...")
# Avviamo il server in locale e attendiamo che sia online
process = subprocess.Popen(["python", "server/app.py"])
time.sleep(3) # Diamo il tempo a Flask di avviarsi sulla porta 5000

print("\n--- TEST CHIAMATA API: RECUPERO MENU ---")
try:
    response = requests.get("http://127.0.0.1:5000/api/menu")
    if response.status_code == 200:
        data = response.json()
        print("SUCCESSO! Ricevuta risposta 200 OK.")
        print(f"Prodotti caricati: {len(data['data'])}")
        for piatto in data['data']:
            print(f"- {piatto['nome']}: €{piatto['prezzo']} (Allergeni: {piatto['allergeni']})")
    else:
        print(f"Errore API: Status code {response.status_code}")
except Exception as e:
    print(f"Errore di connessione: {e}")

finally:
    print("\nSpegnimento del server Flask di test...")
    process.terminate()
