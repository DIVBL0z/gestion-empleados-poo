# EcoTech Solutions - Sistema de Gestión Interna

Sistema de gestión de empleados desarrollado en Python aplicando Programación Orientada a Objetos, como parte de la Evaluación Sumativa 2 (ES02) de la asignatura TI3V21 - Programación Orientada a Objeto Seguro, INACAP.

El proyecto continúa el modelado UML realizado en la Unidad 1, implementándolo en código funcional con conexión a base de datos, manejo de excepciones y validación de datos de usuario.

## Integrantes

- Daniel Díaz
- Denisse Jiménez
- Jose Ignacio Monsalve

## Descripción del proyecto

EcoTech Solutions es una empresa ficticia de tecnologías sostenibles con problemas de duplicidad de datos, mala asignación de empleados a proyectos, falta de trazabilidad de horas trabajadas y riesgos de seguridad en el acceso a la información. Este sistema centraliza esa gestión mediante una aplicación de consola con base de datos propia.

### Funcionalidades principales

- Registro, consulta, modificación y eliminación de departamentos, empleados, usuarios, proyectos y registros de horas trabajadas.
- Asignación de empleados a proyectos (relación muchos a muchos).
- Sistema de usuarios con dos roles: **Administrador** y **Empleado**, cada uno con distintos permisos.
- Validación de datos ingresados por el usuario (correos, números, campos obligatorios).
- Manejo de errores en cada operación con la base de datos, sin interrumpir la ejecución del programa.

## Estructura del proyecto

El programa está organizado en 4 capas, cada una con una única responsabilidad:

```
├── modelos.py     # Las clases del dominio (Departamento, Empleado, Proyecto,
│                  # Usuario, Administrador, EmpleadoUsuario, RegistroDeTiempo)
├── datos.py       # Capa de acceso a datos: conexión SQLite y operaciones CRUD
├── interfaz.py    # Capa de presentación: menús, mensajes y validación de entrada
└── main.py        # Punto de entrada: arma la conexión y los gestores, y arranca el menú
```

- `modelos.py` no depende de ningún otro archivo del proyecto (sin `sqlite3`, sin `print`).
- `datos.py` depende de `modelos.py`, pero no sabe nada de la interfaz.
- `interfaz.py` depende de `modelos.py` y recibe los gestores desde `main.py`; no contiene SQL.
- `main.py` es el único archivo que se ejecuta directamente.

## Modelo de datos

| Clase | Descripción | Relación |
|---|---|---|
| `Departamento` | Unidad organizacional de la empresa | 1 — 0..* con `Empleado` |
| `Empleado` | Persona que trabaja en la empresa | 0..* — 0..* con `Proyecto` |
| `Proyecto` | Iniciativa en la que participan empleados | 1 — 0..* con `RegistroDeTiempo` |
| `RegistroDeTiempo` | Horas trabajadas por un empleado en un proyecto | Depende de `Empleado` y `Proyecto` |
| `Usuario` | Clase base de autenticación | Superclase de `Administrador` y `EmpleadoUsuario` |
| `Administrador` | Usuario con acceso completo al sistema | Hereda de `Usuario` |
| `EmpleadoUsuario` | Usuario con acceso limitado a sus propios datos | Hereda de `Usuario` |

## Requisitos

- Python 3.10 o superior
- No requiere librerías externas: usa `sqlite3`, incluido en la librería estándar de Python

## Instalación y ejecución

```bash
# Clonar el repositorio
git clone https://github.com/[usuario]/gestion-empleados-poo.git
cd gestion-empleados-poo

# Ejecutar el programa
python3 main.py
```

Al ejecutarse por primera vez, el programa crea automáticamente el archivo `ecotech.db` con todas las tablas necesarias.

## Uso

El programa muestra un menú numerado en la consola. Se navega escribiendo el número de la opción deseada y presionando Enter. Algunas recomendaciones:

1. Registra primero al menos un **departamento**, ya que los empleados requieren uno asignado.
2. Registra **empleados** antes de crear sus **usuarios** de acceso.
3. Registra **proyectos** antes de asignar empleados o registrar horas trabajadas en ellos.

## Estado del proyecto

Esta entrega corresponde a la **Unidad 2** de la asignatura (implementación POO y conexión a base de datos). La **Unidad 3** (consumo de APIs externas, autenticación con credenciales cifradas y manejo de errores HTTP) se abordará en una entrega posterior.

## Uso de Inteligencia Artificial

Durante el desarrollo se utilizó IA como apoyo para adaptar el código base entregado por el docente al modelo de este proyecto. Todo el código generado fue revisado, probado y corregido por el equipo antes de integrarlo — el detalle de este proceso se documenta en el informe técnico y se explica en la defensa en video de la evaluación.
