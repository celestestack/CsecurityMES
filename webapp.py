import os
from urllib.parse import quote_plus

from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

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


# Configurazione Database: priorita a DATABASE_URL, poi variabili MySQL, infine SQLite locale
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.before_request
def create_tables():
    db.create_all()

    if not Ruolo.query.first():
        ruoli_iniziali = [
            Ruolo(id_ruolo=1, descrizione="Instructor - system administrator"),
            Ruolo(id_ruolo=2, descrizione="Production manager - planning and preparation of orders"),
            Ruolo(id_ruolo=3, descrizione="Maintenance responsible - maintenance of stations and components"),
            Ruolo(id_ruolo=4, descrizione="Quality manager - quality verification and statistical control"),
            Ruolo(id_ruolo=5, descrizione="Logistics - warehouse and stock management"),
            Ruolo(id_ruolo=6, descrizione="Client - order creation and monitoring"),
            Ruolo(id_ruolo=7, descrizione="Operator - interaction with stations and alarms"),
            Ruolo(id_ruolo=8, descrizione="Guest - role used for visits"),
        ]
        db.session.bulk_save_objects(ruoli_iniziali)
        db.session.commit()

    if not Persona.query.filter_by(username='admin').first():
        admin_user = Persona(nome='Admin', cognome='Sistema', username='admin', password='password')
        first_role = Ruolo.query.filter_by(id_ruolo=1).first()
        if first_role:
            admin_user.ruoli.append(first_role)
        db.session.add(admin_user)
        db.session.commit()


def require_login():
    if 'persona_id' not in session:
        return redirect(url_for('login'))
    return None


def get_logged_persona():
    persona_id = session.get('persona_id')
    if not persona_id:
        return None
    return db.session.get(Persona, persona_id)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        persona = Persona.query.filter_by(username=username, password=password).first()
        if persona:
            session['persona_id'] = persona.id_persona
            session['username'] = persona.username
            session['display_name'] = f'{persona.nome} {persona.cognome}'.strip()
            return redirect(url_for('dashboard'))

        flash('Credenziali non valide!', 'danger')

    return render_template('login.html')


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
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)