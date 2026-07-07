# CsecurityMES

Applicazione Flask per la gestione degli accessi, costruita sullo schema relazionale del dump MySQL `gestione_accessi`.

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
- **Database**: SQLite locale di default, oppure database esterno tramite `DATABASE_URL`
- **Frontend**: HTML, Jinja2, CSS

## Struttura del Progetto

```
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

2. Installa i requisiti:
```powershell
pip install -r requirements.txt
```

3. Avvia l'applicazione:
```powershell
python webapp.py
```

L'applicazione sarà disponibile su `http://localhost:5000`.

## Accesso di Default

- **Username**: `admin`
- **Password**: `password`

## Note Database

- Se `DATABASE_URL` è impostata, l'app prova a usare quel database.
- In assenza di `DATABASE_URL`, viene creato un file SQLite locale `gestione_accessi.db`.
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
