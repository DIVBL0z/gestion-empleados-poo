# datos.py — LA CAPA DE DATOS
# Aqui vive todo el SQL. Ningun print, ningun input.

import sqlite3
from modelos import (Empleado, Usuario, Administrador, EmpleadoUsuario,
                      RegistroDeTiempo, Departamento, Proyecto)


class BaseDeDatos:
    # Solo abre y cierra la conexion, y deja las tablas creadas.

    def __init__(self):
        self.conexion = sqlite3.connect("ecotech.db")
        self.cursor = self.conexion.cursor()
        self.ultimo_error = ""  # Aqui se guarda el ultimo error ocurrido.

        # Departamento no depende de nadie: por eso se crea primero.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS departamentos (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                gerente TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                salario REAL NOT NULL,
                id_departamento INTEGER NOT NULL,
                FOREIGN KEY (id_departamento) REFERENCES departamentos(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS proyectos (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                fecha_inicio TEXT NOT NULL
            )
        """)

        # Un empleado puede tener un usuario para entrar al sistema.
        # La columna tipo guarda "Administrador" o "EmpleadoUsuario": de ese
        # dato depende que clase se construye al leer.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                credencial_hash TEXT NOT NULL,
                rol TEXT NOT NULL,
                tipo TEXT NOT NULL,
                id_empleado INTEGER NOT NULL,
                FOREIGN KEY (id_empleado) REFERENCES empleados(id)
            )
        """)

        # Un registro de tiempo pertenece a UN empleado y a UN proyecto:
        # por eso tiene DOS claves foraneas. Un empleado puede tener muchos
        # registros, y un proyecto tambien.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros_tiempo (
                id INTEGER PRIMARY KEY,
                id_empleado INTEGER NOT NULL,
                id_proyecto INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                horas INTEGER NOT NULL,
                descripcion_tarea TEXT NOT NULL,
                FOREIGN KEY (id_empleado) REFERENCES empleados(id),
                FOREIGN KEY (id_proyecto) REFERENCES proyectos(id)
            )
        """)

        # Tabla intermedia para la relacion muchos-a-muchos Empleado-Proyecto.
        # No existe como clase en modelos.py: solo existe aqui, como tabla,
        # porque una relacion N a N no se guarda dentro de ningun objeto,
        # se guarda como una fila que conecta a los dos.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleado_proyecto (
                id_empleado INTEGER NOT NULL,
                id_proyecto INTEGER NOT NULL,
                PRIMARY KEY (id_empleado, id_proyecto),
                FOREIGN KEY (id_empleado) REFERENCES empleados(id),
                FOREIGN KEY (id_proyecto) REFERENCES proyectos(id)
            )
        """)

        self.conexion.commit()

    def cerrar(self):
        self.conexion.close()


class GestorEmpleados:
    # No abre la conexion: la recibe hecha. Esto es COMPOSICION.
    # GestorEmpleados TIENE una base de datos, no ES una base de datos.

    def __init__(self, base):
        self.base = base  # ATRIBUTO: la base de datos que va a usar.

    def crear(self, empleado):
        try:
            self.base.cursor.execute(
                "INSERT INTO empleados (nombre, email, salario, id_departamento) "
                "VALUES (?, ?, ?, ?)",
                (empleado.nombre, empleado.email, empleado.get_salario(),
                 empleado.id_departamento))
            self.base.conexion.commit()  # Sin commit el dato no queda guardado.
            return True
        except sqlite3.Error as error:
            # La clase no imprime: guarda el error y avisa devolviendo False.
            self.base.ultimo_error = str(error)
            return False

    def leer(self):
        try:
            self.base.cursor.execute(
                "SELECT id, nombre, email, salario, id_departamento "
                "FROM empleados ORDER BY id")
            filas = self.base.cursor.fetchall()
            lista = []
            for fila in filas:
                lista.append(Empleado(fila[0], fila[1], fila[2], fila[3], fila[4]))
            return lista
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None  # None significa que fallo la consulta.

    def buscar(self, id_empleado):
        try:
            self.base.cursor.execute(
                "SELECT id, nombre, email, salario, id_departamento "
                "FROM empleados WHERE id = ?", (id_empleado,))
            fila = self.base.cursor.fetchone()  # Entrega UNA fila, o None.
            if fila == None:
                return None
            return Empleado(fila[0], fila[1], fila[2], fila[3], fila[4])
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None

    def eliminar(self, id_empleado):
        try:
            # El WHERE limita el borrado a un solo empleado.
            self.base.cursor.execute("DELETE FROM empleados WHERE id = ?", (id_empleado,))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def actualizar(self, empleado):
        try:
            # SET indica que columnas cambian, WHERE indica en cual empleado.
            self.base.cursor.execute(
                "UPDATE empleados SET nombre = ?, email = ?, salario = ?, "
                "id_departamento = ? WHERE id = ?",
                (empleado.nombre, empleado.email, empleado.get_salario(),
                 empleado.id_departamento, empleado.id))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False


class GestorUsuarios:

    def __init__(self, base):
        self.base = base

    def armar_usuario(self, fila):
        # Traduce una fila de la tabla al objeto que corresponde.
        # fila[0] id, fila[1] credencial_hash, fila[2] rol,
        # fila[3] tipo, fila[4] id_empleado.
        if fila[3] == "Administrador":
            return Administrador(fila[0], fila[1], fila[2], fila[4])
        else:
            return EmpleadoUsuario(fila[0], fila[1], fila[2], fila[4])

    def crear(self, usuario):
        # Recibe un OBJETO, no cuatro datos sueltos.
        try:
            self.base.cursor.execute(
                "INSERT INTO usuarios (credencial_hash, rol, tipo, id_empleado) "
                "VALUES (?, ?, ?, ?)",
                (usuario.get_credencial_hash(), usuario.rol,
                 usuario.tipo(), usuario.id_empleado))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def leer_con_empleado(self):
        # JOIN une las dos tablas: al lado de cada usuario deja el nombre
        # del empleado cuyo id coincide con su id_empleado.
        # Devuelve pares: [objeto usuario, nombre del empleado].
        try:
            self.base.cursor.execute("""
                SELECT usuarios.id, usuarios.credencial_hash, usuarios.rol,
                       usuarios.tipo, usuarios.id_empleado,
                       empleados.nombre
                FROM usuarios
                JOIN empleados ON usuarios.id_empleado = empleados.id
                ORDER BY usuarios.id
            """)
            filas = self.base.cursor.fetchall()
            lista = []
            for fila in filas:
                lista.append([self.armar_usuario(fila), fila[5]])
            return lista
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None

    def buscar(self, id_usuario):
        try:
            self.base.cursor.execute(
                "SELECT id, credencial_hash, rol, tipo, id_empleado "
                "FROM usuarios WHERE id = ?", (id_usuario,))
            fila = self.base.cursor.fetchone()
            if fila == None:
                return None
            return self.armar_usuario(fila)
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None

    def actualizar(self, usuario):
        try:
            # SET indica que columnas cambian, WHERE indica en cual registro.
            # Sin el WHERE se cambiarian TODOS los usuarios de la tabla.
            self.base.cursor.execute(
                "UPDATE usuarios SET credencial_hash = ?, rol = ? WHERE id = ?",
                (usuario.get_credencial_hash(), usuario.rol, usuario.id))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def eliminar(self, id_usuario):
        try:
            self.base.cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def contar_por_empleado(self, id_empleado):
        # Sirve para saber si un empleado se puede eliminar.
        try:
            self.base.cursor.execute("SELECT COUNT(*) FROM usuarios WHERE id_empleado = ?",
                                     (id_empleado,))
            fila = self.base.cursor.fetchone()
            return fila[0]  # COUNT(*) devuelve una fila con un solo numero.
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None


class GestorRegistros:

    def __init__(self, base):
        self.base = base

    def crear(self, registro):
        # El registro trae las DOS claves foraneas: empleado y proyecto.
        try:
            self.base.cursor.execute(
                "INSERT INTO registros_tiempo "
                "(id_empleado, id_proyecto, fecha, horas, descripcion_tarea) "
                "VALUES (?, ?, ?, ?, ?)",
                (registro.id_empleado, registro.id_proyecto, registro.fecha,
                 registro.horas_trabajadas(), registro.descripcion_tarea))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def leer_completo(self):
        # JOIN une el registro con el empleado que lo hizo.
        # Devuelve pares: [objeto registro, objeto empleado].
        try:
            self.base.cursor.execute("""
                SELECT registros_tiempo.id, registros_tiempo.id_empleado,
                       registros_tiempo.id_proyecto, registros_tiempo.fecha,
                       registros_tiempo.horas, registros_tiempo.descripcion_tarea,
                       empleados.id, empleados.nombre, empleados.email,
                       empleados.salario, empleados.id_departamento
                FROM registros_tiempo
                JOIN empleados ON registros_tiempo.id_empleado = empleados.id
                ORDER BY registros_tiempo.id
            """)
            filas = self.base.cursor.fetchall()
            lista = []
            for fila in filas:
                registro = RegistroDeTiempo(fila[0], fila[1], fila[2], fila[3], fila[4], fila[5])
                empleado = Empleado(fila[6], fila[7], fila[8], fila[9], fila[10])
                lista.append([registro, empleado])
            return lista
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None

    def buscar(self, id_registro):
        try:
            self.base.cursor.execute(
                "SELECT id, id_empleado, id_proyecto, fecha, horas, descripcion_tarea "
                "FROM registros_tiempo WHERE id = ?", (id_registro,))
            fila = self.base.cursor.fetchone()
            if fila == None:
                return None
            return RegistroDeTiempo(fila[0], fila[1], fila[2], fila[3], fila[4], fila[5])
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None

    def actualizar(self, registro):
        try:
            self.base.cursor.execute(
                "UPDATE registros_tiempo SET horas = ?, descripcion_tarea = ? WHERE id = ?",
                (registro.horas_trabajadas(), registro.descripcion_tarea, registro.id))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def contar_por_empleado(self, id_empleado):
        try:
            self.base.cursor.execute(
                "SELECT COUNT(*) FROM registros_tiempo WHERE id_empleado = ?",
                (id_empleado,))
            fila = self.base.cursor.fetchone()
            return fila[0]
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None

    def contar_por_proyecto(self, id_proyecto):
        try:
            self.base.cursor.execute(
                "SELECT COUNT(*) FROM registros_tiempo WHERE id_proyecto = ?",
                (id_proyecto,))
            fila = self.base.cursor.fetchone()
            return fila[0]
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None


class GestorDepartamentos:

    def __init__(self, base):
        self.base = base

    def crear(self, departamento):
        try:
            self.base.cursor.execute(
                "INSERT INTO departamentos (nombre, gerente) VALUES (?, ?)",
                (departamento.nombre, departamento.gerente))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def leer(self):
        try:
            self.base.cursor.execute(
                "SELECT id, nombre, gerente FROM departamentos ORDER BY id")
            filas = self.base.cursor.fetchall()
            lista = []
            for fila in filas:
                lista.append(Departamento(fila[0], fila[1], fila[2]))
            return lista
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None

    def buscar(self, id_departamento):
        try:
            self.base.cursor.execute(
                "SELECT id, nombre, gerente FROM departamentos WHERE id = ?",
                (id_departamento,))
            fila = self.base.cursor.fetchone()
            if fila == None:
                return None
            return Departamento(fila[0], fila[1], fila[2])
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None

    def eliminar(self, id_departamento):
        try:
            self.base.cursor.execute(
                "DELETE FROM departamentos WHERE id = ?", (id_departamento,))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def actualizar(self, departamento):
        try:
            self.base.cursor.execute(
                "UPDATE departamentos SET nombre = ?, gerente = ? WHERE id = ?",
                (departamento.nombre, departamento.gerente, departamento.id))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def contar_empleados(self, id_departamento):
        # Sirve para saber si un departamento se puede eliminar,
        # igual que contar_por_cliente en el ejemplo del taller.
        try:
            self.base.cursor.execute(
                "SELECT COUNT(*) FROM empleados WHERE id_departamento = ?",
                (id_departamento,))
            fila = self.base.cursor.fetchone()
            return fila[0]
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None


class GestorProyectos:

    def __init__(self, base):
        self.base = base

    def crear(self, proyecto):
        try:
            self.base.cursor.execute(
                "INSERT INTO proyectos (nombre, descripcion, fecha_inicio) "
                "VALUES (?, ?, ?)",
                (proyecto.nombre, proyecto.descripcion, proyecto.fecha_inicio))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def leer(self):
        try:
            self.base.cursor.execute(
                "SELECT id, nombre, descripcion, fecha_inicio "
                "FROM proyectos ORDER BY id")
            filas = self.base.cursor.fetchall()
            lista = []
            for fila in filas:
                lista.append(Proyecto(fila[0], fila[1], fila[2], fila[3]))
            return lista
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None

    def buscar(self, id_proyecto):
        try:
            self.base.cursor.execute(
                "SELECT id, nombre, descripcion, fecha_inicio "
                "FROM proyectos WHERE id = ?", (id_proyecto,))
            fila = self.base.cursor.fetchone()
            if fila == None:
                return None
            return Proyecto(fila[0], fila[1], fila[2], fila[3])
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None

    def eliminar(self, id_proyecto):
        try:
            self.base.cursor.execute(
                "DELETE FROM proyectos WHERE id = ?", (id_proyecto,))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def actualizar(self, proyecto):
        try:
            self.base.cursor.execute(
                "UPDATE proyectos SET nombre = ?, descripcion = ?, fecha_inicio = ? "
                "WHERE id = ?",
                (proyecto.nombre, proyecto.descripcion, proyecto.fecha_inicio,
                 proyecto.id))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    # ---- Relacion muchos-a-muchos con Empleado ----
    # Estos tres metodos no tienen equivalente en el ejemplo del taller,
    # porque ese ejemplo no tenia ninguna relacion N a N.

    def asignar_empleado(self, id_empleado, id_proyecto):
        try:
            self.base.cursor.execute(
                "INSERT INTO empleado_proyecto (id_empleado, id_proyecto) "
                "VALUES (?, ?)", (id_empleado, id_proyecto))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            # Si el empleado ya estaba asignado a ese proyecto, la clave
            # primaria compuesta (id_empleado, id_proyecto) rechaza el
            # duplicado y cae aqui.
            self.base.ultimo_error = str(error)
            return False

    def desasignar_empleado(self, id_empleado, id_proyecto):
        try:
            self.base.cursor.execute(
                "DELETE FROM empleado_proyecto "
                "WHERE id_empleado = ? AND id_proyecto = ?",
                (id_empleado, id_proyecto))
            self.base.conexion.commit()
            return True
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return False

    def listar_empleados_de_proyecto(self, id_proyecto):
        try:
            self.base.cursor.execute("""
                SELECT empleados.id, empleados.nombre, empleados.email,
                       empleados.salario, empleados.id_departamento
                FROM empleado_proyecto
                JOIN empleados ON empleado_proyecto.id_empleado = empleados.id
                WHERE empleado_proyecto.id_proyecto = ?
                ORDER BY empleados.id
            """, (id_proyecto,))
            filas = self.base.cursor.fetchall()
            lista = []
            for fila in filas:
                lista.append(Empleado(fila[0], fila[1], fila[2], fila[3], fila[4]))
            return lista
        except sqlite3.Error as error:
            self.base.ultimo_error = str(error)
            return None
