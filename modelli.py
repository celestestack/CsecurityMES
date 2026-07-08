from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

persone_ruoli = db.Table(
    'persone_ruoli',
    db.Column('id_persona', db.Integer, db.ForeignKey('persone.id_persona', ondelete='CASCADE'), primary_key=True),
    db.Column('id_ruolo', db.Integer, db.ForeignKey('ruoli.id_ruolo', ondelete='CASCADE'), primary_key=True),
)


class Persona(db.Model):
    __tablename__ = 'persone'

    id_persona = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cognome = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(30), nullable=True)

    ruoli = db.relationship('Ruolo', secondary=persone_ruoli, back_populates='persone')
    log_movimenti = db.relationship('LogMovimentoUtente', back_populates='persona')


class Ruolo(db.Model):
    __tablename__ = 'ruoli'

    id_ruolo = db.Column(db.Integer, primary_key=True)
    descrizione = db.Column(db.String(100), nullable=False)

    persone = db.relationship('Persona', secondary=persone_ruoli, back_populates='ruoli')
    assegnazioni = db.relationship('RuoloStazionePermesso', back_populates='ruolo', cascade='all, delete-orphan')


class Permesso(db.Model):
    __tablename__ = 'permessi'

    id_permesso = db.Column(db.Integer, primary_key=True)
    nome_permesso = db.Column(db.String(50), nullable=False, unique=True)

    assegnazioni = db.relationship('RuoloStazionePermesso', back_populates='permesso', cascade='all, delete-orphan')


class Stazione(db.Model):
    __tablename__ = 'stazioni'

    id_stazione = db.Column(db.Integer, primary_key=True)
    descrizione = db.Column(db.String(100), nullable=False)

    assegnazioni = db.relationship('RuoloStazionePermesso', back_populates='stazione', cascade='all, delete-orphan')


class RuoloStazionePermesso(db.Model):
    __tablename__ = 'ruolo_stazione_permesso'

    id_assegnazione = db.Column(db.Integer, primary_key=True)
    id_ruolo = db.Column(db.Integer, db.ForeignKey('ruoli.id_ruolo', ondelete='CASCADE'), nullable=False)
    id_stazione = db.Column(db.Integer, db.ForeignKey('stazioni.id_stazione', ondelete='CASCADE'), nullable=False)
    id_permesso = db.Column(db.Integer, db.ForeignKey('permessi.id_permesso', ondelete='CASCADE'), nullable=False)

    ruolo = db.relationship('Ruolo', back_populates='assegnazioni')
    stazione = db.relationship('Stazione', back_populates='assegnazioni')
    permesso = db.relationship('Permesso', back_populates='assegnazioni')


class LogMovimentoUtente(db.Model):
    __tablename__ = 'log_movimenti_utenti'

    id_log = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persone.id_persona', ondelete='SET NULL'), nullable=True)
    username = db.Column(db.String(50), nullable=False)
    categoria = db.Column(db.String(30), nullable=False)
    esito = db.Column(db.String(20), nullable=False)
    azione = db.Column(db.String(100), nullable=False)
    dettaglio = db.Column(db.String(255), nullable=False)
    indirizzo_ip = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

    persona = db.relationship('Persona', back_populates='log_movimenti')
