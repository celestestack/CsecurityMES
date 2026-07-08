import os
import secrets
import string
from urllib.parse import quote_plus

from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from sqlalchemy import inspect, text

from modelli import Persona, Ruolo, db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)

app = Flask(__name__)
app.secret_key = 'password'

def get_database_uri():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    mysql_host = os.getenv('MYSQL_HOST')
    mysql_user = os.getenv('MYSQL_USER')
    mysql_password = os.getenv('MYSQL_PASSWORD')
    mysql_database = os.getenv('MYSQL_DATABASE')

    if all([mysql_host, mysql_user, mysql_password, mysql_database]):
        mysql_port = os.getenv('MYSQL_PORT', '3306')
        return (
            'mysql+pymysql://'
            f'{quote_plus(mysql_user)}:{quote_plus(mysql_password)}'
            f'@{mysql_host}:{mysql_port}/{mysql_database}'
        )

    return 'sqlite:///gestione_accessi.db'


# Configurazione Database: priorità a DATABASE_URL, poi variabili MySQL, infine SQLite locale
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def generate_strong_password(length=14):
    alphabet = string.ascii_letters + string.digits + '!@#$%&*?-_'
    required = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice('!@#$%&*?-_'),
    ]
    required.extend(secrets.choice(alphabet) for _ in range(length - len(required)))
    secrets.SystemRandom().shuffle(required)
    return ''.join(required)


def split_display_name(username):
    parts = username.replace('.', ' ').replace('_', ' ').split()
    if not parts:
        return username, '-'
    nome = parts[0].capitalize()
    cognome = ' '.join(part.capitalize() for part in parts[1:]) or '-'
    return nome, cognome


def ensure_database_schema():
    inspector = inspect(db.engine)
    columns = {column['name'] for column in inspector.get_columns('persone')}
    if 'telefono' not in columns:
        db.session.execute(text('ALTER TABLE persone ADD COLUMN telefono VARCHAR(30) NULL'))
        db.session.commit()


def require_login():
    """Controlla se l'utente è autenticato. Se no, restituisce un redirect alla pagina di login."""
    if 'persona_id' not in session:
        flash('Effettua prima il login.', 'danger')
        return redirect(url_for('login'))
    return None


def get_logged_persona():
    """Restituisce l'oggetto Persona dell'utente attualmente loggato."""
    persona_id = session.get('persona_id')
    if persona_id:
        return Persona.query.get(persona_id)
    return None


@app.route('/')
def index():
    if 'persona_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        persona = Persona.query.filter_by(username=username, password=password).first()
        if not persona and password[:1] in ("'", '"'):
            persona = Persona.query.filter_by(username=username, password=password[1:]).first()

        if persona:
            # Imposta le variabili temporanee di pre-autenticazione
            session['pre_auth_persona_id'] = persona.id_persona
            session['pre_auth_username'] = persona.username
            session['pre_auth_display_name'] = f'{persona.nome} {persona.cognome}'.strip()
            
            # Indirizza l'utente alla schermata del codice 2FA
            return redirect(url_for('verify_2fa_page'))

        flash('Credenziali non valide!', 'danger')

    return render_template('login.html')


@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa_page():
    # Impedisce l'accesso alla pagina se l'utente non ha superato il primo step di login
    if 'pre_auth_persona_id' not in session:
        flash('Effettua prima il login.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Recupera i singoli caratteri inseriti nel form
        digit1 = request.form.get('otp1', '')
        digit2 = request.form.get('otp2', '')
        digit3 = request.form.get('otp3', '')
        digit4 = request.form.get('otp4', '')
        
        codice_inserito = f"{digit1}{digit2}{digit3}{digit4}"
        FALSO_CODICE_OTP = "0000"

        if codice_inserito == FALSO_CODICE_OTP:
            # Codice corretto: promuove la sessione a definitiva
            session['persona_id'] = session.pop('pre_auth_persona_id')
            session['username'] = session.pop('pre_auth_username')
            session['display_name'] = session.pop('pre_auth_display_name')
            return redirect(url_for('dashboard'))
        else:
            flash('Codice di verifica non valido! Riprova usando 0000.', 'danger')

    return render_template('verify_2fa.html')


@app.route('/dashboard')
def dashboard():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response

    persona = get_logged_persona()
    return render_template('dashboard.html', persona=persona, ruoli=persona.ruoli if persona else [])


@app.route('/user-management')
def user_management():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response

    persone = Persona.query.order_by(Persona.id_persona).all()
    ruoli = Ruolo.query.order_by(Ruolo.descrizione).all()
    generated_password = generate_strong_password()
    return render_template(
        'user_management.html',
        persone=persone,
        users=persone,
        ruoli=ruoli,
        generated_password=generated_password,
    )


@app.route('/user-management/create', methods=['POST'])
def create_user():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response

    username = request.form.get('username', '').strip()
    telefono = request.form.get('telefono', '').strip()
    password = request.form.get('password', '').strip() or generate_strong_password()
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    role_ids = request.form.getlist('ruoli')

    if not username or not telefono:
        flash('Nome utente e numero di telefono sono obbligatori.', 'danger')
        return redirect(url_for('user_management'))

    if Persona.query.filter_by(username=username).first():
        flash('Nome utente gia presente nel database.', 'danger')
        return redirect(url_for('user_management'))

    if not nome or not cognome:
        auto_nome, auto_cognome = split_display_name(username)
        nome = nome or auto_nome
        cognome = cognome or auto_cognome

    persona = Persona(
        nome=nome,
        cognome=cognome,
        username=username,
        password=password,
        telefono=telefono,
    )
    persona.ruoli = Ruolo.query.filter(Ruolo.id_ruolo.in_(role_ids)).all() if role_ids else []
    db.session.add(persona)
    db.session.commit()
    flash(f'Utente {username} creato. Password iniziale: {password}', 'success')
    return redirect(url_for('user_management'))


@app.route('/user-management/<int:persona_id>/edit', methods=['POST'])
def edit_user(persona_id):
    redirect_response = require_login()
    if redirect_response:
        return redirect_response

    persona = Persona.query.get_or_404(persona_id)
    username = request.form.get('username', '').strip()
    telefono = request.form.get('telefono', '').strip()
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    password = request.form.get('password', '').strip()
    role_ids = request.form.getlist('ruoli')

    if not username or not telefono:
        flash('Nome utente e numero di telefono sono obbligatori.', 'danger')
        return redirect(url_for('user_management'))

    duplicate = Persona.query.filter(Persona.username == username, Persona.id_persona != persona.id_persona).first()
    if duplicate:
        flash('Nome utente gia assegnato a un altro utente.', 'danger')
        return redirect(url_for('user_management'))

    persona.username = username
    persona.telefono = telefono
    persona.nome = nome or persona.nome
    persona.cognome = cognome or persona.cognome
    if password:
        persona.password = password
    persona.ruoli = Ruolo.query.filter(Ruolo.id_ruolo.in_(role_ids)).all() if role_ids else []

    db.session.commit()
    flash(f'Utente {persona.username} aggiornato.', 'success')
    return redirect(url_for('user_management'))


@app.route('/role-management')
def role_management():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response

    ruoli = Ruolo.query.order_by(Ruolo.id_ruolo).all()
    return render_template('role_management.html', roles=ruoli)


@app.route('/movement')
def movement():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response

    return render_template('movement.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout effettuato con successo.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea le tabelle se non esistono (valido principalmente per SQLite locale)
        ensure_database_schema()
    app.run(debug=True, host='0.0.0.0', port=5000)
