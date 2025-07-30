# Sistema de Concesionaria de Autos

Este proyecto es un sistema de gestión para una concesionaria de autos, compuesto por un backend en Flask (Python) y una interfaz gráfica de usuario (GUI) en Tkinter. Utiliza una base de datos PostgreSQL para almacenar la información.

## Estructura del Proyecto

```
concesionaria_pgadmin.sql      # Script SQL para crear la base de datos y tablas
conn_string.txt                # Cadena de conexión a la base de datos PostgreSQL
client/
    Client.py                  # Interfaz gráfica (Tkinter)
server/
    server.py                  # API REST (Flask)
```

## Requisitos

- Python 3.8+
- PostgreSQL
- Paquetes Python:
  - flask
  - psycopg2
  - requests
  - tkcalendar
  - tkinter (incluido en la mayoría de instalaciones de Python)

## Instalación

1. **Clona el repositorio y entra a la carpeta del proyecto.**

2. **Instala las dependencias:**
   ```sh
   pip install flask psycopg2 requests tkcalendar
   ```

3. **Crea la base de datos y las tablas:**
   - Abre PostgreSQL y ejecuta el script [`concesionaria_pgadmin.sql`](concesionaria_pgadmin.sql).

4. **Configura la cadena de conexión:**
   - Edita [`conn_string.txt`](conn_string.txt) con tu cadena de conexión PostgreSQL si es necesario.

## Ejecución

### 1. Inicia el servidor backend

```sh
cd server
python server.py
```

El backend se ejecutará en `http://127.0.0.1:5000`.

### 2. Inicia el cliente gráfico

En otra terminal:

```sh
cd client
python Client.py
```

## Funcionalidades

- Registrar compras y ventas de autos
- Actualizar datos de vehículos
- Filtrar autos por diferentes criterios
- Consultar historial de compras/ventas por cliente o empleado
- Realizar pedidos de repuestos o vehículos a la central

## Notas

- Asegúrate de que el backend esté corriendo antes de abrir la interfaz gráfica.
- Puedes modificar la cadena de conexión en [`conn_string.txt`](conn_string.txt) para apuntar a tu propia base de datos.

---

¡Listo para usar tu sistema
