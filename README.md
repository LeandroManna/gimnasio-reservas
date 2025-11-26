# 🏋️ Sistema de Reservas para Gimnasio

Sistema web completo de reservas de turnos para gimnasios de múltiples disciplinas. Desarrollado con Flask, MySQL y Bootstrap 5.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-5.7+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuracion](#️-configuracion)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API Endpoints](#-api-endpoints)
- [Changelog](#-changelog)
- [Seguridad](#-seguridad)
- [Licencia](#-licencia)
- [Autor](#-autor)
- [Contacto y Soporte](#-contacto-y-soporte)

---

## ✨ Características

### Para Clientes

- 🌐 **Reservas Online 24/7** - Reserva desde cualquier dispositivo
- 📅 **Calendario Semanal Interactivo** - Visualización clara de disponibilidad
- ⚡ **Verificación en Tiempo Real** - Ve cupos disponibles al instante
- 📱 **100% Responsive** - Diseñado para móviles, tablets y desktop
- 📄 **Carga de Comprobantes** - Sube tu comprobante de pago (opcional)
- 🔒 **Validación de DNI** - Prevención de reservas duplicadas
- 🚫 **Prevención de Horarios Pasados** - Solo reserva horarios futuros

### Para Administradores

- 🎛️ **Panel de Control Completo** - Dashboard con estadísticas
- 📊 **Gestión de Reservas** - Ver, buscar, eliminar y agregar reservas
- 🏋️ **ABM de Disciplinas** - Agregar, editar, activar/desactivar
- ⏰ **Gestión de Horarios** - Configurar días, horas y cupos por clase
- 👁️ **Visualización de Comprobantes** - Revisar pagos de clientes
- 🔍 **Búsqueda Avanzada** - Encuentra reservas por nombre o DNI
- 📈 **Estadísticas en Tiempo Real** - Total de reservas y disciplinas activas

---

## 🛠️ Tecnologias Utilizadas

### Backend

- **Python 3.8+** - Lenguaje de programación
- **Flask 3.0.0** - Framework web
- **Flask-MySQLdb** - Conexión MySQL
- **PyMySQL** - Driver MySQL alternativo
- **Werkzeug** - Seguridad y utilidades
- **Gunicorn** - Servidor WSGI para producción

### Frontend

- **Bootstrap 5** - Framework CSS responsive
- **Bootstrap Icons** - Iconografía
- **JavaScript Vanilla** - Interactividad
- **Jinja2** - Motor de templates

### Base de Datos

- **MySQL 5.7+** - Base de datos relacional
- **MariaDB** - Compatible

## 📦 Requisitos Previos

Antes de instalar, asegurate de tener:

- **Python 3.8 o superior**

  ```bash
  python --version
  ```

- **MySQL 5.7+ o MariaDB**

  ```bash
  mysql --version
  ```

- **pip** (gestor de paquetes de Python)

  ```bash
  pip --version
  ```

- **Git** (opcional, para clonar el repositorio)
  ```bash
  git --version
  ```

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/LeandroManna/gimnasio-reservas.git
cd gimnasio-reservas
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

**Crear base de datos:**

```bash
mysql -u root -p
```

```sql
CREATE DATABASE gimnasio_reservas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

**Importar estructura y datos de ejemplo:**

```bash
mysql -u root -p gimnasio_reservas < database.sql
```

### 5. Configurar Credenciales

Editá el archivo `app.py` y configurá tu conexión MySQL (líneas 26-28):

```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Tu usuario MySQL
app.config['MYSQL_PASSWORD'] = ''  # Tu contraseña MySQL
app.config['MYSQL_DB'] = 'gimnasio_reservas'
```

### 6. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

---

## ⚙️ Configuracion

### Configuración de Admin

**Credenciales por defecto:**

- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE:** Cambiá estas credenciales en producción.

**Generar nuevo hash de contraseña:**

```bash
python generate_password.py
```

Seguí las instrucciones para crear un usuario administrador seguro.

### Configuración de Uploads

Los comprobantes de pago se guardan en:

```
static/uploads/comprobantes/
```

**Límite de tamaño:** 5MB por archivo  
**Formatos permitidos:** JPG, PNG, PDF

---

## 📖 Uso

### Como Cliente

1. Abrí **http://localhost:5000**
2. Seleccioná una disciplina
3. Elegí día y horario en el calendario
4. Completá tus datos (Nombre, Apellido, DNI)
5. Opcionalmente subí tu comprobante de pago
6. Confirmá la reserva
7. Guardá tu número de confirmación

### Como Administrador

1. Accedé a **http://localhost:5000/admin/login**
2. Ingresá usuario y contraseña
3. Desde el dashboard podés:
   - Ver todas las reservas
   - Gestionar disciplinas
   - Configurar horarios
   - Ver estadísticas

---

## 📁 Estructura del Proyecto

```
gimnasio-reservas/
│
├── app.py                      # Aplicación principal Flask
├── database.sql                # Esquema y datos de ejemplo
├── requirements.txt            # Dependencias Python
├── generate_password.py        # Generador de hash de contraseña
├── README.md                   # Este archivo
├── .gitignore                  # Archivos ignorados por Git
│
├── static/
│   └── uploads/
│       └── comprobantes/      # Archivos subidos por clientes
│
└── templates/
    ├── base.html              # Template base
    ├── index.html             # Selección de disciplinas
    ├── reservar.html          # Sistema de calendario y reservas
    └── admin/
        ├── login.html         # Login administrador
        ├── dashboard.html     # Panel principal
        ├── disciplinas.html   # Gestión de disciplinas
        ├── horarios.html      # Gestión de horarios
        └── reservas.html      # Gestión de reservas
```

---

## 🔌 API Endpoints

### Rutas Públicas

| Método | Endpoint                                         | Descripción                               |
| ------ | ------------------------------------------------ | ----------------------------------------- |
| GET    | `/`                                              | Página principal - Listado de disciplinas |
| GET    | `/reservar/<int:disciplina_id>`                  | Vista de calendario para reservar         |
| GET    | `/check_disponibilidad/<int:horario_id>/<fecha>` | API para verificar cupos                  |
| POST   | `/confirmar_reserva`                             | Procesar y confirmar una reserva          |

### Rutas de Administrador

| Método   | Endpoint                                                        | Descripción                      |
| -------- | --------------------------------------------------------------- | -------------------------------- |
| GET/POST | `/admin/login`                                                  | Login del administrador          |
| GET      | `/admin/logout`                                                 | Cerrar sesión                    |
| GET      | `/admin/dashboard`                                              | Panel principal con estadísticas |
| GET      | `/admin/reservas`                                               | Listado de todas las reservas    |
| GET      | `/admin/reservas/eliminar/<int:id>`                             | Eliminar una reserva             |
| GET      | `/admin/disciplinas`                                            | Gestión de disciplinas           |
| POST     | `/admin/disciplinas/agregar`                                    | Agregar nueva disciplina         |
| GET      | `/admin/disciplinas/toggle/<int:id>`                            | Activar/Desactivar disciplina    |
| GET      | `/admin/disciplinas/eliminar/<int:id>`                          | Eliminar disciplina              |
| GET      | `/admin/horarios/<int:disciplina_id>`                           | Gestión de horarios              |
| POST     | `/admin/horarios/agregar/<int:disciplina_id>`                   | Agregar nuevo horario            |
| GET      | `/admin/horarios/eliminar/<int:horario_id>/<int:disciplina_id>` | Eliminar horario                 |

---

**Resumen rápido:**

```bash
# 1. Instalar dependencias del servidor
apt update && apt upgrade -y
apt install python3-pip python3-venv nginx mysql-server -y

# 2. Clonar proyecto
cd /var/www
git clone https://github.com/LeandroManna/gimnasio-reservas.git

# 3. Configurar entorno
cd gimnasio-reservas
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 4. Configurar MySQL e importar database.sql
```

### Variables de Entorno (Producción)

Creá un archivo `.env` (NO lo subas a Git):

```env
SECRET_KEY=tu_clave_super_secreta_de_produccion
MYSQL_HOST=localhost
MYSQL_USER=gimnasio_user
MYSQL_PASSWORD=password_segura
MYSQL_DB=gimnasio_reservas
```


## 📝 Changelog

### v1.0.0 (2024-11-24)

- ✨ Release inicial
- ✅ Sistema completo de reservas
- ✅ Panel de administración
- ✅ Control de cupos automático
- ✅ Prevención de horarios pasados
- ✅ Diseño responsive
- ✅ Carga de comprobantes

---

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con Werkzeug (scrypt)
- ✅ Sesiones seguras con Flask
- ✅ Validación de inputs (frontend y backend)
- ✅ Prevención de SQL Injection con queries parametrizadas
- ✅ Sanitización de nombres de archivo
- ✅ Límite de tamaño de uploads (5MB)
- ✅ Validación de tipos de archivo

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

**Leandro Manna**

- 📍 San Salvador de Jujuy, Argentina
- 💼 Programador & Técnico en Informática
- 🌐 Especializado en desarrollo web y automatización

---

## 📞 Contacto y Soporte

- 💼 **LinkedIn:** [Leandro Manna](https://linkedin.com/in/https://www.linkedin.com/in/leandro-manna-8ba809247)
- 🐙 **GitHub:** [@LeandroManna](https://github.com/LeandroManna)
- 📱 **WhatsApp:** [+54 3884695353](https://wa.me/543884695353)

---

## 🙏 Agradecimientos

- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Bootstrap](https://getbootstrap.com/) - Framework CSS
- [Bootstrap Icons](https://icons.getbootstrap.com/) - Iconografía
- Comunidad de desarrolladores de Python

---

## 📚 Recursos Adicionales

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de Bootstrap 5](https://getbootstrap.com/docs/5.0/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

---

<div align="center">

**⭐ Si te gustó este proyecto, dale una estrella en GitHub ⭐**

Hecho con ❤️ por [Leandro Manna](https://github.com/LeandroManna)

</div>
