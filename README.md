# CsecurityMES

Applicazione Flask per la gestione degli accessi, costruita sullo schema MySQL `gestione_accessi`.

## Descrizione

La webapp gestisce autenticazione, persone, ruoli e tabelle collegate allo schema presente nel progetto:

- `persone`
- `ruoli`
- `permessi`
- `stazioni`
- `persone_ruoli`
- `ruolo_stazione_permesso`

## Stack Tecnologico

- **Backend**: Python 3 + Flask
- **ORM**: Flask-SQLAlchemy / SQLAlchemy
- **Database**: database esterno tramite `DATABASE_URL` oppure variabili MySQL dedicate; in assenza di configurazione viene usato SQLite locale solo come fallback
- **Frontend**: HTML, Jinja2, CSS

## Struttura del Progetto

```text
CsecurityMES/
├── webapp.py
├── modelli.py
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── user_management.html
│   └── role_management.html
└── README.md
```

## Schema Dati

- `persone`: anagrafica utenti con `nome`, `cognome`, `username`, `password`
- `ruoli`: descrizioni dei ruoli
- `permessi`: catalogo permessi
- `stazioni`: elenco stazioni
- `persone_ruoli`: associazione molti-a-molti tra persone e ruoli
- `ruolo_stazione_permesso`: associazione tra ruolo, stazione e permesso

## Installazione

### Prerequisiti

- Python 3.7+
- pip

### Setup

1. Attiva il virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

1. Installa i requisiti:

```powershell
pip install -r requirements.txt
```

1. Configura il database MySQL tramite `.env` o variabili d'ambiente.

   Esempio:

   ```env
   DATABASE_URL=mysql+pymysql://utente:password@localhost:3306/gestione_accessi
   ```

   In alternativa puoi impostare `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` e, se serve, `MYSQL_PORT`.

1. Avvia l'applicazione:

```powershell
python webapp.py
```

L'applicazione sarà disponibile su `http://localhost:5000`.

## Accesso di Default

- **Username**: `admin`
- **Password**: `password`

## Note Database

- L'app legge automaticamente le variabili da un file `.env` se presente.
- Se `DATABASE_URL` è impostata, l'app usa quel database.
- Se non c'è `DATABASE_URL`, ma sono presenti `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD` e `MYSQL_DATABASE`, costruisce la connessione MySQL automaticamente.
- In assenza di configurazione MySQL, viene usato il file SQLite locale `gestione_accessi.db`.
- Alla prima esecuzione vengono creati automaticamente le tabelle e un utente admin di test.

## Rotte Disponibili

- `/` - Login
- `/dashboard` - Dashboard principale
- `/user-management` - Gestione persone
- `/role-management` - Gestione ruoli
- `/logout` - Logout

## Sicurezza

Per l'uso in produzione conviene:

- usare password hashate
- definire una `secret_key` sicura
- usare HTTPS
- validare input e proteggere i form con CSRF
