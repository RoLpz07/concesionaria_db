CREATE TABLE Sucursales (
  id_sucursal SERIAL NOT NULL PRIMARY KEY,
  nombre VARCHAR,
  direccion VARCHAR,
  ciudad VARCHAR,
  calle VARCHAR,
  avenida VARCHAR,
  fecha_apertura TIMESTAMP,
  es_central BOOLEAN DEFAULT FALSE
);

CREATE TABLE Marcas (
  id_marca SERIAL NOT NULL PRIMARY KEY,
  nombre_marca VARCHAR,
  año INT,
  pais_marca VARCHAR
);

CREATE TABLE Vehiculos (
  id_vehiculo SERIAL NOT NULL PRIMARY KEY,
  tipo_vehiculo VARCHAR,
  color VARCHAR,
  kilometraje INT,
  capacidad VARCHAR,
  año INT,
  precio FLOAT,
  estado VARCHAR,
  id_sucursal INT NOT NULL REFERENCES Sucursales(id_sucursal),
  id_marca INT NOT NULL REFERENCES Marcas(id_marca)
);

CREATE TABLE Repuestos (
  id_repuesto SERIAL NOT NULL PRIMARY KEY,
  nombre_repuesto VARCHAR,
  marca_repuesto VARCHAR,
  cantidad_stock INT,
  id_sucursal INT NOT NULL REFERENCES Sucursales(id_sucursal)
);

CREATE TABLE Proveedores (
  id_proveedor SERIAL NOT NULL PRIMARY KEY,
  nombre VARCHAR,
  pais VARCHAR,
  telefono BIGINT,
  correo VARCHAR
);

CREATE TABLE Clientes (
  id_cliente SERIAL NOT NULL PRIMARY KEY,
  nombre VARCHAR,
  apellido VARCHAR,
  cedula BIGINT,
  direccion VARCHAR,
  pais VARCHAR,
  correo VARCHAR,
  telefono BIGINT
);

CREATE TABLE Metodos_Pago (
  id_metodo_pago SERIAL NOT NULL PRIMARY KEY,
  tipo_pago VARCHAR,
  plazo VARCHAR,
  tasa_interes FLOAT
);

CREATE TABLE Empleados (
  id_empleado SERIAL NOT NULL PRIMARY KEY,
  nombre VARCHAR,
  apellido VARCHAR,
  fecha_ingreso TIMESTAMP,
  correo VARCHAR,
  telefono VARCHAR,
  cargo VARCHAR,
  id_sucursal INT NOT NULL REFERENCES Sucursales(id_sucursal)
);

CREATE TABLE Ventas (
  id_venta SERIAL NOT NULL PRIMARY KEY,
  id_cliente INT NOT NULL REFERENCES Clientes(id_cliente),
  id_empleado INT NOT NULL REFERENCES Empleados(id_empleado),
  id_sucursal INT NOT NULL REFERENCES Sucursales(id_sucursal),
  fecha_venta TIMESTAMP,
  total_venta FLOAT,
  id_vehiculo INT NOT NULL UNIQUE REFERENCES Vehiculos(id_vehiculo),
  id_metodo_pago INT NOT NULL REFERENCES Metodos_Pago(id_metodo_pago)
);

CREATE TABLE Compras (
  id_compra SERIAL NOT NULL PRIMARY KEY,
  id_vehiculo INT NOT NULL UNIQUE REFERENCES Vehiculos(id_vehiculo),
  id_empleado INT NOT NULL REFERENCES Empleados(id_empleado),
  id_sucursal INT NOT NULL REFERENCES Sucursales(id_sucursal),
  id_cliente INT REFERENCES Clientes(id_cliente),
  id_proveedor INT REFERENCES Proveedores(id_proveedor),
  fecha_compra TIMESTAMP,
  precio_compra FLOAT
);

CREATE TABLE Transferencias (
  id_transferencia SERIAL NOT NULL PRIMARY KEY,
  id_vehiculo INT NOT NULL REFERENCES Vehiculos(id_vehiculo),
  id_sucursal_origen INT NOT NULL REFERENCES Sucursales(id_sucursal),
  id_sucursal_destino INT NOT NULL REFERENCES Sucursales(id_sucursal),
  id_empleado_solicita INT NOT NULL REFERENCES Empleados(id_empleado),
  fecha_solicitud TIMESTAMP,
  fecha_recepcion TIMESTAMP,
  estado VARCHAR
);

CREATE TABLE Pedidos_Central (
  id_pedido SERIAL NOT NULL PRIMARY KEY,
  id_sucursal_solicitante INT NOT NULL REFERENCES Sucursales(id_sucursal),
  id_empleado_solicitante INT NOT NULL REFERENCES Empleados(id_empleado),
  fecha_pedido TIMESTAMP,
  estado VARCHAR
);

CREATE TABLE Pedido_Detalles (
  id_detalle_pedido SERIAL NOT NULL PRIMARY KEY,
  id_pedido INT NOT NULL REFERENCES Pedidos_Central(id_pedido),
  id_repuesto INT REFERENCES Repuestos(id_repuesto),
  id_vehiculo INT REFERENCES Vehiculos(id_vehiculo),
  cantidad INT NOT NULL
);