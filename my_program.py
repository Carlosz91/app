from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import hashlib
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Cambia esto en producción

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lavado:o70OQQ6APLzF1Va6qCYYi96UupQlHq90@dpg-ct8rbht2ng1s739pq72g-a/lavado_blq2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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
    hora = db.Column(db.DateTime, default=datetime.now)  # Cambiar a DateTime
    hora_finalizacion = db.Column(db.DateTime)  # También DateTime
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('vehiculos', lazy=True))

# Modelo para Pagos
class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculo.id'), nullable=False)
    tipo_lavado = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    chapa = db.Column(db.String(10), nullable=False)
    tipo_pago = db.Column(db.String(50), nullable=False)


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
            usuario_id=usuario_id,
            hora=datetime.now()
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
    # Verifica si el vehículo existe
    if not vehiculo:
        flash("Vehículo no encontrado.")
        return redirect(url_for('estado_lavado'))
    
    # Permitir que un administrador finalice el vehículo, o un usuario normal solo si es su vehículo
    if vehiculo.usuario_id == session['usuario_id'] or is_admin(session['usuario_id']):
        vehiculo.estado = 'Finalizado'
        
        # Obtener la hora actual correctamente
        hora_actual = datetime.now().time()
        vehiculo.hora_finalizacion = datetime.combine(date.today(), hora_actual)
        
        db.session.commit()
        flash("Vehículo finalizado con éxito.")
    else:
        flash("No tienes permiso para finalizar este vehículo.")
    
    return redirect(url_for('estado_lavado'))
    
# Ruta para los pagos
@app.route('/pagos', methods=['GET', 'POST'])
def pagos():
    # Verifica que el usuario esté autenticado
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('login'))  # Si no está autenticado, redirige al login

    # Obtener los vehículos asociados al usuario autenticado
    vehiculos = Vehiculo.query.filter_by(usuario_id=usuario_id).all()

    # Si el formulario es enviado
    if request.method == 'POST':
        vehiculo_id = request.form['vehiculo_id']
        tipo_pago = request.form['tipo_pago']
        # Aquí puedes agregar la lógica para procesar el pago (tarjeta, transferencia)
        return redirect(url_for('confirmacion_pago'))  # Redirige a una página de confirmación de pago

    # Renderizar la plantilla con los vehículos del usuario
    return render_template('pagos.html', vehiculos=vehiculos)

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

@app.route('/admin/pagos', methods=['GET', 'POST'])
@login_requerido
def admin_pagos():
    if not is_admin(session['usuario_id']):
        flash("No tienes permiso para acceder a esta página.")
        return redirect(url_for('menu'))

    if request.method == 'POST':
        # Procesar el formulario de pago
        vehiculo_id = request.form.get('vehiculo')
        tipo_pago = request.form.get('tipo_pago')

        if not vehiculo_id or not tipo_pago:
            flash("Por favor, selecciona un vehículo y un tipo de pago.")
            return redirect(url_for('admin_pagos'))

        try:
            # Obtener datos del vehículo
            vehiculo = Vehiculo.query.get(vehiculo_id)

            if vehiculo:
                # Lógica de registro del pago (puedes adaptarla según tu sistema)
                nuevo_pago = Pago(
                    vehiculo_id=vehiculo.id,
                    tipo_lavado=vehiculo.tipo_lavado,
                    precio=vehiculo.precio,
                    chapa=vehiculo.chapa,
                    tipo_pago=tipo_pago
                )
                db.session.add(nuevo_pago)
                db.session.commit()
                flash("Pago registrado exitosamente.")
            else:
                flash("Vehículo no encontrado.")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al procesar el pago: {e}")
        return redirect(url_for('admin_pagos'))

    try:
        # Consultar los pagos registrados
        pagos = Pago.query.with_entities(
            Pago.id, Pago.tipo_lavado, Pago.precio, Pago.chapa
        ).all()

        # Consultar los vehículos disponibles
        vehiculos = Vehiculo.query.with_entities(
            Vehiculo.id, Vehiculo.modelo, Vehiculo.chapa, Vehiculo.tipo_lavado, Vehiculo.precio
        ).all()

    except Exception as e:
        flash(f"Error al recuperar los datos: {e}")
        pagos = []
        vehiculos = []

    return render_template('admin_pagos.html', pagos=pagos, vehiculos=vehiculos)




@app.route('/admin/reportes', methods=['GET'])
@login_requerido
def admin_reportes():
    if not is_admin(session['usuario_id']):
        flash("No tienes permiso para acceder a esta página.")
        return redirect(url_for('menu'))
    
    cantidad_vehiculos = Vehiculo.query.count()
    return render_template('admin_reportes.html', cantidad_vehiculos=cantidad_vehiculos)

@app.route('/admin/reportes/lavados', methods=['GET'])
@login_requerido
def admin_reportes_lavados():
    if not is_admin(session['usuario_id']):
        flash("No tienes permiso para acceder a esta página.")
        return redirect(url_for('menu'))
    
    lavados = Vehiculo.query.all()  
    
    print(f"Número de lavados: {len(lavados)}")  # Verifica los registros
    return render_template('admin_reportes_lavados.html', lavados=lavados)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))  # Si Render asigna un puerto dinámico
    app.run(host='0.0.0.0', port=port, debug=True)
