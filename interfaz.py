# interfaz.py — LA INTERFAZ
# Aqui vive todo lo que se imprime y todo lo que se pregunta.
# Ni una linea de SQL.

from modelos import Departamento, Empleado, Proyecto, Administrador, EmpleadoUsuario, RegistroDeTiempo


# ---------- Validaciones ----------

def pedir_texto(mensaje):
    # Devuelve el texto escrito, o None si quedo vacio.
    texto = input(mensaje).strip()
    if texto == "":
        print("Este dato no puede quedar vacio.")
        return None
    return texto


def pedir_email(mensaje):
    # Validacion simple: exige un "@" y un "." despues del "@".
    correo = pedir_texto(mensaje)
    if correo == None:
        return None
    if "@" not in correo or "." not in correo.split("@")[-1]:
        print("El correo no tiene un formato valido (ej: nombre@dominio.cl).")
        return None
    return correo


def pedir_numero(mensaje, minimo, maximo):
    entrada = input(mensaje).strip()
    try:
        numero = int(entrada)
    except ValueError:
        print("Debe escribir un numero.")
        return None

    if numero < minimo or numero > maximo:
        print("El valor debe estar entre", minimo, "y", maximo, ".")
        return None
    return numero


def pedir_decimal(mensaje, minimo):
    entrada = input(mensaje).strip()
    try:
        numero = float(entrada)
    except ValueError:
        print("Debe escribir un numero (ej: 1500000 o 1500000.50).")
        return None

    if numero < minimo:
        print("El valor no puede ser menor a", minimo, ".")
        return None
    return numero


# ---------- Departamentos ----------

def opcion_crear_departamento(g):
    print("\n-- REGISTRAR DEPARTAMENTO --")

    nombre = pedir_texto("Nombre: ")
    if nombre == None:
        return

    gerente = pedir_texto("Gerente a cargo: ")
    if gerente == None:
        return

    departamento = Departamento(0, nombre, gerente)  # El id lo asigna la BD.
    if g["departamentos"].crear(departamento):
        print("Departamento registrado.")
    else:
        print("No se pudo registrar el departamento.")
        print("--- Detalle tecnico ---\n", g["departamentos"].base.ultimo_error)


def opcion_listar_departamentos(g):
    print("\n-- DEPARTAMENTOS --")
    lista = g["departamentos"].leer()

    if lista == None:
        print("No se pudo leer la base de datos.")
        return
    if lista == []:
        print("No hay departamentos registrados.")
        return

    for departamento in lista:
        print("ID:", departamento.id, "|", departamento.nombre,
              "| Gerente:", departamento.gerente)


def opcion_eliminar_departamento(g):
    print("\n-- ELIMINAR DEPARTAMENTO --")
    opcion_listar_departamentos(g)

    id_departamento = pedir_numero("ID del departamento a eliminar: ", 1, 99999)
    if id_departamento == None:
        return

    departamento = g["departamentos"].buscar(id_departamento)
    if departamento == None:
        print("No existe un departamento con ese ID.")
        return

    # Si el departamento tiene empleados, borrarlo los dejaria sin departamento.
    cantidad = g["departamentos"].contar_empleados(id_departamento)
    if cantidad == None:
        print("No se pudo revisar la base de datos.")
        return
    if cantidad > 0:
        print("No se puede eliminar:", departamento.nombre, "tiene", cantidad,
              "empleado(s) asignado(s).")
        return

    confirmacion = input("Eliminar " + departamento.nombre + "? s/n: ")
    if confirmacion.lower() != "s":
        print("Eliminacion cancelada.")
        return

    if g["departamentos"].eliminar(id_departamento):
        print("Departamento eliminado.")
    else:
        print("No se pudo eliminar el departamento.")


# ---------- Empleados ----------

def opcion_crear_empleado(g):
    print("\n-- REGISTRAR EMPLEADO --")

    lista = g["departamentos"].leer()
    if lista == None or lista == []:
        print("Primero debe registrar un departamento.")
        return
    opcion_listar_departamentos(g)

    id_departamento = pedir_numero("ID del departamento: ", 1, 99999)
    if id_departamento == None:
        return
    if g["departamentos"].buscar(id_departamento) == None:
        print("No existe un departamento con ese ID.")
        return

    nombre = pedir_texto("Nombre: ")
    if nombre == None:
        return

    email = pedir_email("Email: ")
    if email == None:
        return

    salario = pedir_decimal("Salario: ", 0)
    if salario == None:
        return

    empleado = Empleado(0, nombre, email, salario, id_departamento)
    if g["empleados"].crear(empleado):
        print("Empleado registrado.")
    else:
        print("No se pudo registrar el empleado.")
        print("--- Detalle tecnico ---\n", g["empleados"].base.ultimo_error)


def opcion_listar_empleados(g):
    print("\n-- EMPLEADOS --")
    lista = g["empleados"].leer()

    if lista == None:
        print("No se pudo leer la base de datos.")
        return
    if lista == []:
        print("No hay empleados registrados.")
        return

    for empleado in lista:
        print("ID:", empleado.id, "|", empleado.nombre, "|", empleado.email,
              "| $", empleado.get_salario(), "| Depto:", empleado.id_departamento)


def opcion_eliminar_empleado(g):
    print("\n-- ELIMINAR EMPLEADO --")
    opcion_listar_empleados(g)

    id_empleado = pedir_numero("ID del empleado a eliminar: ", 1, 99999)
    if id_empleado == None:
        return

    empleado = g["empleados"].buscar(id_empleado)
    if empleado == None:
        print("No existe un empleado con ese ID.")
        return

    # Si el empleado tiene un usuario asociado, borrarlo lo dejaria huerfano.
    cantidad = g["usuarios"].contar_por_empleado(id_empleado)
    if cantidad == None:
        print("No se pudo revisar la base de datos.")
        return
    if cantidad > 0:
        print("No se puede eliminar:", empleado.nombre, "tiene un usuario asociado.")
        return

    confirmacion = input("Eliminar a " + empleado.nombre + "? s/n: ")
    if confirmacion.lower() != "s":
        print("Eliminacion cancelada.")
        return

    if g["empleados"].eliminar(id_empleado):
        print("Empleado eliminado.")
    else:
        print("No se pudo eliminar el empleado.")


# ---------- Usuarios (Administrador / EmpleadoUsuario) ----------

def opcion_crear_usuario(g):
    print("\n-- REGISTRAR USUARIO --")

    lista = g["empleados"].leer()
    if lista == None or lista == []:
        print("Primero debe registrar un empleado.")
        return
    opcion_listar_empleados(g)

    id_empleado = pedir_numero("ID del empleado: ", 1, 99999)
    if id_empleado == None:
        return
    if g["empleados"].buscar(id_empleado) == None:
        print("No existe un empleado con ese ID.")
        return

    credencial = pedir_texto("Contrasena: ")
    if credencial == None:
        return

    print("1 - Administrador")
    print("2 - EmpleadoUsuario")
    tipo = input("Tipo (1-2): ").strip()

    if tipo == "1":
        usuario = Administrador(0, credencial, "Administrador", id_empleado)
    elif tipo == "2":
        usuario = EmpleadoUsuario(0, credencial, "Empleado", id_empleado)
    else:
        print("Tipo no valido. No se registro el usuario.")
        return

    if g["usuarios"].crear(usuario):
        print("Usuario registrado como", usuario.tipo() + ".")
    else:
        print("No se pudo registrar el usuario.")
        print("--- Detalle tecnico ---\n", g["usuarios"].base.ultimo_error)


def opcion_listar_usuarios(g):
    print("\n-- USUARIOS --")
    lista = g["usuarios"].leer_con_empleado()

    if lista == None:
        print("No se pudo leer la base de datos.")
        return
    if lista == []:
        print("No hay usuarios registrados.")
        return

    for par in lista:
        usuario = par[0]   # El objeto Administrador o EmpleadoUsuario.
        empleado = par[1]  # El nombre del empleado.
        # Se llama igual al metodo sin preguntar de que tipo es el objeto:
        # cada subclase responde lo suyo. Eso es polimorfismo.
        print("ID:", usuario.id, "|", usuario.tipo(), "| Empleado:", empleado,
              "| Rol:", usuario.rol)


def opcion_eliminar_usuario(g):
    print("\n-- ELIMINAR USUARIO --")
    opcion_listar_usuarios(g)

    id_usuario = pedir_numero("ID del usuario a eliminar: ", 1, 99999)
    if id_usuario == None:
        return

    usuario = g["usuarios"].buscar(id_usuario)
    if usuario == None:
        print("No existe un usuario con ese ID.")
        return

    confirmacion = input("Eliminar este usuario? s/n: ")
    if confirmacion.lower() != "s":
        print("Eliminacion cancelada.")
        return

    if g["usuarios"].eliminar(id_usuario):
        print("Usuario eliminado.")
    else:
        print("No se pudo eliminar el usuario.")


# ---------- Proyectos ----------

def opcion_crear_proyecto(g):
    print("\n-- REGISTRAR PROYECTO --")

    nombre = pedir_texto("Nombre: ")
    if nombre == None:
        return

    descripcion = pedir_texto("Descripcion: ")
    if descripcion == None:
        return

    fecha_inicio = pedir_texto("Fecha de inicio (AAAA-MM-DD): ")
    if fecha_inicio == None:
        return

    proyecto = Proyecto(0, nombre, descripcion, fecha_inicio)
    if g["proyectos"].crear(proyecto):
        print("Proyecto registrado.")
    else:
        print("No se pudo registrar el proyecto.")
        print("--- Detalle tecnico ---\n", g["proyectos"].base.ultimo_error)


def opcion_listar_proyectos(g):
    print("\n-- PROYECTOS --")
    lista = g["proyectos"].leer()

    if lista == None:
        print("No se pudo leer la base de datos.")
        return
    if lista == []:
        print("No hay proyectos registrados.")
        return

    for proyecto in lista:
        print("ID:", proyecto.id, "|", proyecto.nombre, "|", proyecto.descripcion,
              "| Inicio:", proyecto.fecha_inicio)


def opcion_asignar_empleado_proyecto(g):
    print("\n-- ASIGNAR EMPLEADO A PROYECTO --")

    opcion_listar_empleados(g)
    id_empleado = pedir_numero("ID del empleado: ", 1, 99999)
    if id_empleado == None:
        return
    if g["empleados"].buscar(id_empleado) == None:
        print("No existe un empleado con ese ID.")
        return

    opcion_listar_proyectos(g)
    id_proyecto = pedir_numero("ID del proyecto: ", 1, 99999)
    if id_proyecto == None:
        return
    if g["proyectos"].buscar(id_proyecto) == None:
        print("No existe un proyecto con ese ID.")
        return

    if g["proyectos"].asignar_empleado(id_empleado, id_proyecto):
        print("Empleado asignado al proyecto.")
    else:
        print("No se pudo asignar (puede que ya estuviera asignado).")
        print("--- Detalle tecnico ---\n", g["proyectos"].base.ultimo_error)


def opcion_listar_empleados_de_proyecto(g):
    print("\n-- EMPLEADOS DE UN PROYECTO --")
    opcion_listar_proyectos(g)

    id_proyecto = pedir_numero("ID del proyecto: ", 1, 99999)
    if id_proyecto == None:
        return

    lista = g["proyectos"].listar_empleados_de_proyecto(id_proyecto)
    if lista == None:
        print("No se pudo leer la base de datos.")
        return
    if lista == []:
        print("Ese proyecto no tiene empleados asignados.")
        return

    for empleado in lista:
        print("ID:", empleado.id, "|", empleado.nombre, "|", empleado.email)


# ---------- Registros de tiempo ----------

def opcion_crear_registro(g):
    print("\n-- REGISTRAR HORAS TRABAJADAS --")

    opcion_listar_empleados(g)
    id_empleado = pedir_numero("ID del empleado: ", 1, 99999)
    if id_empleado == None:
        return
    if g["empleados"].buscar(id_empleado) == None:
        print("No existe un empleado con ese ID.")
        return

    opcion_listar_proyectos(g)
    id_proyecto = pedir_numero("ID del proyecto: ", 1, 99999)
    if id_proyecto == None:
        return
    if g["proyectos"].buscar(id_proyecto) == None:
        print("No existe un proyecto con ese ID.")
        return

    fecha = pedir_texto("Fecha (AAAA-MM-DD): ")
    if fecha == None:
        return

    horas = pedir_numero("Horas trabajadas: ", 1, 24)
    if horas == None:
        return

    descripcion_tarea = pedir_texto("Descripcion de la tarea: ")
    if descripcion_tarea == None:
        return

    registro = RegistroDeTiempo(0, id_empleado, id_proyecto, fecha, horas, descripcion_tarea)
    if g["registros"].crear(registro):
        print("Registro de tiempo guardado.")
    else:
        print("No se pudo guardar el registro.")
        print("--- Detalle tecnico ---\n", g["registros"].base.ultimo_error)


def opcion_listar_registros(g):
    print("\n-- REGISTROS DE TIEMPO --")
    lista = g["registros"].leer_completo()

    if lista == None:
        print("No se pudo leer la base de datos.")
        return
    if lista == []:
        print("No hay registros de tiempo.")
        return

    for par in lista:
        registro = par[0]   # El objeto RegistroDeTiempo.
        empleado = par[1]   # El objeto Empleado.
        print("ID:", registro.id, "|", empleado.nombre, "|", registro.getResumen())


# ---------- Modificar (UPDATE) ----------
# Todas siguen el mismo patron: listar, pedir el ID, buscar el registro actual,
# pedir los datos nuevos (mostrando el valor actual), armar un objeto con el
# MISMO id y entregarselo al gestor. El gestor hace el UPDATE ... WHERE id.

def opcion_actualizar_departamento(g):
    print("\n-- MODIFICAR DEPARTAMENTO --")
    opcion_listar_departamentos(g)

    id_departamento = pedir_numero("ID del departamento a modificar: ", 1, 99999)
    if id_departamento == None:
        return

    actual = g["departamentos"].buscar(id_departamento)
    if actual == None:
        print("No existe un departamento con ese ID.")
        return

    nombre = pedir_texto("Nombre nuevo (actual: " + actual.nombre + "): ")
    if nombre == None:
        return

    gerente = pedir_texto("Gerente nuevo (actual: " + actual.gerente + "): ")
    if gerente == None:
        return

    departamento = Departamento(id_departamento, nombre, gerente)
    if g["departamentos"].actualizar(departamento):
        print("Departamento actualizado.")
    else:
        print("No se pudo actualizar el departamento.")
        print("--- Detalle tecnico ---\n", g["departamentos"].base.ultimo_error)


def opcion_actualizar_empleado(g):
    print("\n-- MODIFICAR EMPLEADO --")
    opcion_listar_empleados(g)

    id_empleado = pedir_numero("ID del empleado a modificar: ", 1, 99999)
    if id_empleado == None:
        return

    actual = g["empleados"].buscar(id_empleado)
    if actual == None:
        print("No existe un empleado con ese ID.")
        return

    nombre = pedir_texto("Nombre nuevo (actual: " + actual.nombre + "): ")
    if nombre == None:
        return

    email = pedir_email("Email nuevo (actual: " + actual.email + "): ")
    if email == None:
        return

    salario = pedir_decimal("Salario nuevo (actual: " + str(actual.get_salario()) + "): ", 0)
    if salario == None:
        return

    opcion_listar_departamentos(g)
    id_departamento = pedir_numero("ID del departamento nuevo (actual: " +
                                   str(actual.id_departamento) + "): ", 1, 99999)
    if id_departamento == None:
        return
    if g["departamentos"].buscar(id_departamento) == None:
        print("No existe un departamento con ese ID.")
        return

    empleado = Empleado(id_empleado, nombre, email, salario, id_departamento)
    if g["empleados"].actualizar(empleado):
        print("Empleado actualizado.")
    else:
        print("No se pudo actualizar el empleado.")
        print("--- Detalle tecnico ---\n", g["empleados"].base.ultimo_error)


def opcion_actualizar_usuario(g):
    # Solo se cambia la contrasena: el rol y el empleado asociado se mantienen.
    print("\n-- CAMBIAR CONTRASENA DE UN USUARIO --")
    opcion_listar_usuarios(g)

    id_usuario = pedir_numero("ID del usuario a modificar: ", 1, 99999)
    if id_usuario == None:
        return

    actual = g["usuarios"].buscar(id_usuario)
    if actual == None:
        print("No existe un usuario con ese ID.")
        return

    credencial = pedir_texto("Contrasena nueva: ")
    if credencial == None:
        return

    # type(actual) es la clase del usuario (Administrador o EmpleadoUsuario):
    # asi el objeto nuevo es del mismo tipo que el original.
    usuario = type(actual)(id_usuario, credencial, actual.rol, actual.id_empleado)
    if g["usuarios"].actualizar(usuario):
        print("Contrasena actualizada.")
    else:
        print("No se pudo actualizar el usuario.")
        print("--- Detalle tecnico ---\n", g["usuarios"].base.ultimo_error)


def opcion_actualizar_proyecto(g):
    print("\n-- MODIFICAR PROYECTO --")
    opcion_listar_proyectos(g)

    id_proyecto = pedir_numero("ID del proyecto a modificar: ", 1, 99999)
    if id_proyecto == None:
        return

    actual = g["proyectos"].buscar(id_proyecto)
    if actual == None:
        print("No existe un proyecto con ese ID.")
        return

    nombre = pedir_texto("Nombre nuevo (actual: " + actual.nombre + "): ")
    if nombre == None:
        return

    descripcion = pedir_texto("Descripcion nueva (actual: " + actual.descripcion + "): ")
    if descripcion == None:
        return

    fecha_inicio = pedir_texto("Fecha de inicio nueva, AAAA-MM-DD (actual: " +
                               actual.fecha_inicio + "): ")
    if fecha_inicio == None:
        return

    proyecto = Proyecto(id_proyecto, nombre, descripcion, fecha_inicio)
    if g["proyectos"].actualizar(proyecto):
        print("Proyecto actualizado.")
    else:
        print("No se pudo actualizar el proyecto.")
        print("--- Detalle tecnico ---\n", g["proyectos"].base.ultimo_error)


def opcion_actualizar_registro(g):
    # Solo se corrigen las horas y la descripcion: el empleado, el proyecto y la
    # fecha del registro se mantienen.
    print("\n-- MODIFICAR REGISTRO DE TIEMPO --")
    opcion_listar_registros(g)

    id_registro = pedir_numero("ID del registro a modificar: ", 1, 99999)
    if id_registro == None:
        return

    actual = g["registros"].buscar(id_registro)
    if actual == None:
        print("No existe un registro con ese ID.")
        return

    horas = pedir_numero("Horas nuevas (actual: " + str(actual.horas_trabajadas()) +
                         ", entre 1 y 24): ", 1, 24)
    if horas == None:
        return

    descripcion_tarea = pedir_texto("Descripcion nueva (actual: " +
                                    actual.descripcion_tarea + "): ")
    if descripcion_tarea == None:
        return

    registro = RegistroDeTiempo(id_registro, actual.id_empleado, actual.id_proyecto,
                                actual.fecha, horas, descripcion_tarea)
    if g["registros"].actualizar(registro):
        print("Registro actualizado.")
    else:
        print("No se pudo actualizar el registro.")
        print("--- Detalle tecnico ---\n", g["registros"].base.ultimo_error)


# ---------- Menu principal ----------

def menu_principal(g):
    while True:
        print("\n===== ECOTECH SOLUTIONS =====")
        print(" 1 - Registrar departamento")
        print(" 2 - Listar departamentos")
        print(" 3 - Eliminar departamento")
        print(" 4 - Registrar empleado")
        print(" 5 - Listar empleados")
        print(" 6 - Eliminar empleado")
        print(" 7 - Registrar usuario (login)")
        print(" 8 - Listar usuarios")
        print(" 9 - Eliminar usuario")
        print("10 - Registrar proyecto")
        print("11 - Listar proyectos")
        print("12 - Asignar empleado a proyecto")
        print("13 - Ver empleados de un proyecto")
        print("14 - Registrar horas trabajadas")
        print("15 - Listar registros de tiempo")
        print("16 - Modificar departamento")
        print("17 - Modificar empleado")
        print("18 - Cambiar contrasena de usuario")
        print("19 - Modificar proyecto")
        print("20 - Modificar registro de tiempo")
        print("21 - SALIR")

        opcion = input("Elija una opcion: ").strip()

        if opcion == "1":
            opcion_crear_departamento(g)
        elif opcion == "2":
            opcion_listar_departamentos(g)
        elif opcion == "3":
            opcion_eliminar_departamento(g)
        elif opcion == "4":
            opcion_crear_empleado(g)
        elif opcion == "5":
            opcion_listar_empleados(g)
        elif opcion == "6":
            opcion_eliminar_empleado(g)
        elif opcion == "7":
            opcion_crear_usuario(g)
        elif opcion == "8":
            opcion_listar_usuarios(g)
        elif opcion == "9":
            opcion_eliminar_usuario(g)
        elif opcion == "10":
            opcion_crear_proyecto(g)
        elif opcion == "11":
            opcion_listar_proyectos(g)
        elif opcion == "12":
            opcion_asignar_empleado_proyecto(g)
        elif opcion == "13":
            opcion_listar_empleados_de_proyecto(g)
        elif opcion == "14":
            opcion_crear_registro(g)
        elif opcion == "15":
            opcion_listar_registros(g)
        elif opcion == "16":
            opcion_actualizar_departamento(g)
        elif opcion == "17":
            opcion_actualizar_empleado(g)
        elif opcion == "18":
            opcion_actualizar_usuario(g)
        elif opcion == "19":
            opcion_actualizar_proyecto(g)
        elif opcion == "20":
            opcion_actualizar_registro(g)
        elif opcion == "21":
            print("Cerrando programa...")
            break
        else:
            print("Opcion no valida.")

        input("Presione Enter para volver al menu...")
