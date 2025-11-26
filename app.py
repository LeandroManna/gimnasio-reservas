from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, time, timedelta
import os

# --- PyMySQL debe emular MySQLdb antes de cualquier importación MySQL ---
import pymysql
pymysql.install_as_MySQLdb()

# --- Ahora sí, podés importar Flask-MySQLdb ---
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_segura_cambiala'

# Agregar datetime al contexto de Jinja2
from datetime import datetime as dt

@app.context_processor
def inject_now():
    return {
        'now': dt.now,
        'datetime_now': dt.now()  # Agregar también la fecha/hora actual como objeto
    }

# Configuración MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gimnasio_reservas'

# Configuración de archivos
UPLOAD_FOLDER = 'static/uploads/comprobantes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB máximo

mysql = MySQL(app)

# Crear carpeta de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==================== FILTROS PERSONALIZADOS ====================

@app.template_filter('format_timedelta')
def format_timedelta(td):
    """Convierte timedelta a formato HH:MM"""
    total = int(td.total_seconds())
    h = total // 3600
    m = (total % 3600) // 60
    return f"{h:02d}:{m:02d}"

@app.template_filter('format_time')
def format_time(value):
    """Convierte diferentes formatos de tiempo a HH:MM"""
    # Si ya es un datetime.time
    if isinstance(value, time):
        return value.strftime("%H:%M")

    # Si es un timedelta (por si MySQL lo devuelve así)
    if isinstance(value, timedelta):
        total = int(value.total_seconds())
        h = total // 3600
        m = (total % 3600) // 60
        return f"{h:02d}:{m:02d}"

    # Si viene como string "HH:MM:SS"
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%H:%M:%S").strftime("%H:%M")
        except ValueError:
            pass

        # Si viene como "HH:MM"
        try:
            return datetime.strptime(value, "%H:%M").strftime("%H:%M")
        except ValueError:
            pass

    # Si no matchea nada, lo devolvemos tal cual
    return str(value)

# ==================== FUNCIONES AUXILIARES ====================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_week_dates():
    """Obtiene las fechas de la semana actual"""
    today = datetime.now()
    start = today - timedelta(days=today.weekday())
    return [start + timedelta(days=i) for i in range(7)]

# ==================== RUTAS CLIENTE ====================

@app.route('/')
def index():
    """Página principal - Selección de disciplinas"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM disciplinas WHERE activa = TRUE")
    disciplinas = cur.fetchall()
    cur.close()
    return render_template('index.html', disciplinas=disciplinas)

@app.route('/reservar/<int:disciplina_id>')
def reservar(disciplina_id):
    """Vista de calendario y reserva para una disciplina"""
    cur = mysql.connection.cursor()
    
    # Obtener disciplina
    cur.execute("SELECT * FROM disciplinas WHERE id = %s", [disciplina_id])
    disciplina = cur.fetchone()
    
    if not disciplina:
        flash('Disciplina no encontrada', 'danger')
        return redirect(url_for('index'))
    
    # Obtener horarios de la disciplina
    cur.execute("""
        SELECT id, dia_semana, hora_inicio, cupo_maximo 
        FROM horarios 
        WHERE disciplina_id = %s
        ORDER BY FIELD(dia_semana, 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'), hora_inicio
    """, [disciplina_id])
    horarios_raw = cur.fetchall()
    cur.close()
    
    # Crear estructura de datos optimizada para el template
    horarios_map = {}
    horas_unicas = set()
    
    for h in horarios_raw:
        horario_id = h[0]
        dia_semana = h[1]
        hora_inicio = h[2]
        
        # Convertir timedelta a string HH:MM
        if isinstance(hora_inicio, timedelta):
            total_seconds = int(hora_inicio.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            hora_str = f"{hours:02d}:{minutes:02d}"
        else:
            hora_str = hora_inicio.strftime('%H:%M') if hasattr(hora_inicio, 'strftime') else str(hora_inicio)
        
        # Agregar al mapa
        if dia_semana not in horarios_map:
            horarios_map[dia_semana] = {}
        horarios_map[dia_semana][hora_str] = horario_id
        horas_unicas.add(hora_str)
    
    week_dates = get_week_dates()
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    horas_ordenadas = sorted(list(horas_unicas))
    
    # AGREGAR: Fecha y hora actual para comparar en el template
    now = datetime.now()
    
    return render_template('reservar.html', 
                         disciplina=disciplina, 
                         horarios_map=horarios_map,
                         horas_ordenadas=horas_ordenadas,
                         week_dates=week_dates,
                         dias_semana=dias_semana,
                         current_datetime=now)

@app.route('/check_disponibilidad/<int:horario_id>/<fecha>')
def check_disponibilidad(horario_id, fecha):
    """API para verificar disponibilidad de un horario"""
    cur = mysql.connection.cursor()
    
    # Obtener cupo máximo
    cur.execute("SELECT cupo_maximo FROM horarios WHERE id = %s", [horario_id])
    horario = cur.fetchone()
    
    if not horario:
        return jsonify({'error': 'Horario no encontrado'}), 404
    
    cupo_maximo = horario[0]
    
    # Contar reservas
    cur.execute("""
        SELECT COUNT(*) FROM reservas 
        WHERE horario_id = %s AND fecha_clase = %s AND estado != 'cancelada'
    """, [horario_id, fecha])
    
    reservas_count = cur.fetchone()[0]
    cur.close()
    
    disponible = reservas_count < cupo_maximo
    cupos_restantes = cupo_maximo - reservas_count
    
    return jsonify({
        'disponible': disponible,
        'cupos_restantes': cupos_restantes,
        'cupo_maximo': cupo_maximo
    })

@app.route('/confirmar_reserva', methods=['POST'])
def confirmar_reserva():
    """Procesar y confirmar una reserva"""
    try:
        horario_id = request.form.get('horario_id')
        fecha_clase = request.form.get('fecha_clase')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        dni = request.form.get('dni')
        comprobante = request.files.get('comprobante')
        
        # Validaciones básicas
        if not all([horario_id, fecha_clase, nombre, apellido, dni]):
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(request.referrer)
        
        cur = mysql.connection.cursor()
        
        # AGREGAR: Obtener hora del horario
        cur.execute("SELECT hora_inicio FROM horarios WHERE id = %s", [horario_id])
        horario_data = cur.fetchone()
        
        if not horario_data:
            flash('Horario no encontrado', 'danger')
            cur.close()
            return redirect(request.referrer)
        
        hora_inicio = horario_data[0]
        
        # Convertir hora_inicio a hora comparable
        if isinstance(hora_inicio, timedelta):
            total_seconds = int(hora_inicio.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
        else:
            hours = hora_inicio.hour
            minutes = hora_inicio.minute
        
        # Crear datetime de la clase
        fecha_clase_dt = datetime.strptime(fecha_clase, '%Y-%m-%d')
        fecha_hora_clase = fecha_clase_dt.replace(hour=hours, minute=minutes, second=0)
        
        # VALIDAR: No permitir reservas en horarios pasados
        if fecha_hora_clase < datetime.now():
            flash('No se puede reservar en horarios que ya pasaron', 'warning')
            cur.close()
            return redirect(request.referrer)
        
        # Verificar si ya existe reserva con ese DNI
        cur.execute("""
            SELECT id FROM reservas 
            WHERE horario_id = %s AND fecha_clase = %s AND dni = %s
        """, [horario_id, fecha_clase, dni])
        
        if cur.fetchone():
            flash('Ya existe una reserva con este DNI para esta clase', 'warning')
            cur.close()
            return redirect(request.referrer)
        
        # Verificar disponibilidad
        cur.execute("SELECT cupo_maximo FROM horarios WHERE id = %s", [horario_id])
        cupo_maximo = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) FROM reservas 
            WHERE horario_id = %s AND fecha_clase = %s AND estado != 'cancelada'
        """, [horario_id, fecha_clase])
        
        reservas_count = cur.fetchone()[0]
        
        if reservas_count >= cupo_maximo:
            flash('Este horario ya no tiene cupos disponibles', 'danger')
            cur.close()
            return redirect(request.referrer)
        
        # Procesar comprobante
        comprobante_filename = None
        if comprobante and allowed_file(comprobante.filename):
            filename = secure_filename(f"{dni}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{comprobante.filename}")
            comprobante.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            comprobante_filename = filename
        
        # Insertar reserva
        cur.execute("""
            INSERT INTO reservas (horario_id, fecha_clase, nombre, apellido, dni, comprobante_pago, estado)
            VALUES (%s, %s, %s, %s, %s, %s, 'confirmada')
        """, [horario_id, fecha_clase, nombre, apellido, dni, comprobante_filename])
        
        mysql.connection.commit()
        reserva_id = cur.lastrowid
        cur.close()
        
        flash(f'¡Reserva confirmada! Número de reserva: {reserva_id}', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Error al procesar la reserva: {str(e)}', 'danger')
        return redirect(request.referrer)

# ==================== RUTAS ADMIN ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Login del administrador"""
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, password_hash FROM administradores WHERE usuario = %s", [usuario])
        admin = cur.fetchone()
        cur.close()
        
        if admin and check_password_hash(admin[1], password):
            session['admin_id'] = admin[0]
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Cerrar sesión del administrador"""
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Panel principal del administrador"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cur = mysql.connection.cursor()
    
    # Estadísticas
    cur.execute("SELECT COUNT(*) FROM reservas WHERE estado = 'confirmada'")
    total_reservas = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM disciplinas WHERE activa = TRUE")
    total_disciplinas = cur.fetchone()[0]
    
    cur.close()
    
    return render_template('admin/dashboard.html', 
                         total_reservas=total_reservas,
                         total_disciplinas=total_disciplinas)

@app.route('/admin/reservas')
def admin_reservas():
    """Listado de todas las reservas"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.id, r.nombre, r.apellido, r.dni, r.fecha_clase, 
               h.hora_inicio, d.nombre as disciplina, r.estado, r.comprobante_pago
        FROM reservas r
        JOIN horarios h ON r.horario_id = h.id
        JOIN disciplinas d ON h.disciplina_id = d.id
        ORDER BY r.fecha_clase DESC, h.hora_inicio DESC
    """)
    reservas = cur.fetchall()
    cur.close()
    
    return render_template('admin/reservas.html', reservas=reservas)

@app.route('/admin/reservas/eliminar/<int:reserva_id>')
def admin_eliminar_reserva(reserva_id):
    """Eliminar una reserva"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reservas WHERE id = %s", [reserva_id])
    mysql.connection.commit()
    cur.close()
    
    flash('Reserva eliminada correctamente', 'success')
    return redirect(url_for('admin_reservas'))

@app.route('/admin/disciplinas')
def admin_disciplinas():
    """Gestión de disciplinas"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM disciplinas ORDER BY id DESC")
    disciplinas = cur.fetchall()
    cur.close()
    
    return render_template('admin/disciplinas.html', disciplinas=disciplinas)

@app.route('/admin/disciplinas/agregar', methods=['POST'])
def admin_agregar_disciplina():
    """Agregar nueva disciplina"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO disciplinas (nombre, descripcion) VALUES (%s, %s)", 
                [nombre, descripcion])
    mysql.connection.commit()
    cur.close()
    
    flash('Disciplina agregada correctamente', 'success')
    return redirect(url_for('admin_disciplinas'))

@app.route('/admin/disciplinas/toggle/<int:disciplina_id>')
def admin_toggle_disciplina(disciplina_id):
    """Activar/desactivar disciplina"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE disciplinas SET activa = NOT activa WHERE id = %s", [disciplina_id])
    mysql.connection.commit()
    cur.close()
    
    flash('Estado de disciplina actualizado', 'success')
    return redirect(url_for('admin_disciplinas'))

@app.route('/admin/disciplinas/eliminar/<int:disciplina_id>')
def admin_eliminar_disciplina(disciplina_id):
    """Eliminar disciplina"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM disciplinas WHERE id = %s", [disciplina_id])
    mysql.connection.commit()
    cur.close()
    
    flash('Disciplina eliminada correctamente', 'success')
    return redirect(url_for('admin_disciplinas'))

@app.route('/admin/horarios/<int:disciplina_id>')
def admin_horarios(disciplina_id):
    """Gestión de horarios de una disciplina"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM disciplinas WHERE id = %s", [disciplina_id])
    disciplina = cur.fetchone()
    
    cur.execute("""
        SELECT id, dia_semana, hora_inicio, cupo_maximo 
        FROM horarios 
        WHERE disciplina_id = %s
        ORDER BY FIELD(dia_semana, 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'), hora_inicio
    """, [disciplina_id])
    horarios = cur.fetchall()
    
    # Debug: ver qué datos estamos obteniendo
    print("\nDEBUG - Horarios obtenidos:")
    for h in horarios:
        print(f"  ID: {h[0]}, Día: {h[1]}, Hora: {h[2]} (tipo: {type(h[2])}), Cupo: {h[3]}")
    
    cur.close()
    
    return render_template('admin/horarios.html', disciplina=disciplina, horarios=horarios)

@app.route('/admin/horarios/agregar/<int:disciplina_id>', methods=['POST'])
def admin_agregar_horario(disciplina_id):
    """Agregar nuevo horario"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    dia_semana = request.form.get('dia_semana')
    hora_inicio = request.form.get('hora_inicio')
    cupo_maximo = request.form.get('cupo_maximo', 10)
    
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO horarios (disciplina_id, dia_semana, hora_inicio, cupo_maximo)
        VALUES (%s, %s, %s, %s)
    """, [disciplina_id, dia_semana, hora_inicio, cupo_maximo])
    mysql.connection.commit()
    cur.close()
    
    flash('Horario agregado correctamente', 'success')
    return redirect(url_for('admin_horarios', disciplina_id=disciplina_id))

@app.route('/admin/horarios/eliminar/<int:horario_id>/<int:disciplina_id>')
def admin_eliminar_horario(horario_id, disciplina_id):
    """Eliminar horario"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM horarios WHERE id = %s", [horario_id])
    mysql.connection.commit()
    cur.close()
    
    flash('Horario eliminado correctamente', 'success')
    return redirect(url_for('admin_horarios', disciplina_id=disciplina_id))

# ==================== INICIO DE LA APLICACIÓN ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)