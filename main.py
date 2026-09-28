# main.py — EL PROGRAMA
# Este archivo no hace trabajo: solo crea los objetos y los pone a funcionar.
# Es el unico que se ejecuta.

import sqlite3
from datos import (BaseDeDatos, GestorEmpleados, GestorUsuarios, GestorRegistros,
                    GestorDepartamentos, GestorProyectos)
from interfaz import menu_principal


def main():
    # Si la base de datos no se puede abrir, el programa avisa y termina
    # en vez de mostrar un error de Python que nadie entiende.
    try:
        base = BaseDeDatos()  # Una sola conexion para todo el programa.
    except sqlite3.Error:
        print("No se pudo abrir la base de datos. El programa se cerrara.")
        return

    # Los cinco gestores reciben la MISMA base de datos: eso es composicion.
    gestores = {
        "departamentos": GestorDepartamentos(base),
        "empleados": GestorEmpleados(base),
        "proyectos": GestorProyectos(base),
        "usuarios": GestorUsuarios(base),
        "registros": GestorRegistros(base)
    }

    menu_principal(gestores)  # Se le entregan los gestores a la interfaz.

    base.cerrar()  # La conexion la cierra la base, no los gestores.


# Ejecuta el programa solo si este archivo se abre directamente.
# Gracias a esta linea, importar los otros archivos no dispara el menu.
if __name__ == "__main__":
    main()
