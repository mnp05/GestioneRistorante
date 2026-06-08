# Gestione Ristorante

Applicazione desktop e backend server per la gestione di un ristorante. Sviluppata come progetto per il corso di Ingegneria del Software, basandosi sulle linee guida architetturali e stilistiche del sistema *Wardrobe*.

Il sistema adotta un'architettura **Client-Server a 3 livelli (3-Tier)**:
1. **Presentation Layer**: Client desktop PyQt5 per i Clienti (`client/`) e per lo Staff (`staff/`).
2. **Business Logic Layer**: Controller Flask (`server/controllers/`) che espongono API RESTful.
3. **Data Access Layer**: Repositories in Python (`server/repositories/`) che utilizzano Pandas per persistere i dati in formato CSV (`data/`).

---

## Struttura del Progetto

Il codice sorgente è organizzato secondo la seguente struttura modulare:

- `data/`: Contiene i file CSV per la persistenza dei dati (Utenti, Prenotazioni, Tavoli, Menù, Inventario, Buoni Regalo, Transazioni Punti, Bacheca Staff).
- `server/`: Backend RESTful sviluppato in Flask.
  - `models/`: Classi di dominio entità (Entity).
  - `controllers/`: Logica di business applicativa (Controller Pattern).
  - `app.py`: Configurazione delle rotte Flask ed endpoint REST.
- `client/`: Applicazione PyQt5 dedicata ai Clienti (Visualizzazione menù, prenotazioni, programma punti fedeltà, acquisto e riscatto buoni regalo).
- `staff/`: Applicazione PyQt5 dedicata allo Staff (Gestione tavoli in tempo reale, approvazione prenotazioni, gestione menù, inventario e bacheca interna).

---

## Requisiti di Sistema

- **Python 3.8+**
- Le dipendenze librarie elencate in `requirements.txt` (Flask, Pandas, PyQt5, Requests).

---

## Guida all'Installazione ed Avvio

### 1. Clonare il Repository
```bash
git clone https://github.com/NOME_UTENTE/GestioneRistorante.git
cd GestioneRistorante
```

### 2. Configurare l'Ambiente Virtuale (Consigliato)
Crea un ambiente virtuale Python per isolare le dipendenze:
```powershell
# Creazione dell'ambiente virtuale
python -m venv venv

# Attivazione su Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Attivazione su macOS/Linux
source venv/bin/activate
```

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
