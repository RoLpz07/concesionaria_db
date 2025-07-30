import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import requests

# Paleta pastel
COLOR_FONDO = "#66A3BD"
COLOR_BOTON = "#07386F"
COLOR_TEXTO = "#FFFFFF"
COLOR_ACCION = "#08182D"
FUENTE_TITULO = ("Segoe UI", 20, "bold")
FUENTE_BOTON = ("Segoe UI", 14)

BACKEND_URL = "http://127.0.0.1:5000"

class ConcesionariaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Concesionaria")
        self.geometry("1000x600")
        self.configure(bg=COLOR_FONDO)

        self.frames = {}
        self.crear_frames()
        self.mostrar_carga()

    def crear_frames(self):
        for F in (PantallaInicio, PantallaCompra, PantallaVenta, PantallaActualizar, PantallaFiltrar, PantallaHistorial, PantallaPedidos):
            frame = F(self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

    def mostrar_frame(self, nombre_frame):
        for frame in self.frames.values():
            frame.place_forget()
        frame = self.frames[nombre_frame]
        frame.place(relwidth=1, relheight=1)
        frame.tkraise()

    def mostrar_carga(self):
        for frame in self.frames.values():
            frame.place_forget()

        self.carga = ttk.Progressbar(self, orient="horizontal", mode="indeterminate", length=300)
        self.carga.place(relx=0.5, rely=0.5, anchor="center")
        self.carga.start(10)

        self.after(2000, self.fin_carga)

    def fin_carga(self):
        self.carga.destroy()
        self.mostrar_frame("PantallaInicio")

class PantallaInicio(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_FONDO)
        tk.Label(self, text="¡Bienvenido al Sistema de Concesionaria!", font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=40)

        opciones = [
            ("Registrar Compra de Auto", "PantallaCompra"),
            ("Registrar Venta de Auto", "PantallaVenta"),
            ("Actualizar Datos de Auto", "PantallaActualizar"),
            ("Filtrar Autos", "PantallaFiltrar"),
            ("Consultar Historial", "PantallaHistorial"),
            ("Realizar Pedido a la Central", "PantallaPedidos"),
        ]

        for texto, destino in opciones:
            btn = tk.Button(self, text=texto, font=FUENTE_BOTON, bg=COLOR_BOTON, fg=COLOR_TEXTO,
                            activebackground=COLOR_ACCION, activeforeground="white", bd=0, relief="flat",
                            highlightthickness=0, command=lambda d=destino: master.mostrar_frame(d))
            btn.pack(pady=10, ipadx=30, ipady=10)

class PantallaCompra(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_FONDO)
        tk.Label(self, text="Registrar Compra de Auto", font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=10)

        campos = [
            ("ID Vehículo", "id_vehiculo"),
            ("ID Empleado", "id_empleado"),
            ("ID Sucursal", "id_sucursal"),
            ("ID Cliente (opcional)", "id_cliente"),
            ("ID Proveedor (opcional)", "id_proveedor"),
            ("Precio Compra", "precio_compra")
        ]

        self.entradas = {}
        for texto, campo in campos:
            tk.Label(self, text=texto + ":", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack()
            entry = tk.Entry(self, relief="solid", bd=1)
            entry.pack(pady=2)
            self.entradas[campo] = entry

        self.estado_label = tk.Label(self, text="", bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.estado_label.pack()

        tk.Button(self, text="Registrar Compra", command=self.comprar, bg=COLOR_BOTON, fg=COLOR_TEXTO, bd=0).pack(pady=10)
        tk.Button(self, text="Volver", command=lambda: master.mostrar_frame("PantallaInicio"), bg=COLOR_ACCION, fg="white", bd=0).pack()

    def comprar(self):
        datos = {k: v.get().strip() for k, v in self.entradas.items()}
        campos_obligatorios = ["id_vehiculo", "id_empleado", "id_sucursal", "precio_compra"]
        for campo in campos_obligatorios:
            if not datos[campo]:
                messagebox.showwarning("Faltan datos", f"El campo '{campo}' es obligatorio.")
                return
        try:
            datos['precio_compra'] = float(datos['precio_compra'])
        except ValueError:
            messagebox.showerror("Formato inválido", "El precio debe ser numérico.")
            return
        # Campos opcionales: si están vacíos, poner None
        for opcional in ["id_cliente", "id_proveedor"]:
            if not datos[opcional]:
                datos[opcional] = None
        self.estado_label.config(text="Registrando, por favor espera...")
        self.update_idletasks()
        try:
            resp = requests.post(f"{BACKEND_URL}/carros/comprar", json=datos)
            if resp.status_code == 200 and resp.json().get("status") == "ok":
                self.estado_label.config(text="")
                messagebox.showinfo("Compra Registrada", f"Compra registrada con éxito. ID: {resp.json().get('id_compra')}")
                for entry in self.entradas.values():
                    entry.delete(0, tk.END)
            else:
                self.estado_label.config(text="")
                messagebox.showerror("Error", f"Error al registrar compra: {resp.text}")
        except Exception as e:
            self.estado_label.config(text="")
            messagebox.showerror("Error de conexión", str(e))

class PantallaVenta(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_FONDO)
        tk.Label(self, text="Registrar Venta de Auto", font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=10)

        campos = [
            ("ID Cliente", "id_cliente"),
            ("ID Empleado (vendedor)", "id_empleado"),
            ("ID Sucursal", "id_sucursal"),
            ("Total Venta", "total_venta"),
            ("ID Vehículo", "id_vehiculo"),
            ("ID Método de Pago", "id_metodo_pago")
        ]

        self.entradas = {}
        for texto, campo in campos:
            tk.Label(self, text=texto + ":", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack()
            entry = tk.Entry(self, relief="solid", bd=1)
            entry.pack(pady=2)
            self.entradas[campo] = entry

        self.estado_label = tk.Label(self, text="", bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.estado_label.pack()

        tk.Button(self, text="Confirmar Venta", command=self.vender, bg=COLOR_BOTON, fg=COLOR_TEXTO, bd=0).pack(pady=10)
        tk.Button(self, text="Volver", command=lambda: master.mostrar_frame("PantallaInicio"), bg=COLOR_ACCION, fg="white", bd=0).pack()

    def vender(self):
        datos = {k: v.get().strip() for k, v in self.entradas.items()}
        campos_obligatorios = ["id_cliente", "id_empleado", "id_sucursal", "total_venta", "id_vehiculo", "id_metodo_pago"]
        for campo in campos_obligatorios:
            if not datos[campo]:
                messagebox.showwarning("Faltan datos", f"El campo '{campo}' es obligatorio.")
                return
        try:
            datos['total_venta'] = float(datos['total_venta'])
        except ValueError:
            messagebox.showerror("Formato inválido", "El total de venta debe ser numérico.")
            return
        self.estado_label.config(text="Procesando venta...")
        self.update_idletasks()
        try:
            resp = requests.post(f"{BACKEND_URL}/carros/vender", json=datos)
            if resp.status_code == 200 and resp.json().get("status") == "ok":
                self.estado_label.config(text="")
                messagebox.showinfo("Venta Registrada", f"Venta registrada con éxito. ID: {resp.json().get('id_venta')}")
                for entry in self.entradas.values():
                    entry.delete(0, tk.END)
            else:
                self.estado_label.config(text="")
                messagebox.showerror("Error", f"Error al registrar venta: {resp.text}")
        except Exception as e:
            self.estado_label.config(text="")
            messagebox.showerror("Error de conexión", str(e))

class PantallaActualizar(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_FONDO)
        tk.Label(self, text="Actualizar Datos de Auto", font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=20)

        campos = [
            ("ID Vehículo", "id_vehiculo"),
            ("Tipo Vehículo", "tipo_vehiculo"),
            ("Color", "color"),
            ("Kilometraje", "kilometraje"),
            ("Capacidad", "capacidad"),
            ("Año", "anio"),
            ("Precio", "precio"),
            ("Estado", "estado"),
            ("ID Sucursal", "id_sucursal"),
            ("ID Marca", "id_marca")
        ]
        self.entradas = {}
        for texto, campo in campos:
            tk.Label(self, text=texto + ":", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack()
            entry = tk.Entry(self, relief="solid", bd=1)
            entry.pack(pady=2)
            self.entradas[campo] = entry

        self.estado_label = tk.Label(self, text="", bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.estado_label.pack()

        tk.Button(self, text="Actualizar", command=self.actualizar, bg=COLOR_BOTON, fg=COLOR_TEXTO, bd=0).pack(pady=10)
        tk.Button(self, text="Volver", command=lambda: master.mostrar_frame("PantallaInicio"), bg=COLOR_ACCION, fg="white", bd=0).pack()

    def actualizar(self):
        datos = {k: v.get().strip() for k, v in self.entradas.items()}
        if not datos["id_vehiculo"]:
            messagebox.showerror("Falta ID", "Debes ingresar el ID del vehículo a actualizar.")
            return
        try:
            datos['kilometraje'] = int(datos['kilometraje'])
            datos['capacidad'] = int(datos['capacidad'])
            datos['anio'] = int(datos['anio'])
            datos['precio'] = float(datos['precio'])
        except Exception:
            messagebox.showerror("Formato inválido", "Kilometraje, capacidad, año y precio deben ser numéricos.")
            return
        self.estado_label.config(text="Actualizando datos...")
        self.update_idletasks()
        try:
            resp = requests.put(f"{BACKEND_URL}/carros/actualizar", json=datos)
            if resp.status_code == 200 and resp.json().get("status") == "ok":
                self.estado_label.config(text="")
                messagebox.showinfo("Actualizado", f"Vehículo ID {datos['id_vehiculo']} actualizado con éxito.")
            else:
                self.estado_label.config(text="")
                messagebox.showerror("Error", f"Error al actualizar: {resp.text}")
        except Exception as e:
            self.estado_label.config(text="")
            messagebox.showerror("Error de conexión", str(e))

class PantallaFiltrar(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_FONDO)
        tk.Label(self, text="Filtrar Autos", font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=20)

        filtros = [
            ("Tipo Vehículo", "tipo_vehiculo"),
            ("Color", "color"),
            ("Año", "anio"),
            ("Estado", "estado")
        ]
        self.entradas = {}
        for texto, campo in filtros:
            tk.Label(self, text=texto + ":", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack()
            entry = tk.Entry(self, relief="solid", bd=1)
            entry.pack(pady=2)
            self.entradas[campo] = entry

        tk.Button(self, text="Buscar", command=self.filtrar, bg=COLOR_BOTON, fg=COLOR_TEXTO, bd=0).pack(pady=10)
        tk.Button(self, text="Volver", command=lambda: master.mostrar_frame("PantallaInicio"), bg=COLOR_ACCION, fg="white", bd=0).pack()

        frame_tabla = tk.Frame(self, bg=COLOR_FONDO)
        frame_tabla.pack(fill="both", expand=True, pady=10)

        self.columnas = [
            "id_vehiculo", "tipo_vehiculo", "color", "kilometraje", "capacidad",
            "anio", "precio", "estado", "id_sucursal", "id_marca"
        ]
        self.resultados = ttk.Treeview(frame_tabla, columns=self.columnas, show="headings", height=12)
        for col in self.columnas:
            heading = "Año" if col == "anio" else col.replace("_", " ").capitalize()
            self.resultados.heading(col, text=heading)
            self.resultados.column(col, width=100, anchor="center")
        vsb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.resultados.yview)
        hsb = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.resultados.xview)
        self.resultados.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.resultados.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

    def filtrar(self):
        params = {k: v.get().strip() for k, v in self.entradas.items() if v.get().strip()}
        try:
            resp = requests.get(f"{BACKEND_URL}/carros/filtrar", params=params)
            if resp.status_code == 200:
                for row in self.resultados.get_children():
                    self.resultados.delete(row)
                for auto in resp.json():
                    fila = [auto.get(col, "") for col in self.columnas]
                    self.resultados.insert("", "end", values=fila)
            else:
                messagebox.showerror("Error", f"Error al filtrar: {resp.text}")
        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))

class PantallaHistorial(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_FONDO)
        tk.Label(self, text="Consultar Historial", font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=20)

        tk.Label(self, text="ID Cliente:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack()
        self.entry_cliente = tk.Entry(self, relief="solid", bd=1)
        self.entry_cliente.pack(pady=5)

        tk.Label(self, text="ID Empleado:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack()
        self.entry_empleado = tk.Entry(self, relief="solid", bd=1)
        self.entry_empleado.pack(pady=5)

        tk.Button(self, text="Consultar", command=self.consultar, bg=COLOR_BOTON, fg=COLOR_TEXTO, bd=0).pack(pady=10)
        tk.Button(self, text="Volver", command=lambda: master.mostrar_frame("PantallaInicio"), bg=COLOR_ACCION, fg="white", bd=0).pack()

        # Tabla con scrollbar para mostrar historial organizado
        frame_tabla = tk.Frame(self, bg=COLOR_FONDO)
        frame_tabla.pack(fill="both", expand=True, pady=10)

        columnas = ("tipo", "id", "fecha", "monto", "id_vehiculo", "id_persona", "id_sucursal")
        self.resultados = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)
        encabezados = ["Tipo", "ID", "Fecha", "Monto", "ID Vehículo", "ID Persona", "ID Sucursal"]
        for col, txt in zip(columnas, encabezados):
            self.resultados.heading(col, text=txt)
            self.resultados.column(col, width=110, anchor="center")
        # Scrollbars
        vsb = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.resultados.yview)
        hsb = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.resultados.xview)
        self.resultados.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.resultados.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

    def consultar(self):
        id_cliente = self.entry_cliente.get().strip()
        id_empleado = self.entry_empleado.get().strip()
        params = {}
        if id_cliente:
            params["id_cliente"] = id_cliente
        if id_empleado:
            params["id_empleado"] = id_empleado
        if not params:
            messagebox.showwarning("Faltan datos", "Ingrese al menos un ID para consultar.")
            return
        try:
            resp = requests.get(f"{BACKEND_URL}/historial", params=params)
            if resp.status_code == 200:
                for row in self.resultados.get_children():
                    self.resultados.delete(row)
                for item in resp.json():
                    if item["tipo"] == "venta":
                        self.resultados.insert("", "end", values=(
                            "venta", item.get("id_venta"), item.get("fecha_venta"), item.get("total_venta"),
                            item.get("id_vehiculo"), item.get("id_empleado", item.get("id_cliente")), item.get("id_sucursal")
                        ))
                    else:
                        self.resultados.insert("", "end", values=(
                            "compra", item.get("id_compra"), item.get("fecha_compra"), item.get("precio_compra"),
                            item.get("id_vehiculo"), item.get("id_empleado", item.get("id_cliente")), item.get("id_sucursal")
                        ))
            else:
                messagebox.showerror("Error", f"Error al consultar: {resp.text}")
        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))

class PantallaPedidos(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_FONDO)
        tk.Label(self, text="Realizar Pedido a la Central", font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=20)

        campos = [
            ("ID Sucursal Solicitante", "id_sucursal_solicitante"),
            ("ID Empleado Solicitante", "id_empleado_solicitante"),
            ("Estado del Pedido", "estado")
        ]
        self.entradas = {}
        for texto, campo in campos:
            tk.Label(self, text=texto + ":", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack()
            entry = tk.Entry(self, relief="solid", bd=1)
            entry.pack(pady=2)
            self.entradas[campo] = entry

        # Instrucción clara para el usuario sobre el formato de detalles
        instrucciones = (
            "Detalles del Pedido (uno por línea, formato: id_repuesto,id_vehiculo,cantidad)\n"
            "Puedes dejar id_repuesto o id_vehiculo vacío si no aplica, pero la coma debe estar.\n"
            "Ejemplos válidos:\n"
            "1,,5\n"
            ",2,10\n"
            "3,4,2\n"
            'Esto significa:\n' \
            '- Primer detalle: id_repuesto=1, id_vehiculo=None, cantidad=5\n' \
            '- Segundo detalle: id_repuesto=None, id_vehiculo=2, cantidad=10\n' \
            '- Tercer detalle: id_repuesto=3, id_vehiculo=4, cantidad=2\n'
            "No pongas espacios entre los números y las comas."
        )
        tk.Label(self, text=instrucciones, bg=COLOR_FONDO, fg=COLOR_TEXTO, justify="left", anchor="w").pack(pady=(10, 0), padx=10, fill="x")
        self.detalles_text = tk.Text(self, height=5, width=60)
        self.detalles_text.pack(pady=5)

        self.estado_label = tk.Label(self, text="", bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.estado_label.pack()

        tk.Button(self, text="Realizar Pedido", command=self.realizar_pedido, bg=COLOR_BOTON, fg=COLOR_TEXTO, bd=0).pack(pady=10)
        tk.Button(self, text="Volver", command=lambda: master.mostrar_frame("PantallaInicio"), bg=COLOR_ACCION, fg="white", bd=0).pack()

    def realizar_pedido(self):
        datos = {k: v.get().strip() for k, v in self.entradas.items()}
        detalles = []
        for linea in self.detalles_text.get("1.0", tk.END).strip().splitlines():
            partes = [x.strip() for x in linea.split(",")]
            if len(partes) == 3:
                detalles.append({
                    "id_repuesto": partes[0] if partes[0] else None,
                    "id_vehiculo": partes[1] if partes[1] else None,
                    "cantidad": int(partes[2])
                })
        datos["detalles"] = detalles
        self.estado_label.config(text="Enviando pedido...")
        self.update_idletasks()
        try:
            resp = requests.post(f"{BACKEND_URL}/pedidos", json=datos)
            if resp.status_code == 200 and resp.json().get("status") == "ok":
                self.estado_label.config(text="")
                messagebox.showinfo("Pedido realizado", f"Pedido registrado con éxito. ID: {resp.json().get('id_pedido')}")
                for entry in self.entradas.values():
                    entry.delete(0, tk.END)
                self.detalles_text.delete("1.0", tk.END)
            else:
                self.estado_label.config(text="")
                messagebox.showerror("Error", f"Error al registrar pedido: {resp.text}")
        except Exception as e:
            self.estado_label.config(text="")
            messagebox.showerror("Error de conexión", str(e))

# En la pantalla de pedidos, los detalles deben ingresarse así:
# Cada línea representa un detalle.
# El formato de cada línea es:
# id_repuesto,id_vehiculo,cantidad
# Puedes dejar id_repuesto o id_vehiculo vacío si no aplica, pero la coma debe estar.
#
# Ejemplos válidos:
#
# 1, ,5
# ,2,10
# 3,4,2
#
# Esto significa:
# - Primer detalle: id_repuesto=1, id_vehiculo=None, cantidad=5
# - Segundo detalle: id_repuesto=None, id_vehiculo=2, cantidad=10
# - Tercer detalle: id_repuesto=3, id_vehiculo=4, cantidad=2
#
# No pongas espacios entre los números y las comas para evitar errores.

if __name__ == "__main__":
    app = ConcesionariaApp()
    app.mainloop()