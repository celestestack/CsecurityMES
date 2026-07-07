# CsecurityMES

Sistema di gestione della sicurezza e dei ruoli per ambienti Manufacturing Execution System (MES).

## Descrizione

CsecurityMES è un'applicazione web Flask per la gestione centralizzata di utenti e ruoli in un sistema MES. L'applicazione fornisce:

- **Autenticazione**: Sistema di login sicuro con gestione delle sessioni
- **Gestione Ruoli**: 8 ruoli predefiniti con permessi specifici (Instructor, Production Manager, Maintenance Responsible, Quality Manager, Logistics, Client, Operator, Guest)
- **Gestione Utenti**: Interfaccia per la creazione e gestione degli utenti del sistema
- **Dashboard**: Pagina principale con informazioni di sistema
- **Database Integrato**: SQLite locale per lo sviluppo

## Stack Tecnologico

- **Backend**: Python 3 + Flask
- **Database**: SQLite (file locale `sifmes_sim.db`)
- **Frontend**: HTML, CSS, Jinja2 templates
- **ORM**: SQLAlchemy via Flask-SQLAlchemy

## Struttura del Progetto

```
CsecurityMES/
├── webapp.py                 # Applicazione principale Flask
├── modelli.py               # Modelli database (User, Role)
├── style.css                # Foglio di stile globale
├── templates/               # Template HTML
│   ├── login.html          # Pagina di login
│   ├── dashboard.html      # Dashboard principale
│   ├── user_management.html # Gestione utenti
│   └── role_management.html # Gestione ruoli
└── README.md
```

## Ruoli Disponibili

1. **Instructor** - Amministratore di sistema. Permessi per gestire utenti e ruoli, generare disturbi ed eseguire esercizi
2. **Production Manager** - Pianificazione e preparazione ordini
3. **Maintenance Responsible** - Manutenzione stazioni e componenti
4. **Quality Manager** - Verifica qualità e processi di controllo statistico
5. **Logistics** - Gestione magazzino
6. **Client** - Creazione e monitoraggio ordini
7. **Operator** - Interazione con stazioni e visualizzazione allarmi
8. **Guest** - Ruolo per visite

## Installazione

### Prerequisiti
- Python 3.7+
- pip

### Setup

1. Installare le dipendenze:
```bash
pip install flask flask-sqlalchemy
```

2. Eseguire l'applicazione:
```bash
python webapp.py
```

L'applicazione sarà disponibile su `http://localhost:5000`

## Credenziali di Default

- **Username**: `admin`
- **Password**: `password`

⚠️ **Nota Importante**: Queste sono credenziali di default solo per lo sviluppo. Cambiarle in produzione!

## Rotte Disponibili

- `/` - Login
- `/dashboard` - Dashboard principale (richiede autenticazione)
- `/user-management` - Gestione utenti
- `/role-management` - Gestione ruoli
- `/logout` - Logout

## Database

Il database SQLite viene creato automaticamente alla prima esecuzione con i ruoli e l'utente admin precaricati.

File database: `sifmes_sim.db` (creato localmente)

## Sicurezza

⚠️ **IMPORTANTE**: Questo progetto è in fase di sviluppo. Per la produzione:
- Implementare hashing delle password (es. Werkzeug)
- Usare una chiave segreta sicura (non quella di default)
- Implementare HTTPS
- Usare un database robusto (PostgreSQL, MySQL)
- Aggiungere validazione dei dati e protezione CSRF

## Autore

Progetto Galligani