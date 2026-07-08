import os
from urllib.parse import quote_plus

from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

from modelli import Persona, Ruolo, db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))\nload_dotenv(os.path.join(BASE_DIR, '.env'), override=True)

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
        username = request.form.get('username')
        password = request.form.get('password')

        persona = Persona.query.filter_by(username=username, password=password).first()
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
    return render_template('user_management.html', persone=persone, users=persone)


@app.route('/role-management')
def role_management():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response

    ruoli = Ruolo.query.order_by(Ruolo.id_ruolo).all()
    return render_template('role_management.html', roles=ruoli)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout effettuato con successo.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea le tabelle se non esistono (valido principalmente per SQLite locale)
    app.run(debug=True, host='0.0.0.0', port=5000)