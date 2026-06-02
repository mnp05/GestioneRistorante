import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("Avvio del server di Gestione Ristorante in corso...")
    from server.app import app
    app.run(debug=True, port=5000)
