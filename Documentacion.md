                                       Introducción

Este proyecto es una aplicación web construida con **Flask** para gestionar el lavado de vehículos, incluyendo el registro de usuarios, vehículos, pagos y la gestión de estados de lavado. La aplicación utiliza **PostgreSQL** como sistema de base de datos y **SQLAlchemy** como ORM (Object Relational Mapper) para interactuar con la base de datos.

Requisitos

Para ejecutar este proyecto, necesitas tener los siguientes requisitos previos:

- **Python 3.x** o superior
- **PostgreSQL** (para la base de datos)
- **pip** (para la instalación de paquetes)
- **Virtualenv** (opcional, pero recomendado para gestionar las dependencias)


Configuración del Entorno de Desarrollo

Crear un Entorno Virtual

Para evitar conflictos con otras aplicaciones Python en tu sistema, es recomendable crear un entorno virtual.

Crea un entorno virtual con el siguiente comando:

                     ```bash
                  python3 -m venv venv

Instala las dependencias con el siguiente comando:

               pip install -r requirements.txt

Ejecutar la Aplicación

Para ejecutar la aplicación de forma local en tu máquina, sigue estos pasos:

Configura la clave secreta de Flask (para gestionar las sesiones y la seguridad). Asegúrate de cambiarla por una clave más segura en producción:

                      python
               app.secret_key = "supersecretkey"



Ejecuta el servidor de Flask con el siguiente comando:


                         python my_program.py
Abre tu navegador y visita http://localhost:5000 para interactuar con la aplicación.

                   Estructura de Archivos

                  /project_root
                  /my_program.py               # Archivo principal con la lógica de la aplicación
                  /templates/           # Archivos HTML de la interfaz de usuario
                  /static/              # Archivos estáticos (CSS, JS, imágenes)
                  /requirements.txt     # Lista de dependencias
                  /Procfile             # Configuración de despliegue en Render






                                   
                                   Conclusión
Este proyecto proporciona un sistema de gestión de lavados de vehículos fácil de usar, con características de autenticación, gestión de vehículos y pagos, y una interfaz de usuario basada en Flask y PostgreSQL. Está diseñado para ser flexible y puede adaptarse a varios entornos de despliegue, como servidores locales o plataformas en la nube como Render






%% Diagrama: Arquitectura del Sistema

```mermaid
flowchart TD
    A["Navegador (Frontend)"] -->|Solicitudes HTTP| B["Aplicación Flask (Backend)"]
    B --> C["Base de Datos (PostgreSQL)"]
    B --> D["Rutas y Controladores"]
    B --> E["Modelos (SQLAlchemy)"]
    B --> F["Base de Datos (Usuarios, Vehículos, Pagos)"]

```






%% Diagrama: Flujo de Inicio de Sesión

```mermaid
flowchart TD
    A[Ingreso de credenciales] --> B{¿Usuario y contraseña correctos?}
    B -->|Sí| C[Acceso permitido]
    B -->|No| D[Error: Usuario o contraseña incorrectos]
    C --> E[Redirigir a menú]
    D --> E

```






%% Diagrama: Registro de Vehículo


```mermaid
flowchart TD
    A[Ingresar datos del vehículo] --> B{¿Tipo de lavado válido?}
    B -->|Sí| C[Registrar vehículo]
    B -->|No| D[Error: Tipo de lavado no válido]
    C --> E[Vehículo registrado con éxito]
    D --> E
```






%% Diagrama: Finalización de Vehículo

```mermaid
flowchart TD
    A[Administrador o Usuario propietario accede a la opción de finalizar] --> B{¿Es el propietario o admin?}
    B -->|Sí| C[Finalizar vehículo]
    B -->|No| D[Error: Sin permiso para finalizar]
    C --> E[Vehículo marcado como finalizado]
    D --> E
```





%% Diagrama: Configuración del Entorno

```mermaid
flowchart TD
    A[Crear entorno virtual] --> B[Instalar dependencias]
    B --> C[Configurar base de datos PostgreSQL]
    C --> D[Configurar Flask con URI de la base de datos]
    D --> E[Configurar la clave secreta de Flask]
    E --> F[Instalar Gunicorn]
    F --> G[Crear un archivo Procfile]
    G --> H[Subir a Render]
    H --> I[Realizar migraciones de base de datos]
    I --> J[Abrir la aplicación en el navegador]
```



%% Diagrama: Modelo de Datos

```mermaid

erDiagram
    USUARIO {
        int id PK
        string nombre
        string password
        string correo
        string ciudad
        boolean es_admin
    }
    VEHICULO {
        int id PK
        string modelo
        string chapa
        string tipo_lavado
        string estado
        int precio
        datetime hora
        datetime hora_finalizacion
        int usuario_id FK
    }
    PAGO {
        int id PK
        int vehiculo_id FK
        string tipo_lavado
        int precio
        string chapa
        string tipo_pago
    }

    USUARIO ||--o| VEHICULO : "Tiene"
    VEHICULO ||--o| PAGO : "Genera"
```








%% Diagrama: Interacción Completa del Sistema
```mermaid

flowchart LR
    A["Usuario interactúa con la aplicación"] --> B["Navegador (Frontend)"]
    B --> C["Envío de solicitudes HTTP (GET, POST)"]
    C --> D["Aplicación Flask (Backend)"]
    D --> E["Base de datos PostgreSQL"]
    D --> F["Procesamiento de lógica (rutas, controladores)"]
    F --> G["Modelos de datos (SQLAlchemy)"]
    G --> E
    G --> H["Generación de respuestas (HTML, JSON)"]
    H --> B
    B --> I["Usuario recibe respuesta"]
    I --> J["Interacción con la aplicación (Ver menú, registrar vehículo, etc.)"]
    J --> B
```



