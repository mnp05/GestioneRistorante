import sys
import os

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from server.repositories.user_repository import UserRepository

print("--- TEST USER REPOSITORY ---")
repo = UserRepository()
utenti = repo.get_all()
print(f"Utenti totali caricati da CSV: {len(utenti)}")
for u in utenti:
    print(f"- {u['nome']} {u['cognome']} ({u['ruolo']}) - Email: {u['email']}")

print("\n--- TEST LOGIN ---")
user = repo.authenticate("gestore@ristorante.it", "gestore123")
if user:
    print(f"Login completato per {user['nome']}! Livello di accesso: {user['livello_accesso']}")
else:
    print("Login fallito.")
