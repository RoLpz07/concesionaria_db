import os
from flask import Flask, jsonify, request
import psycopg2
from urllib.parse import urlparse

app = Flask(__name__)

def load_database_url():
    # 1. Intenta obtener de variable de entorno
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url
    # 2. Intenta leer de archivo local
    try:
        with open('conn_string.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('postgresql://'):
                    return line
    except Exception:
        pass
    # 3. Usa valor por defecto (Neon)
    return 'postgresql://neondb_owner:npg_Vk4JwKGiTeF3@ep-late-block-aexe6fi4-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

DATABASE_URL = load_database_url()

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def home():
    return 'API Concesionaria funcionando'

@app.route('/sucursales')
def get_sucursales():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id_sucursal, nombre, ciudad FROM Sucursales')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    sucursales = []
    for row in rows:
        sucursales.append({
            'id_sucursal': row[0],
            'nombre': row[1],
            'ciudad': row[2]
        })
    return jsonify(sucursales)

@app.route('/carros/vender', methods=['POST'])
def vender_carro():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    # Corrige el nombre de la columna a precio_venta
    cur.execute(
        """
        INSERT INTO Ventas (id_cliente, id_empleado, id_sucursal, fecha_venta, precio_venta, id_vehiculo, id_metodo_pago)
        VALUES (%s, %s, %s, NOW(), %s, %s, %s) RETURNING id_venta
        """,
        (
            data['id_cliente'],
            data['id_empleado'],
            data['id_sucursal'],
            data['total_venta'],  # Si tu frontend envía 'total_venta', puedes cambiarlo a 'precio_venta' en el frontend para mayor claridad
            data['id_vehiculo'],
            data['id_metodo_pago']
        )
    )
    venta_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'ok', 'id_venta': venta_id})

@app.route('/carros/comprar', methods=['POST'])
def comprar_carro():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    # Insertar en Compras
    cur.execute(
        """
        INSERT INTO Compras (id_vehiculo, id_empleado, id_sucursal, id_cliente, id_proveedor, fecha_compra, precio_compra)
        VALUES (%s, %s, %s, %s, %s, NOW(), %s) RETURNING id_compra
        """,
        (
            data['id_vehiculo'],
            data['id_empleado'],
            data['id_sucursal'],
            data.get('id_cliente'),    # Puede ser null si es proveedor
            data.get('id_proveedor'),  # Puede ser null si es cliente
            data['precio_compra']
        )
    )
    compra_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'ok', 'id_compra': compra_id})

@app.route('/carros/actualizar', methods=['PUT'])
def actualizar_carro():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    # Actualiza datos del vehículo
    cur.execute(
        """
        UPDATE Vehiculos
        SET tipo_vehiculo=%s, color=%s, kilometraje=%s, capacidad=%s, anio=%s, precio=%s, estado=%s, id_sucursal=%s, id_marca=%s
        WHERE id_vehiculo=%s
        """,
        (
            data['tipo_vehiculo'],
            data['color'],
            data['kilometraje'],
            data['capacidad'],
            data['anio'],
            data['precio'],
            data['estado'],
            data['id_sucursal'],
            data['id_marca'],
            data['id_vehiculo']
        )
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/carros/transferir', methods=['POST'])
def transferir_carro():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    # Insertar en Transferencias
    cur.execute(
        """
        INSERT INTO Transferencias (id_vehiculo, id_sucursal_origen, id_sucursal_destino, id_empleado_solicita, fecha_solicitud, estado)
        VALUES (%s, %s, %s, %s, NOW(), %s) RETURNING id_transferencia
        """,
        (
            data['id_vehiculo'],
            data['id_sucursal_origen'],
            data['id_sucursal_destino'],
            data['id_empleado_solicita'],
            data['estado']
        )
    )
    transferencia_id = cur.fetchone()[0]
    # Actualizar sucursal del vehículo
    cur.execute(
        "UPDATE Vehiculos SET id_sucursal = %s WHERE id_vehiculo = %s",
        (data['id_sucursal_destino'], data['id_vehiculo'])
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'ok', 'id_transferencia': transferencia_id})

@app.route('/pedidos', methods=['POST'])
def realizar_pedido():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    # Insertar en Pedidos_Central
    cur.execute(
        """
        INSERT INTO Pedidos_Central (id_sucursal_solicitante, id_empleado_solicitante, fecha_pedido, estado)
        VALUES (%s, %s, NOW(), %s) RETURNING id_pedido
        """,
        (
            data['id_sucursal_solicitante'],
            data['id_empleado_solicitante'],
            data['estado']
        )
    )
    pedido_id = cur.fetchone()[0]
    # Insertar detalles del pedido correctamente
    detalles = data.get('detalles', [])
    for detalle in detalles:
        # Asegúrate de que cantidad sea un entero y no None
        cantidad = detalle.get('cantidad')
        try:
            cantidad = int(cantidad)
        except Exception:
            cantidad = None
        # Solo inserta si cantidad es válida
        if cantidad is not None:
            cur.execute(
                """
                INSERT INTO Pedido_Detalles (id_pedido, id_repuesto, id_vehiculo, cantidad)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    pedido_id,
                    detalle.get('id_repuesto') if detalle.get('id_repuesto') not in ["", None] else None,
                    detalle.get('id_vehiculo') if detalle.get('id_vehiculo') not in ["", None] else None,
                    cantidad
                )
            )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'ok', 'id_pedido': pedido_id})

@app.route('/carros/filtrar', methods=['GET'])
def filtrar_carros():
    tipo_vehiculo = request.args.get('tipo_vehiculo')
    color = request.args.get('color')
    anio = request.args.get('anio')
    estado = request.args.get('estado')
    query = "SELECT id_vehiculo, tipo_vehiculo, color, kilometraje, capacidad, anio, precio, estado, id_sucursal, id_marca FROM Vehiculos WHERE 1=1"
    params = []
    if tipo_vehiculo:
        query += " AND tipo_vehiculo = %s"
        params.append(tipo_vehiculo)
    if color:
        query += " AND color = %s"
        params.append(color)
    if anio:
        query += " AND anio = %s"
        params.append(anio)
    if estado:
        query += " AND estado = %s"
        params.append(estado)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    vehiculos = []
    for row in rows:
        vehiculos.append({
            'id_vehiculo': row[0],
            'tipo_vehiculo': row[1],
            'color': row[2],
            'kilometraje': row[3],
            'capacidad': row[4],
            'anio': row[5],
            'precio': row[6],
            'estado': row[7],
            'id_sucursal': row[8],
            'id_marca': row[9]
        })
    return jsonify(vehiculos)

@app.route('/historial', methods=['GET'])
def historial():
    id_cliente = request.args.get('id_cliente')
    id_empleado = request.args.get('id_empleado')
    conn = get_db_connection()
    cur = conn.cursor()
    historial = []
    # Usa precio_venta en los SELECT
    if id_cliente:
        cur.execute(
            """
            SELECT v.id_venta, v.fecha_venta, v.precio_venta, v.id_vehiculo, v.id_empleado, v.id_sucursal
            FROM ventas v
            WHERE v.id_cliente = %s
            ORDER BY v.fecha_venta DESC
            """,
            (id_cliente,)
        )
        for row in cur.fetchall():
            historial.append({
                'tipo': 'venta',
                'id_venta': row[0],
                'fecha_venta': row[1],
                'total_venta': row[2],  # Puedes cambiar la clave a 'precio_venta' si quieres ser más explícito
                'id_vehiculo': row[3],
                'id_empleado': row[4],
                'id_sucursal': row[5]
            })
        cur.execute(
            """
            SELECT c.id_compra, c.fecha_compra, c.precio_compra, c.id_vehiculo, c.id_empleado, c.id_sucursal
            FROM compras c
            WHERE c.id_cliente = %s
            ORDER BY c.fecha_compra DESC
            """,
            (id_cliente,)
        )
        for row in cur.fetchall():
            historial.append({
                'tipo': 'compra',
                'id_compra': row[0],
                'fecha_compra': row[1],
                'precio_compra': row[2],
                'id_vehiculo': row[3],
                'id_empleado': row[4],
                'id_sucursal': row[5]
            })
    elif id_empleado:
        cur.execute(
            """
            SELECT v.id_venta, v.fecha_venta, v.precio_venta, v.id_vehiculo, v.id_cliente, v.id_sucursal
            FROM ventas v
            WHERE v.id_empleado = %s
            ORDER BY v.fecha_venta DESC
            """,
            (id_empleado,)
        )
        for row in cur.fetchall():
            historial.append({
                'tipo': 'venta',
                'id_venta': row[0],
                'fecha_venta': row[1],
                'total_venta': row[2],  # Puedes cambiar la clave a 'precio_venta' si quieres ser más explícito
                'id_vehiculo': row[3],
                'id_cliente': row[4],
                'id_sucursal': row[5]
            })
        cur.execute(
            """
            SELECT c.id_compra, c.fecha_compra, c.precio_compra, c.id_vehiculo, c.id_cliente, c.id_sucursal
            FROM compras c
            WHERE c.id_empleado = %s
            ORDER BY c.fecha_compra DESC
            """,
            (id_empleado,)
        )
        for row in cur.fetchall():
            historial.append({
                'tipo': 'compra',
                'id_compra': row[0],
                'fecha_compra': row[1],
                'precio_compra': row[2],
                'id_vehiculo': row[3],
                'id_cliente': row[4],
                'id_sucursal': row[5]
            })
    cur.close()
    conn.close()
    return jsonify(historial)

if __name__ == '__main__':
    app.run(debug=True)


