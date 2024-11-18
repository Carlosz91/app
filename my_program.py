from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
from functools import wraps
import os
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Cambia esto en producción

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lavado_1bwn_user:ivaJCbDZ42Zyuh923g6tx8KenVFDlR2I@dpg-cstjrul6l47c73elu51g-a/lavado_1bwn'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Inicialización de migraciones
migrate = Migrate(app, db)

# Modelo para Usuarios
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Aumentar longitud para bcrypt
    correo = db.Column(db.String(120), nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)  # Campo para verificar si es administrador

# Modelo para Vehículos
class Vehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(50), nullable=False)
    chapa = db.Column(db.String(10), nullable=False)
    tipo_lavado = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(20), default="En Curso")
    precio = db.Column(db.Integer, nullable=False)
    hora = db.Column(db.String(5), default=datetime.now().strftime("%H:%M"))  # Hora como cadena HH:MM
    hora_finalizacion = db.Column(db.DateTime, nullable=True)  # Use DateTime for finalization time
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('vehiculos', lazy=True))

# Función para hashear contraseñas
def hashear_contrasena(contrasena):
    return hashlib.sha256(contrasena.encode()).hexdigest()

# Decorador para proteger rutas
def login_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Inicia sesión para acceder a esta página.")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorador

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    usuario = request.form['usuario']
    password = request.form['password']
    usuario_db = Usuario.query.filter_by(nombre=usuario).first()
    if usuario_db and usuario_db.password == hashear_contrasena(password):
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
    admin = is_admin(session['usuario_id'])  # Verifica si el usuario es admin
    if admin:
        vehiculos_en_curso = Vehiculo.query.filter_by(estado='En Curso').all()
        vehiculos_finalizados = Vehiculo.query.filter_by(estado='Finalizado').all()
    else:
        usuario_id = session['usuario_id']
        vehiculos_en_curso = Vehiculo.query.filter_by(estado='En Curso', usuario_id=usuario_id).all()
        vehiculos_finalizados = Vehiculo.query.filter_by(estado='Finalizado', usuario_id=usuario_id).all()

    return render_template('estado_lavado.html', 
                           vehiculos_en_curso=vehiculos_en_curso, 
                           vehiculos_finalizados=vehiculos_finalizados,
                           es_admin=admin)  # Pasa la variable es_admin a la plantilla

@app.route('/finalizar_vehiculo/<int:id>', methods=['POST'])
@login_requerido
def finalizar_vehiculo(id):
    vehiculo = Vehiculo.query.get(id)
    
    if not vehiculo:
        flash("Vehículo no encontrado.")
        return redirect(url_for('estado_lavado'))

    if vehiculo.usuario_id == session['usuario_id'] or is_admin(session['usuario_id']):
        vehiculo.estado = 'Finalizado'
        
        # Set finalization time to current time
        vehiculo.hora_finalizacion = datetime.now()

        db.session.commit()
        
        flash("Vehículo finalizado con éxito.")
    else:
        flash("No tienes permiso para finalizar este vehículo.")
    
    return redirect(url_for('estado_lavado'))



@app.route('/pagos')
@login_requerido
def pagos():
    return render_template('pagos.html')

@app.route('/olvide_contrasena', methods=['GET', 'POST'])
def olvide_contrasena():
    if request.method == 'POST':
        correo = request.form['correo']
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario:
            flash(f"Instrucciones enviadas a {correo} (simulado).")
            return redirect(url_for('index'))
        else:
            flash("Correo no encontrado.")
    return render_template('olvide_contrasena.html')

@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.pop('usuario_id', None)
    flash("Sesión cerrada.")
    return redirect(url_for('index'))

# Rutas de administración
def is_admin(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    return usuario.es_admin if usuario else False

@app.route('/admin/vehiculos', methods=['GET'])
@login_requerido
def admin_vehiculos():
    if not is_admin(session['usuario_id']):
        flash("No tienes permiso para acceder a esta página.")
        return redirect(url_for('menu'))
    
    vehiculos = Vehiculo.query.all()  # Obtener todos los vehículos registrados
    return render_template('admin_vehiculos.html', vehiculos=vehiculos)

@app.route('/admin/pagos', methods=['GET'])
@login_requerido
def admin_pagos():
    if not is_admin(session['usuario_id']):
        flash("No tienes permiso para acceder a esta página.")
        return redirect(url_for('menu'))
    
    # Obtener solo los datos necesarios de cada vehículo
    pagos = Vehiculo.query.with_entities(Vehiculo.id, Vehiculo.tipo_lavado, Vehiculo.precio, Vehiculo.chapa).all()
    
    return render_template('admin_pagos.html', pagos=pagos)

@app.route('/admin/reportes', methods=['GET'])
@login_requerido
def admin_reportes():
    if not is_admin(session['usuario_id']):
        flash("No tienes permiso para acceder a esta página.")
        return redirect(url_for('menu'))
    
    # Generar reportes según los criterios que necesites
    vehiculos = Vehiculo.query.all()  # Obtener todos los vehículos
    return render_template('admin_reportes.html', vehiculos=vehiculos)

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)
