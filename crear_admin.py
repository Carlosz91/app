import hashlib
from my_program import app, db, Usuario  # Asegúrate de usar el nombre correcto de tu archivo principal

def crear_usuario_admin():
    nombre_admin = 'admin'
    password_admin = 'admin123'
    correo_admin = 'admin@example.com'
    ciudad_admin = 'Tu Ciudad'

    # Verificar si el usuario ya existe
    usuario_existente = Usuario.query.filter_by(nombre=nombre_admin).first()

    if not usuario_existente:
        nuevo_admin = Usuario(
            nombre=nombre_admin,
            password=hashlib.sha256(password_admin.encode()).hexdigest(),
            correo=correo_admin,
            ciudad=ciudad_admin,
            es_admin=True
        )
        db.session.add(nuevo_admin)
        db.session.commit()
        print(f"Usuario administrador '{nombre_admin}' creado con éxito.")
    else:
        print("El usuario administrador ya existe.")
        


if __name__ == '__main__':
    with app.app_context():  # Asegúrate de que el contexto de la aplicación esté activo
        db.create_all()  # Esto asegura que las tablas estén creadas antes de intentar agregar un nuevo usuario
        crear_usuario_admin()
