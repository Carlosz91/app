from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import bcrypt
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Cambiar esto en producción

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lavado_1bwn_user:ivaJCbDZ42Zyuh923g6tx8KenVFDlR2I@dpg-cstjrul6l47c73elu51g-a/lavado_1bwn'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)

class Vehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(50), nullable=False)
    chapa = db.Column(db.String(10), nullable=False)
    tipo_lavado = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(20), default="En Curso")
    precio = db.Column(db.Integer, nullable=False)
    hora = db.Column(db.DateTime, default=datetime.now)
    hora_finalizacion = db.Column(db.DateTime)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False, index=True)
    usuario = db.relationship('Usuario', backref=db.backref('vehiculos', lazy='dynamic'))

# Utilidades de seguridad
def hashear_contrasena(contrasena):
    return bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verificar_contrasena(contrasena, hashed):
    return bcrypt.checkpw(contrasena.encode('utf-8'), hashed.encode('utf-8'))

# Decoradores
def login_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Inicia sesión para acceder a esta página.")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorador

def admin_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'usuario_id' not in session or not is_admin(session['usuario_id']):
            flash("No tienes permiso para acceder a esta página.")
            return redirect(url_for('menu'))
        return f(*args, **kwargs)
    return decorador

def is_admin(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    return usuario.es_admin if usuario else False

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    usuario = request.form['usuario']
    password = request.form['password']
    usuario_db = Usuario.query.filter_by(nombre=usuario).first()

    if usuario_db and verificar_contrasena(password, usuario_db.password):
        session['usuario_id'] = usuario_db.id
        flash("Inicio de sesión exitoso.")
        return redirect(url_for('menu'))
    else:
        flash("Usuario o contraseña incorrecta.")
        return redirect(url_for('index'))

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nombre = request.form['usuario']
        password = request.form['password']
        correo = request.form['correo']
        ciudad = request.form['ciudad']

        if not Usuario.query.filter_by(nombre=nombre).first():
            nuevo_usuario = Usuario(
                nombre=nombre,
                password=hashear_contrasena(password),
                correo=correo,
                ciudad=ciudad
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash("Usuario registrado con éxito.")
            return redirect(url_for('index'))
        else:
            flash("El usuario ya existe.")
    return render_template('registro.html')

@app.route('/menu')
@login_requerido
def menu():
    usuario_id = session['usuario_id']
    es_admin = is_admin(usuario_id)
    return render_template('menu.html', es_admin=es_admin)

@app.route('/registro_vehiculo', methods=['GET', 'POST'])
@login_requerido
def registro_vehiculo():
    if request.method == 'POST':
        modelo = request.form['modelo']
        chapa = request.form['chapa']
        tipo_lavado = request.form['tipo_lavado']
        usuario_id = session['usuario_id']

        precios = {
            "ducha y aspirado": 35000,
            "lavado completo": 50000
        }

        precio = precios.get(tipo_lavado)
        if precio is None:
            flash("Tipo de lavado no válido.")
            return redirect(url_for('registro_vehiculo'))

        nuevo_vehiculo = Vehiculo(
            modelo=modelo,
            chapa=chapa,
            tipo_lavado=tipo_lavado,
            precio=precio,
            usuario_id=usuario_id
        )
        db.session.add(nuevo_vehiculo)
        db.session.commit()
        flash("Vehículo registrado con éxito.")
        return redirect(url_for('menu'))

    return render_template('registro_vehiculo.html')

@app.route('/estado_lavado')
@login_requerido
def estado_lavado():
    admin = is_admin(session['usuario_id'])
    if admin:
        vehiculos = Vehiculo.query.all()
    else:
        usuario_id = session['usuario_id']
        vehiculos = Vehiculo.query.filter_by(usuario_id=usuario_id).all()
    
    return render_template('estado_lavado.html', vehiculos=vehiculos, es_admin=admin)

@app.route('/admin/reportes', methods=['GET'])
@admin_requerido
def admin_reportes():
    cantidad_vehiculos = Vehiculo.query.count()
    return render_template('admin_reportes.html', cantidad_vehiculos=cantidad_vehiculos)

@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.pop('usuario_id', None)
    flash("Sesión cerrada.")
    return redirect(url_for('index'))

# Inicialización
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

