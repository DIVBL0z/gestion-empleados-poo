# modelos.py — LAS CLASES DEL PROBLEMA
# Este archivo no importa sqlite3 ni tiene ningun print:
# no sabe nada de la base de datos ni de la pantalla.

class Departamento:

    def __init__(self, id_departamento, nombre, gerente):
        self.id = id_departamento
        self.nombre = nombre
        self.gerente = gerente



class Empleado:

    def __init__(self, id_empleado, nombre, email, salario, id_departamento):
        self.id = id_empleado
        self.nombre = nombre
        self.email = email
        self._salario = salario
        self.id_departamento = id_departamento

    def get_salario(self):
        return self._salario


class Proyecto:

    def __init__(self, id_proyecto, nombre, descripcion, fecha_inicio):
        self.id = id_proyecto
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio

        
class Usuario:

    def __init__(self, id_usuario, credencial_hash, rol, id_empleado):
        self.id = id_usuario
        self._credencial_hash = credencial_hash   # privado
        self.rol = rol                            # protegido (#)
        self.id_empleado = id_empleado

    def tipo(self):
        # Se guarda en la base de datos para saber que clase reconstruir.
        return "Usuario"

    def autenticar(self, credencial_ingresada):
        return self._credencial_hash == credencial_ingresada

    def verificarPermiso(self, accion):
        return False

    def get_credencial_hash(self):
        return self._credencial_hash

# Administrador ES UN Usuario: hereda todo y solo cambia lo distinto.

class Administrador(Usuario):

    def tipo(self):
        return "Administrador"

    def verificarPermiso(self, accion):
        # El administrador tiene acceso a todo.
        return True

    def generarInformeGlobal(self):
        return "Informe global generado por " +str(self.id)


class EmpleadoUsuario(Usuario):

    def tipo(self):
        return "EmpleadoUsuario"

    def verificarPermiso(self, accion):
        # Un empleado normal solo puede ver/editar sus propios datos.
        acciones_permitidas = ["ver_propio_registro", "registrar_horas"]
        return accion in acciones_permitidas

class RegistroDeTiempo:

    def __init__(self, id_registro, id_empleado, id_proyecto, fecha, horas, descripcion_tarea):
        self.id = id_registro
        self.id_empleado = id_empleado
        self.id_proyecto = id_proyecto
        self.fecha = fecha
        self._horas_trabajadas = horas          # encapsulado
        self.descripcion_tarea = descripcion_tarea

    def horas_trabajadas(self):
        return self._horas_trabajadas

    def getResumen(self):
        # El método que ya propusiste en tu matriz de trazabilidad.
        return (str(self.fecha) + " | " + str(self._horas_trabajadas) +
                " hrs | " + self.descripcion_tarea)