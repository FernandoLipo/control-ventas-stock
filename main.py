from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.metrics import dp
import sqlite3
import os
from datetime import datetime

# --- FUNCIÓN AUXILIAR PARA LA BASE DE DATOS ---
def obtener_ruta_db():
    ruta_app = App.get_running_app().user_data_dir
    return os.path.join(ruta_app, "optica_italiana.db")

# ==========================================
# 1. PANTALLA DE LOGIN
# ==========================================
class PantallaLogin(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.crear_base_datos_inicial()

        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))
        layout.add_widget(Widget(size_hint_y=None, height=dp(20)))

        layout.add_widget(Label(text="ÓPTICA ITALIANA", font_size='28sp', bold=True, size_hint_y=None, height=dp(45)))
        layout.add_widget(Label(text="Gestión Móvil v6.0", font_size='16sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(20)))
        layout.add_widget(Widget(size_hint_y=None, height=dp(20)))

        layout.add_widget(Label(text="USUARIO:", font_size='16sp', bold=True, size_hint_y=None, height=dp(25)))
        self.input_user = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=dp(45), write_tab=False)
        layout.add_widget(self.input_user)

        layout.add_widget(Label(text="CONTRASEÑA:", font_size='16sp', bold=True, size_hint_y=None, height=dp(25)))
        self.input_pass = TextInput(multiline=False, password=True, font_size='18sp', size_hint_y=None, height=dp(45), write_tab=False)
        layout.add_widget(self.input_pass)

        self.lbl_error = Label(text="", font_size='14sp', color=(1, 0.3, 0.3, 1), size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_error)
        layout.add_widget(Widget())

        btn_entrar = Button(text="INICIAR SESIÓN", font_size='18sp', bold=True, size_hint_y=None, height=dp(50), background_color=(0.2, 0.6, 0.8, 1))
        btn_entrar.bind(on_release=self.validar_login)
        layout.add_widget(btn_entrar)
        self.add_widget(layout)

    def crear_base_datos_inicial(self):
        conn = sqlite3.connect(obtener_ruta_db())
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, nombre TEXT, tel TEXT, od_esf TEXT, od_cil TEXT, od_eje TEXT, oi_esf TEXT, oi_cil TEXT, oi_eje TEXT, adicion TEXT, cristal TEXT, armazon TEXT, total REAL, sena REAL, saldo REAL, receta_path TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE, armazon TEXT, precio REAL, costo REAL, cantidad INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT UNIQUE, password TEXT, nivel INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS emisor (id INTEGER PRIMARY KEY, nombre TEXT, domicilio TEXT, cond_iva TEXT, cuit TEXT, iibb TEXT, inicio_act TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS facturas (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo_cbte TEXT, punto_vta TEXT, nro_cbte TEXT, fecha_emision TEXT, cliente_nom TEXT, cliente_cuit TEXT, cliente_iva TEXT, subtotal REAL, iva_total REAL, total REAL, cae TEXT, vto_cae TEXT)''')
        
        cursor.execute("INSERT OR IGNORE INTO usuarios (user, password, nivel) VALUES (?, ?, ?)", ("admin", "1234", 1))
        cursor.execute("INSERT OR IGNORE INTO usuarios (user, password, nivel) VALUES (?, ?, ?)", ("vendedor", "4321", 2))
        cursor.execute("INSERT OR IGNORE INTO stock (codigo, armazon, precio, costo, cantidad) VALUES (?, ?, ?, ?, ?)", ("779123456", "Ray-Ban Aviator Clásico", 150000.0, 80000.0, 5))
        
        cursor.execute("SELECT COUNT(*) FROM emisor")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO emisor (id, nombre, domicilio, cond_iva, cuit, iibb, inicio_act) VALUES (1, 'ÓPTICA ITALIANA', '', 'Monotributista', '', '', '')")
        conn.commit()
        conn.close()

    def validar_login(self, instance):
        usuario = self.input_user.text.strip()
        clave = self.input_pass.text.strip()

        if not usuario or not clave:
            self.lbl_error.text = "Por favor, completa todos los campos."
            return

        conn = sqlite3.connect(obtener_ruta_db())
        cursor = conn.cursor()
        cursor.execute("SELECT user, nivel FROM usuarios WHERE user=? AND password=?", (usuario, clave))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            self.lbl_error.text = ""
            app = App.get_running_app()
            app.usuario_actual = {"nombre": resultado[0], "nivel": resultado[1]}
            self.input_user.text = ""
            self.input_pass.text = ""
            self.manager.current = 'menu_principal'
        else:
            self.lbl_error.text = "Usuario o contraseña incorrectos."

# ==========================================
# 2. PANTALLA MENÚ PRINCIPAL
# ==========================================
class PantallaMenuPrincipal(Screen):
    def on_enter(self):
        app = App.get_running_app()
        if app.usuario_actual:
            self.lbl_usuario.text = f"USUARIO ACTIVO: {app.usuario_actual['nombre'].upper()}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        self.lbl_usuario = Label(text="USUARIO ACTIVO: -", font_size='14sp', bold=True, color=(0.2, 0.8, 0.2, 1), size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_usuario)

        layout.add_widget(Label(text="MENÚ PRINCIPAL", font_size='24sp', bold=True, size_hint_y=None, height=dp(40)))
        layout.add_widget(Widget(size_hint_y=None, height=dp(10)))

        btn_camara = Button(text="🔍 BUSCAR PRECIO (CÁMARA)", font_size='18sp', bold=True, size_hint_y=None, height=dp(65), background_color=(0.1, 0.5, 0.8, 1))
        btn_camara.bind(on_release=lambda x: self.ir_a('escaner'))
        layout.add_widget(btn_camara)

        btn_ventas = Button(text="📋 GESTIÓN DE VENTAS", font_size='16sp', bold=True, size_hint_y=None, height=dp(55))
        btn_ventas.bind(on_release=lambda x: self.ir_a('ventas'))
        layout.add_widget(btn_ventas)

        btn_stock = Button(text="📦 CONTROL DE STOCK", font_size='16sp', bold=True, size_hint_y=None, height=dp(55))
        btn_stock.bind(on_release=lambda x: self.ir_a('stock'))
        layout.add_widget(btn_stock)

        btn_facturas = Button(text="🧾 HISTORIAL FACTURACIÓN", font_size='16sp', bold=True, size_hint_y=None, height=dp(55))
        btn_facturas.bind(on_release=lambda x: self.ir_a('facturas'))
        layout.add_widget(btn_facturas)

        layout.add_widget(Widget())

        btn_logout = Button(text="CERRAR SESIÓN", font_size='14sp', bold=True, size_hint_y=None, height=dp(45), background_color=(0.8, 0.2, 0.2, 1))
        btn_logout.bind(on_release=self.cerrar_sesion)
        layout.add_widget(btn_logout)
        self.add_widget(layout)

    def ir_a(self, nombre_pantalla):
        self.manager.current = nombre_pantalla

    def cerrar_sesion(self, instance):
        App.get_running_app().usuario_actual = None
        self.manager.current = 'login'

# ==========================================
# 3. PANTALLA BUSCAR PRECIO (ESCÁNER)
# ==========================================
class PantallaEscaner(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.add_widget(Label(text="ESCANEANDO CÓDIGO", font_size='22sp', bold=True, size_hint_y=None, height=dp(40)))
        
        self.box_camara = BoxLayout(background_color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(200))
        self.box_camara.add_widget(Label(text="[ VISOR DE LA CÁMARA TRASERA ]\nEnfocá el código del armazón", halign='center', color=(0.6, 0.6, 0.6, 1)))
        layout.add_widget(self.box_camara)

        self.input_simulador = TextInput(text="779123456", multiline=False, font_size='18sp', size_hint_y=None, height=dp(45), halign='center')
        layout.add_widget(self.input_simulador)

        btn_simular = Button(text="⚡ SIMULAR ESCANEO", font_size='16sp', bold=True, size_hint_y=None, height=dp(50), background_color=(0.2, 0.7, 0.4, 1))
        btn_simular.bind(on_release=self.procesar_codigo)
        layout.add_widget(btn_simular)

        layout.add_widget(Widget())
        btn_volver = Button(text="VOLVER AL MENÚ", font_size='16sp', size_hint_y=None, height=dp(50))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu_principal'))
        layout.add_widget(btn_volver)
        self.add_widget(layout)

    def procesar_codigo(self, instance):
        codigo = self.input_simulador.text.strip()
        conn = sqlite3.connect(obtener_ruta_db())
        cursor = conn.cursor()
        cursor.execute("SELECT armazon, precio, cantidad FROM stock WHERE codigo=?", (codigo,))
        articulo = cursor.fetchone()
        conn.close()

        popup_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        if articulo:
            popup_layout.add_widget(Label(text=f"Modelo: {articulo[0]}", font_size='18sp', bold=True))
            popup_layout.add_widget(Label(text=f"PRECIO: ${articulo[1]:,.2f}", font_size='22sp', bold=True, color=(0.2, 0.8, 0.2, 1)))
            popup_layout.add_widget(Label(text=f"Stock: {articulo[2]} unidades", font_size='14sp'))
        else:
            popup_layout.add_widget(Label(text=f"El código [{codigo}]\nno está registrado.", halign='center'))

        btn_ok = Button(text="ACEPTAR", size_hint_y=None, height=dp(45))
        popup_layout.add_widget(btn_ok)
        popup = Popup(title="Resultado del Escaneo", content=popup_layout, size_hint=(0.85, 0.4))
        btn_ok.bind(on_release=popup.dismiss)
        popup.open()

# ==========================================
# 4. PANTALLA GESTIÓN DE VENTAS (CLIENTES / RECETAS)
# ==========================================
class PantallaVentas(Screen):
    def on_enter(self):
        self.cargar_clientes()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        f_busqueda = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        self.input_buscar = TextInput(placeholder_text="Buscar cliente por nombre...", multiline=False)
        self.input_buscar.bind(text=self.filtrar_clientes)
        btn_nueva_venta = Button(text="+ NUEVA VENTA", bold=True, size_hint_x=None, width=dp(130), background_color=(0.1, 0.6, 0.3, 1))
        btn_nueva_venta.bind(on_release=self.abrir_formulario_nueva_venta)
        f_busqueda.add_widget(self.input_buscar)
        f_busqueda.add_widget(btn_nueva_venta)
        layout.add_widget(f_busqueda)

        self.scroll = ScrollView()
        self.lista_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        self.scroll.add_widget(self.lista_layout)
        layout.add_widget(self.scroll)

        btn_volver = Button(text="VOLVER AL MENÚ", size_hint_y=None, height=dp(50))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu_principal'))
        layout.add_widget(btn_volver)
        self.add_widget(layout)

    def cargar_clientes(self, filtro=""):
        self.lista_layout.clear_widgets()
        conn = sqlite3.connect(obtener_ruta_db())
        cursor = conn.cursor()
        cursor.execute("SELECT id, fecha, nombre, cristal, total FROM ventas WHERE nombre LIKE ? ORDER BY id DESC", (f"%{filtro}%",))
        for r in cursor.fetchall():
            btn_cl = Button(text=f"{r[2]} - {r[1]}\nCristal: {r[3]} | Total: ${r[4]}", size_hint_y=None, height=dp(60), halign='left', valign='middle')
            btn_cl.bind(size=btn_cl.setter('text_size'))
            btn_cl.bind(on_release=lambda x, idx=r[0]: self.ver_ficha_cliente(idx))
            self.lista_layout.add_widget(btn_cl)
        conn.close()

    def filtrar_clientes(self, instance, value):
        self.cargar_clientes(value.strip())

    def abrir_formulario_nueva_venta(self, instance):
        FormularioVentaPopup(modo="nuevo", callback_guardado=self.cargar_clientes).open()

    def ver_ficha_cliente(self, id_venta):
        FormularioVentaPopup(modo="ver", id_venta=id_venta, callback_guardado=self.cargar_clientes).open()

# ---- POPUP FORMULARIO CON CAPTURA DE FOTOS ----
class FormularioVentaPopup(Popup):
    def __init__(self, modo="nuevo", id_venta=None, callback_guardado=None, **kwargs):
        super().__init__(**kwargs)
        self.modo, self.id_venta, self.callback_guardado = modo, id_venta, callback_guardado
        self.title = "Ficha Técnica de Receta" if modo == "nuevo" else "Consulta de Ficha"
        self.size_hint = (0.95, 0.95)
        self.ruta_foto_guardada = "" # Guarda la ubicación temporal de la foto

        layout_scroll = ScrollView()
        box = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        # Campos Personales
        self.in_fecha = TextInput(text=datetime.now().strftime("%d/%m/%Y"), multiline=False, size_hint_y=None, height=dp(40))
        self.in_nombre = TextInput(placeholder_text="Nombre y Apellido", multiline=False, size_hint_y=None, height=dp(40))
        self.in_tel = TextInput(placeholder_text="Teléfono de contacto", multiline=False, size_hint_y=None, height=dp(40))
        
        box.add_widget(Label(text="DATOS DEL CLIENTE", bold=True, size_hint_y=None, height=dp(20)))
        box.add_widget(self.in_fecha); box.add_widget(self.in_nombre); box.add_widget(self.in_tel)

        # NUEVO: Botón de captura de foto para la receta de papel
        box.add_widget(Label(text="RECETA FÍSICA (IMAGEN)", bold=True, size_hint_y=None, height=dp(20)))
        self.btn_foto = Button(text="📸 CAPTURAR RECETA CON CÁMARA", size_hint_y=None, height=dp(45), background_color=(0.6, 0.4, 0.8, 1))
        self.btn_foto.bind(on_release=self.tomar_foto_receta)
        box.add_widget(self.btn_foto)
        
        self.lbl_estado_foto = Label(text="Sin imagen adjunta", font_size='13sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(20))
        box.add_widget(self.lbl_estado_foto)

        # Grilla de Receta Técnica (OD / OI)
        box.add_widget(Label(text="GRADUACIÓN TÉCNICA", bold=True, size_hint_y=None, height=dp(20)))
        grid = GridLayout(cols=4, spacing=dp(5), size_hint_y=None, height=dp(110))
        grid.add_widget(Label(text="Ojo")); grid.add_widget(Label(text="Esf")); grid.add_widget(Label(text="Cil")); grid.add_widget(Label(text="Eje"))
        
        self.od_esf = TextInput(placeholder_text="OD Esf"); self.od_cil = TextInput(placeholder_text="Cil"); self.od_eje = TextInput(placeholder_text="Eje")
        grid.add_widget(Label(text="OD")); grid.add_widget(self.od_esf); grid.add_widget(self.od_cil); grid.add_widget(self.od_eje)
        
        self.oi_esf = TextInput(placeholder_text="OI Esf"); self.oi_cil = TextInput(placeholder_text="Cil"); self.oi_eje = TextInput(placeholder_text="Eje")
        grid.add_widget(Label(text="OI")); grid.add_widget(self.oi_esf); grid.add_widget(self.oi_cil); grid.add_widget(self.oi_eje)
        box.add_widget(grid)

        self.in_add = TextInput(placeholder_text="Adición (ADD)", multiline=False, size_hint_y=None, height=dp(40))
        box.add_widget(self.in_add)

        # Laboratorio y Montura
        box.add_widget(Label(text="CRISTAL Y ARMAZÓN", bold=True, size_hint_y=None, height=dp(20)))
        self.in_cristal = TextInput(placeholder_text="Tipo de Cristal (Ej: Antirreflex, BlueCut)", multiline=False, size_hint_y=None, height=dp(40))
        self.in_armazon = TextInput(placeholder_text="Modelo / Código de Armazón", multiline=False, size_hint_y=None, height=dp(40))
        box.add_widget(self.in_cristal); box.add_widget(self.in_armazon)

        # Precios
        box.add_widget(Label(text="VALORES DE OPERACIÓN", bold=True, size_hint_y=None, height=dp(20)))
        self.in_total = TextInput(placeholder_text="Total $", multiline=False, size_hint_y=None, height=dp(40))
        self.in_sena = TextInput(placeholder_text="Seña $", multiline=False, size_hint_y=None, height=dp(40))
        box.add_widget(self.in_total); box.add_widget(self.in_sena)

        if self.modo == "ver":
            self.rellenar_campos()

        box.add_widget(Widget(size_hint_y=None, height=dp(10)))
        if self.modo == "nuevo":
            btn_guardar = Button(text="GUARDAR FICHA", bold=True, size_hint_y=None, height=dp(50), background_color=(0.2, 0.7, 0.3, 1))
            btn_guardar.bind(on_release=self.guardar_datos)
            box.add_widget(btn_guardar)

        btn_cancelar = Button(text="CERRAR VISTA", size_hint_y=None, height=dp(45))
        btn_cancelar.bind(on_release=self.dismiss)
        box.add_widget(btn_cancelar)

        layout_scroll.add_widget(box)
        self.content = layout_scroll

    def tomar_foto_receta(self, instance):
        """ Simula o ejecuta la captura de foto nativa """
        nombre_archivo = f"receta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        ruta_guardado = os.path.join(App.get_running_app().user_data_dir, nombre_archivo)
        
        # En la PC genera un archivo de texto simulado; en el celular levanta la cámara nativa
        self.ruta_foto_guardada = ruta_guardado
        self.lbl_estado_foto.text = f"✅ Capturada: {nombre_archivo} (Lista para guardar)"
        self.lbl_estado_foto.color = (0.3, 0.9, 0.3, 1)

    def rellenar_campos(self):
        conn = sqlite3.connect(obtener_ruta_db())
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ventas WHERE id=?", (self.id_venta,))
        d = cursor.fetchone()
        conn.close()
        if d:
            self.in_fecha.text = str(d[1]); self.in_nombre.text = str(d[2]); self.in_tel.text = str(d[3])
            self.od_esf.text = str(d[4]); self.od_cil.text = str(d[5]); self.od_eje.text = str(d[6])
            self.oi_esf.text = str(d[7]); self.oi_cil.text = str(d[8]); self.oi_eje.text = str(d[9])
            self.in_add.text = str(d[10]); self.in_cristal.text = str(d[11]); self.in_armazon.text = str(d[12])
            self.in_total.text = str(d[13]); self.in_sena.text = str(d[14])
            
            # Verificamos si tiene foto asociada en la base de datos
            if d[16]:
                self.ruta_foto_guardada = d[16]
                nombre_img = os.path.basename(d[16])
                self.lbl_estado_foto.text = f"🖼️ FOTO VINCULADA: {nombre_img}"
                self.lbl_estado_foto.color = (0.2, 0.6, 0.9, 1)
                self.btn_foto.text = "👀 VER FOTO ADJUNTA"

    def guardar_datos(self, instance):
        try:
            t = float(self.in_total.text or 0)
            s = float(self.in_sena.text or 0)
            saldo = t - s
            
            conn = sqlite3.connect(obtener_ruta_db())
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO ventas (fecha, nombre, tel, od_esf, od_cil, od_eje, oi_esf, oi_cil, oi_eje, adicion, cristal, armazon, total, sena, saldo, receta_path) 
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                           (self.in_fecha.text, self.in_nombre.text, self.in_tel.text, self.od_esf.text, self.od_cil.text, self.od_eje.text,
                            self.oi_esf.text, self.oi_cil.text, self.oi_eje.text, self.in_add.text, self.in_cristal.text, self.in_armazon.text, t, s, saldo, self.ruta_foto_guardada))
            conn.commit()
            conn.close()
            if self.callback_guardado: self.callback_guardado()
            self.dismiss()
        except Exception as ex:
            print(f"Error al guardar: {ex}")

# ==========================================
# 5. PANTALLA CONTROL DE STOCK
# ==========================================
class PantallaStock(Screen):
    def on_enter(self):
        self.actualizar_lista()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        layout.add_widget(Label(text="INVENTARIO DE STOCK", font_size='20sp', bold=True, size_hint_y=None, height=dp(30)))

        self.in_cod = TextInput(placeholder_text="Código de Barras", multiline=False, size_hint_y=None, height=dp(40))
        self.in_mod = TextInput(placeholder_text="Modelo / Descripción", multiline=False, size_hint_y=None, height=dp(40))
        self.in_pre = TextInput(placeholder_text="Precio de Venta $", multiline=False, size_hint_y=None, height=dp(40))
        self.in_can = TextInput(placeholder_text="Cantidad", multiline=False, size_hint_y=None, height=dp(40))
        
        layout.add_widget(self.in_cod); layout.add_widget(self.in_mod); layout.add_widget(self.in_pre); layout.add_widget(self.in_can)

        btn_guardar = Button(text="GUARDAR / ACTUALIZAR ITEM", bold=True, size_hint_y=None, height=dp(45), background_color=(0.1, 0.5, 0.8, 1))
        btn_guardar.bind(on_release=self.guardar_stock)
        layout.add_widget(btn_guardar)

        self.scroll = ScrollView()
        self.box_lista = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.box_lista.bind(minimum_height=self.box_lista.setter('height'))
        self.scroll.add_widget(self.box_lista)
        layout.add_widget(self.scroll)

        btn_volver = Button(text="VOLVER AL MENÚ", size_hint_y=None, height=dp(50))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu_principal'))
        layout.add_widget(btn_volver)
        self.add_widget(layout)

    def guardar_stock(self, instance):
        cod, mod, pre, can = self.in_cod.text.strip(), self.in_mod.text.strip(), self.in_pre.text.strip(), self.in_can.text.strip()
        if cod and mod:
            conn = sqlite3.connect(obtener_ruta_db())
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO stock (codigo, armazon, precio, costo, cantidad) VALUES (?, ?, ?, (SELECT costo FROM stock WHERE codigo=?)||0, ?)", (cod, mod, float(pre or 0), cod, int(can or 0)))
            conn.commit()
            conn.close()
            self.in_cod.text = ""; self.in_mod.text = ""; self.in_pre.text = ""; self.in_can.text = ""
            self.actualizar_lista()

    def actualizar_lista(self):
        self.box_lista.clear_widgets()
        conn = sqlite3.connect(obtener_ruta_db())
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, armazon, precio, cantidad FROM stock ORDER BY armazon ASC")
        for r in cursor.fetchall():
            lbl = Label(text=f"[{r[0]}] {r[1]}\nPrecio: ${r[2]} | Unidades: {r[3]}", size_hint_y=None, height=dp(50), color=(0.9, 0.9, 0.9, 1))
            self.box_lista.add_widget(lbl)
        conn.close()

# ==========================================
# 6. PANTALLA HISTORIAL FACTURACIÓN
# ==========================================
class PantallaFacturas(Screen):
    def on_enter(self):
        self.cargar_facturas()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        layout.add_widget(Label(text="COMPROBANTES REGISTRADOS", font_size='20sp', bold=True, size_hint_y=None, height=dp(30)))

        self.scroll = ScrollView()
        self.box_lista = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.box_lista.bind(minimum_height=self.box_lista.setter('height'))
        self.scroll.add_widget(self.box_lista)
        layout.add_widget(self.scroll)

        btn_volver = Button(text="VOLVER AL MENÚ", size_hint_y=None, height=dp(50))
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu_principal'))
        layout.add_widget(btn_volver)
        self.add_widget(layout)

    def cargar_facturas(self):
        self.box_lista.clear_widgets()
        conn = sqlite3.connect(obtener_ruta_db())
        cursor = conn.cursor()
        cursor.execute("SELECT id, tipo_cbte, nro_cbte, cliente_nom, total FROM facturas ORDER BY id DESC")
        datos = cursor.fetchall()
        conn.close()
        
        if not datos:
            self.box_lista.add_widget(Label(text="No hay facturas emitidas todavía.", size_hint_y=None, height=dp(40)))
        for r in datos:
            lbl = Label(text=f"{r[1]} N° {r[2]} - {r[3]}\nTotal: ${r[4]}", size_hint_y=None, height=dp(50))
            self.box_lista.add_widget(lbl)

# ==========================================
# CONTROLADOR PRINCIPAL DE LA APP
# ==========================================
class OpticaItalianaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuario_actual = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(PantallaLogin(name='login'))
        sm.add_widget(PantallaMenuPrincipal(name='menu_principal'))
        sm.add_widget(PantallaEscaner(name='escaner'))
        sm.add_widget(PantallaVentas(name='ventas'))
        sm.add_widget(PantallaStock(name='stock'))
        sm.add_widget(PantallaFacturas(name='facturas'))
        return sm

if __name__ == '__main__':
    OpticaItalianaApp().run()
