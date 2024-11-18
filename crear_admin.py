from werkzeug.security import generate_password_hash, check_password_hash
from my_program import app, db, Usuario  # Asegúrate de usar el nombre correcto de tu archivo principal

def crear_usuario_admin():
    nombre_admin = 'admin'
    password_admin = 'admin123'
    correo_admin = 'admin@example.com'
    ciudad_admin = 'Tu Ciudad'

    # Verificar si el usuario ya existe
    usuario_existente = Usuario.query.filter_by(nombre=nombre_admin).first()

    if not usuario_existente:
        # Usar generate_password_hash para el hash de la contraseña
        password_hash = generate_password_hash(password_admin)

        nuevo_admin = Usuario(
            nombre=nombre_admin,
            password=password_hash,  # Usar el hash generado
            correo=correo_admin,
            ciudad=ciudad_admin,
            es_admin=True
        )
        db.session.add(nuevo_admin)
        db.session.commit()
        print(f"Usuario administrador '{nombre_admin}' creado con éxito.")
    else:
        print("El usuario administrador ya existe.")

# Verificación de la contraseña al autenticar al usuario admin
def verificar_password_admin():
    usuario = Usuario.query.filter_by(nombre='admin').first()
    if usuario and check_password_hash(usuario.password, 'admin123'):  # Compara la contraseña
        print("Contraseña correcta")
    else:
        print("Contraseña incorrecta")

if __name__ == '__main__':
    with app.app_context():  # Asegúrate de que el contexto de la aplicación esté activo
        db.create_all()  # Esto asegura que las tablas estén creadas antes de intentar agregar un nuevo usuario
        crear_usuario_admin()
        verificar_password_admin()  # Verificación de la contraseña (solo para probar)
