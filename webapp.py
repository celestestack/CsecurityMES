from flask import Flask, render_template, request, redirect, url_for, session, flash
from CsecurityMES.modelli import db, User, Role

app = Flask(__name__)
app.secret_key = 'chiave_segreta_provvisoria'

# Configurazione Database SQLite locale
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sifmes_sim.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Popolamento iniziale del DB (eseguito solo la prima volta)
@app.before_request
def create_tables():
    db.create_all()
    if not Role.query.first():
        # Inseriamo i ruoli esattamente come da tua foto
        ruoli_iniziali = [
            Role(id=1, name="Instructor", description="System administrator. Permission to manage users and roles, generate disturbances and execute exercises..."),
            Role(id=2, name="Production manager", description="Planning and preparation of orders. Permission to manage and launch orders..."),
            Role(id=3, name="Maintenance responsible", description="Maintenance of stations and components. Permission to maintenance options."),
            Role(id=4, name="Quality manager", description="System quality verification. Permission to energy management and statistical control processes."),
            Role(id=5, name="Logistics", description="Warehouse management. Permission to stock management, warehouse management..."),
            Role(id=6, name="Client", description="Place orders. Permission to create his orders and monitor them."),
            Role(id=7, name="Operator", description="Interaction with stations. Permission to see alarms and system status."),
            Role(id=8, name="Guest", description="Role used for visits.")
        ]
        db.session.bulk_save_objects(ruoli_iniziali)
        
        # Un utente di test admin/admin
        admin_user = User(username="admin", password="password", role_id=1)
        db.session.add(admin_user)
        db.session.commit()

# --- ROTTE ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Credenziali non valide!', 'danger')
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/user-management')
def user_management():
    if 'user_id' not in session: return redirect(url_for('login'))
    # Per ora passiamo una lista vuota o finta, la collegheremo dopo al DB utenti
    users = User.query.all()
    return render_template('user_management.html', users=users)

@app.route('/role-management')
def role_management():
    if 'user_id' not in session: return redirect(url_for('login'))
    roles = Role.query.all()
    return render_template('role_management.html', roles=roles)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)