# Gestione Ristorante

Applicazione desktop e backend server per la gestione di un ristorante. Sviluppata come progetto per il corso di Ingegneria del Software.

Il sistema adotta un'architettura **Client-Server a 3 livelli (3-Tier)**:
1. **Presentation Layer**: Client desktop PyQt5 per i Clienti (`client/`) e per lo Staff (`staff/`).
2. **Business Logic Layer**: Controller Flask (`server/controllers/`) che espongono API RESTful.
3. **Data Access Layer**: Repositories in Python (`server/models/`) che utilizzano Pandas per persistere i dati in formato CSV (`data/`).

---

## Requisiti di Sistema

- **Python 3.8+**
- Le dipendenze librarie elencate in `requirements.txt` (Flask, Pandas, PyQt5, Requests).

---

## Guida all'Installazione ed Avvio


### 3. Installare le Dipendenze
Con l'ambiente virtuale attivo, esegui:
```bash
pip install -r requirements.txt
```

### 4. Avvio dei Componenti
Per eseguire l'applicazione completa, avvia in sequenza (in terminali separati):

1. **Avvia il Server Backend**:
   ```bash
   python run_server.py
   ```
2. **Avvia l'Applicazione Cliente**:
   ```bash
   python run_client.py
   ```
3. **Avvia l'Applicazione Staff**:
   ```bash
   python run_staff.py
   ```
### Credenziali
dsdsdsdsdsds