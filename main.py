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
from kivy.core.window import Window
import sqlite3
import os
import random
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE COLORES GLOBALES (ESTILOS MODERNOS) ---
COLOR_FONDO = (0.1, 0.12, 0.15, 1)      # Gris oscuro premium
COLOR_TARJETA = (0.15, 0.18, 0.22, 1)    # Gris tarjeta
COLOR_PRIMARIO = (0.12, 0.53, 0.9, 1)    # Azul Óptico
COLOR_EXITO = (0.15, 0.65, 0.35, 1)      # Verde AFIP / Guardar
COLOR_ALERTA = (0.85, 0.25, 0.25, 1)    # Rojo alerta

def obtener_ruta_db():
    ruta_app = App.get_running_app().user_data_dir
    return os.path.join(ruta_app, "optica_italiana.db")

# Componente base para aplicar color de fondo a las pantallas de Kivy de forma limpia
class PantallaBase(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = COLOR_FONDO

# ==========================================
# 1. PANTALLA DE LOGIN (CON ESTILOS)
# ==========================================
class PantallaLogin(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.crear_base_datos_inicial()

        layout = BoxLayout(orientation='vertical', padding=dp(35), spacing=dp(15))
        layout.add_widget(Widget(size_hint_y=None, height=dp(30)))

        layout.add_widget(Label(text="ÓPTICA ITALIANA", font_size='32sp', bold=True, color=(1, 1, 1, 1), size_hint_y=None, height=dp(45)))
        layout.add_widget(Label(text="Gestión Móvil Profesional v6.0", font_size='15sp', color=(0.6, 0.65, 0.7, 1), size_hint_y=None, height=dp(20)))
        layout.add_widget(Widget(size_hint_y=None, height=dp(25)))

        layout.add_widget(Label(text="USUARIO", font_size='14sp', bold=True, color=COLOR_PRIMARIO, size_hint_y=None, height=dp(20)))
        self.input_user = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=dp(45), write_tab=False, background_color=(0.2, 0.23, 0.28, 1), foreground_color=(1,1,1,1))
        layout.add_widget(self.input_user)

        layout.add_widget(Label(text="CONTRASEÑA", font_size='14sp', bold=True, color=COLOR_PRIMARIO, size_hint_y=None, height=dp(20)))
        self.input_pass = TextInput(multiline=False, password=True, font_size='18sp', size_hint_y=None, height=dp(45), write_tab=False, background_color=(0.2, 0.23, 0.28, 1), foreground_color=(1,1,1,1))
        layout.add_widget(self.input_pass)

        self.lbl_error = Label(text="", font_size='14sp', color=COLOR_ALERTA, size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_error)
        layout.add_widget(Widget())

        btn_entrar = Button(text="INICIAR SESIÓN", font_size='18sp', bold=True, size_hint_y=None, height=dp(52), background_color=COLOR_PRIMARIO, background_normal='')
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
            cursor.execute("INSERT INTO emisor (id, nombre, domicilio, cond_iva, cuit, iibb, inicio_act) VALUES (1, 'ÓPTICA ITALIANA', 'Lanús, Buenos Aires', 'Monotributista', '20-38475839-7', '20-38475839-7', '01/03/2018')")
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
# 2. PANTALLA MENÚ PRINCIPAL (CON ESTILOS)
# ==========================================
class PantallaMenuPrincipal(PantallaBase):
    def on_enter(self):
        app = App.get_running_app()
        if app.usuario_actual:
            self.lbl_usuario.text = f"SESIÓN ACTIVA: {app.usuario_actual['nombre'].upper()}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        self.lbl_usuario = Label(text="SESIÓN ACTIVA: -", font_size='13sp', bold=True, color=(0.4, 0.8, 0.4, 1), size_hint_y=None, height=dp(25))
        layout.add_widget(self.lbl_usuario)

        layout.add_widget(Label(text="PANEL PRINCIPAL", font_size='24sp', bold=True, color=(1,1,1,1), size_hint_y=None, height=dp(35)))
        layout.add_widget(Widget(size_hint_y=None, height=dp(5)))

        # --- BOTONERA PRINCIPAL PREMIUM ---
        btn_camara = Button(text="🔍  BUSCAR PRECIO (CÁMARA)", font_size='17sp', bold=True, size_hint_y=None, height=dp(65), background_color=COLOR_PRIMARIO, background_normal='')
        btn_camara.bind(on_release=lambda x: self.ir_a('escaner'))
        layout.add_widget(btn_camara)

        btn_ventas = Button(text="📋  GESTIÓN DE VENTAS", font_size='16sp', bold=True, size_hint_y=None, height=dp(55), background_color=COLOR_TARJETA, background_normal='')
        btn_ventas.bind(on_release=lambda x: self.ir_a('ventas'))
        layout.add_widget(btn_ventas)

        btn_stock = Button(text="📦  CONTROL DE STOCK", font_size='16sp', bold=True, size_hint_y=None, height=dp(55), background_color=COLOR_TARJETA, background_normal='')
        btn_stock.bind(on_release=lambda x: self.ir_a('stock'))
        layout.add_widget(btn_stock)

        btn_facturas = Button(text="🧾  HISTORIAL DE FACTURACIÓN", font_size='16sp', bold=True, size_hint_y=None, height=dp(55), background_color=COLOR_TARJETA, background_normal='')
        btn_facturas.bind(on_release=lambda x: self.ir_a('facturas'))
        layout.add_widget(btn_facturas)

        layout.add_widget(Widget())

        btn_logout = Button(text="CERRAR SESIÓN ASIGNADA", font_size='14sp', bold=True, size_hint_y=None, height=dp(45), background_color=COLOR_ALERTA, background_normal='')
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
class PantallaEscaner(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.add_widget(Label(text="ESCANEANDO CÓDIGO", font_size='22sp', bold=True, size_hint_y=None, height=dp(40)))
        
        self.box_camara = BoxLayout(background_color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(180))
        self.box_camara.add_widget(Label(text="[ INTERFAZ DE CÁMARA ACTIVA ]\nEnfocá el código de barras en el armazón", halign='center', color=(0.6, 0.65, 0.7, 1)))
        layout.add_widget(self.box_camara)

        self.input_simulador = TextInput(text="779123456", multiline=False, font_size='18sp', size_hint_y=None, height=dp(45), halign='center', background_color=(0.2, 0.23, 0.28, 1), foreground_color=(1,1,1,1))
        layout.add_widget(self.input_simulador)

        btn_simular = Button(text="⚡ SIMULAR LECTURA LÁSER", font_size='16sp', bold=True, size_hint_y=None, height=dp(50), background_color=COLOR_EXITO, background_normal='')
        btn_simular.bind(on_release=self.procesar_codigo)
        layout.add_widget(btn_simular)

        layout.add_widget(Widget())
        btn_volver = Button(text="VOLVER AL MENÚ", font_size='16sp', size_hint_y=None, height=dp(50), background_color=COLOR_TARJETA, background_normal='')
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

        popup_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        if articulo:
            popup_layout.add_widget(Label(text=f"Modelo: {articulo[0]}", font_size='18sp', bold=True))
            popup_layout.add_widget(Label(text=f"PRECIO: ${articulo[1]:,.2f}", font_size='24sp', bold=True, color=(0.3, 0.85, 0.4, 1)))
            popup_layout.add_widget(Label(text=f"Unidades en Stock: {articulo[2]} u.", font_size='15sp', color=(0.7, 0.75, 0.8, 1)))
        else:
            popup_layout.add_widget(Label(text=f"El código de barras [{codigo}]\nno existe en el inventario.", halign='center', color=COLOR_ALERTA))

        btn_ok = Button(text="ENTENDIDO", size_hint_y=None, height=dp(45), background_color=COLOR_PRIMARIO, background_normal='')
        popup_layout.add_widget(btn_ok)
        popup = Popup(title="Lector de Precios Móvil", content=popup_layout, size_hint=(0.85, 0.42), background_color=COLOR_TARJETA)
        btn_ok.bind(on_release=popup.dismiss)
        popup.open()

# ==========================================
# 4. PANTALLA GESTIÓN DE VENTAS (CLIENTES)
# ==========================================
class PantallaVentas(PantallaBase):
    def on_enter(self):
        self.cargar_clientes()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        f_busqueda = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        self.input_buscar = TextInput(placeholder_text="Buscar por nombre de cliente...", multiline=False, background_color=(0.2, 0.23, 0.28, 1), foreground_color=(1,1,1,1))
        self.input_buscar.bind(text=self.filtrar_clientes)
        btn_nueva_venta = Button(text="+ NUEVA VENTA", bold=True, size_hint_x=None, width=dp(135), background_color=COLOR_EXITO, background_normal='')
        btn_nueva_venta.bind(on_release=self.abrir_formulario_nueva_venta)
        f_busqueda.add_widget(self.input_buscar)
        f_busqueda.add_widget(btn_nueva_venta)
        layout.add_widget(f_busqueda)

        self.scroll = ScrollView()
        self.lista_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6))
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        self.scroll.add_widget(self.lista_layout)
        layout.add_widget(self.scroll)

        btn_volver = Button(text="VOLVER AL MENÚ", size_hint_y=None, height=dp(50), background_color=COLOR_TARJETA, background_normal='')
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu_principal'))
        layout.add_widget(btn_volver)
        self.add_widget(layout)

    def cargar_clientes(self, filtro=""):
        self.lista_layout.clear_widgets()
        conn = sqlite3.connect(obtener_ruta_db())
        cursor = conn.cursor()
        cursor.execute("SELECT id, fecha, nombre, cristal, total FROM ventas WHERE nombre LIKE ? ORDER BY id DESC", (f"%{filtro}%",))
        for r in cursor.fetchall():
            btn_cl = Button(text=f" 👤 {r[2].upper()} ({r[1]})\n  Cristal: {r[3]} | Total de Venta: ${r[4]:,.2f}", size_hint_y=None, height=dp(65), halign='left', valign='middle', background_color=COLOR_TARJETA, background_normal='')
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


# ---- POPUP DE CARGA DE RECETAS + CONTROL INTEGRADO DE AFIP ----
class FormularioVentaPopup(Popup):
    def __init__(self, modo="nuevo", id_venta=None, callback_guardado=None, **kwargs):
        super().__init__(**kwargs)
        self.modo, self.id_venta, self.callback_guardado = modo, id_venta, callback_guardado
        self.title = "Ficha Técnica de Receta" if modo == "nuevo" else "Visualización Completa de Operación"
        self.size_hint = (0.95, 0.95)
        self.ruta_foto_guardada = ""
        self.background_color = COLOR_FONDO

        layout_scroll = ScrollView()
        box = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        # Datos Generales
        box.add_widget(Label(text="DATOS FILIATORIOS", bold=True, color=COLOR_PRIMARIO, size_hint_y=None, height=dp(20)))
        self.in_fecha = TextInput(text=datetime.now().strftime("%d/%m/%Y"), multiline=False, size_hint_y=None, height=dp(40), background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        self.in_nombre = TextInput(placeholder_text="Nombre Completo del Paciente", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        self.in_tel = TextInput(placeholder_text="N° de Teléfono Celular", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        box.add_widget(self.in_fecha); box.add_widget(self.in_nombre); box.add_widget(self.in_tel)

        # Captura de Imágenes
        box.add_widget(Label(text="REGISTRO ÓPTICO DE PAPEL", bold=True, color=COLOR_PRIMARIO, size_hint_y=None, height=dp(20)))
        self.btn_foto = Button(text="📸  FOTOGRAFIAR ORDEN DE MÉDICO", size_hint_y=None, height=dp(45), background_color=(0.45, 0.3, 0.7, 1), background_normal='')
        self.btn_foto.bind(on_release=self.tomar_foto_receta)
        box.add_widget(self.btn_foto)
        self.lbl_estado_foto = Label(text="Sin imagen enlazada en el registro", font_size='13sp', color=(0.6,0.6,0.6,1), size_hint_y=None, height=dp(18))
        box.add_widget(self.lbl_estado_foto)

        # Graduación Técnica Completa
        box.add_widget(Label(text="GRADUACIÓN DE CRISTALES", bold=True, color=COLOR_PRIMARIO, size_hint_y=None, height=dp(20)))
        grid = GridLayout(cols=4, spacing=dp(5), size_hint_y=None, height=dp(110))
        grid.add_widget(Label(text="Ojo", bold=True)); grid.add_widget(Label(text="Esférico")); grid.add_widget(Label(text="Cilíndrico")); grid.add_widget(Label(text="Eje"))
        
        self.od_esf = TextInput(placeholder_text="OD Esf", background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        self.od_cil = TextInput(placeholder_text="Cil", background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        self.od_eje = TextInput(placeholder_text="Eje", background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        grid.add_widget(Label(text="OD", bold=True, color=COLOR_PRIMARIO)); grid.add_widget(self.od_esf); grid.add_widget(self.od_cil); grid.add_widget(self.od_eje)
        
        self.oi_esf = TextInput(placeholder_text="OI Esf", background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        self.oi_cil = TextInput(placeholder_text="Cil", background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        self.oi_eje = TextInput(placeholder_text="Eje", background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        grid.add_widget(Label(text="OI", bold=True, color=COLOR_PRIMARIO)); grid.add_widget(self.oi_esf); grid.add_widget(self.oi_cil); grid.add_widget(self.oi_eje)
        box.add_widget(grid)

        self.in_add = TextInput(placeholder_text="Adición Técnica (ADD)", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        box.add_widget(self.in_add)

        # Insumos
        box.add_widget(Label(text="TRABAJO DE LABORATORIO", bold=True, color=COLOR_PRIMARIO, size_hint_y=None, height=dp(20)))
        self.in_cristal = TextInput(placeholder_text="Especificación del Cristal (Ej: Orgánico, Policarbonato)", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        self.in_armazon = TextInput(placeholder_text="Código o Nombre del Armazón Utilizado", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        box.add_widget(self.in_cristal); box.add_widget(self.in_armazon)

        # Costos de Caja
        box.add_widget(Label(text="MONTOS ECONÓMICOS", bold=True, color=COLOR_PRIMARIO, size_hint_y=None, height=dp(20)))
        self.in_total = TextInput(placeholder_text="Importe Total Neto $", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        self.in_sena = TextInput(placeholder_text="Monto de Seña Entregado $", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.12, 0.14, 0.18, 1), foreground_color=(1,1,1,1))
        box.add_widget(self.in_total); box.add_widget(self.in_sena)

        if self.modo == "ver":
            self.rellenar_campos()
            # PASO 1 INTEGRADO: Solo el administrador puede emitir facturas electrónicas AFIP
            app = App.get_running_app()
            if app.usuario_actual and app.usuario_actual['nivel'] == 1:
                box.add_widget(Widget(size_hint_y=None, height=dp(10)))
                self.btn_afip = Button(text="🧾  FACTURAR COMPROBANTE (AFIP)", bold=True, size_hint_y=None, height=dp(50), background_color=(0.9, 0.55, 0.1, 1), background_normal='')
                self.btn_afip.bind(on_release=self.emitir_factura_electronica_afip)
                box.add_widget(self.btn_afip)

        box.add_widget(Widget(size_hint_y=None, height=dp(12)))
        if self.modo == "nuevo":
            btn_guardar = Button(text="GUARDAR NUEVA REGISTRACIÓN", bold=True, size_hint_y=None, height=dp(52), background_color=COLOR_EXITO, background_normal='')
            btn_guardar.bind(on_release=self.guardar_datos)
            box.add_widget(btn_guardar)

        btn_cancelar = Button(text="CERRAR VENTANA", size_hint_y=None, height=dp(45), background_color=COLOR_TARJETA, background_normal='')
        btn_cancelar.bind(on_release=self.dismiss)
        box.add_widget(btn_cancelar)

        layout_scroll.add_widget(box)
        self.content = layout_scroll

    def tomar_foto_receta(self, instance):
        nombre_archivo = f"receta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        self.ruta_foto_guardada = os.path.join(App.get_running_app().user_data_dir, nombre_archivo)
        self.lbl_estado_foto.text = f"✅ Cámara activada: {nombre_archivo} lista"
        self.lbl_estado_foto.color = (0.3, 0.9, 0.4, 1)

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
            if d[16]:
                self.ruta_foto_guardada = d[16]
                self.lbl_estado_foto.text = f"🖼️ IMAGEN VINCULADA: {os.path.basename(d[16])}"
                self.lbl_estado_foto.color = COLOR_PRIMARIO
                self.btn_foto.text = "👀 VISUALIZAR CAPTURA ASOCIADA"

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

    # ========================================================
    # PASO 1 DESARROLLADO: SIMULACIÓN INTERNA DE AFIP REAL (WSFEV1)
    # ========================================================
    def emitir_factura_electronica_afip(self, instance):
        nombre_cliente = self.input_owner_name = self.in_nombre.text.strip() or "Consumidor Final"
        monto_total = float(self.in_total.text or 0)

        if monto_total <= 0:
            return

        conn = sqlite3.connect(obtener_ruta_db())
        cursor = conn.cursor()
        
        # Obtenemos los datos del emisor de la óptica cargados en la tabla
        cursor.execute("SELECT cuit, cond_iva FROM emisor WHERE id=1")
        emisor = cursor.fetchone()
        
        # Buscamos el último comprobante para simular la correlatividad del Web Service de AFIP
        cursor.execute("SELECT COUNT(*) FROM facturas")
        prox_nro = cursor.fetchone()[0] + 1
        nro_comprobante = f"00004-{prox_nro:08d}"

        # Lógica tributaria: Si es Monotributista emite Factura B o C
        tipo_comprobante = "Factura C" if emisor and emisor[1] == "Monotributista" else "Factura B"
        
        # Generación de variables fiscales devueltas por AFIP
        cae_devuelto = str(random.randint(76000000000000, 76999999999999))
        vencimiento_cae = (datetime.now() + timedelta(days=10)).strftime("%d/%m/%Y")
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")

        # Guardamos el comprobante fiscal homologado en la Base de Datos
        cursor.execute('''INSERT INTO facturas (tipo_cbte, punto_vta, nro_cbte, fecha_emision, cliente_nom, cliente_cuit, cliente_iva, subtotal, iva_total, total, cae, vto_cae) 
                       VALUES (?, '00004', ?, ?, ?, '99-99999999-9', 'Consumidor Final', ?, 0.0, ?, ?, ?)''',
                       (tipo_comprobante, nro_comprobante, fecha_hoy, nombre_cliente, monto_total, monto_total, cae_devuelto, vencimiento_cae))
        conn.commit()
        conn.close()

        # Ventana de Éxito de conexión con Servidores AFIP
        pop_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        pop_layout.add_widget(Label(text="¡COMPROBANTE AFIP AUTORIZADO!", bold=True, color=(0.3, 0.9, 0.4, 1), font_size='16sp'))
        pop_layout.add_widget(Label(text=f"{tipo_comprobante} N° {nro_comprobante}", font_size='14sp'))
        pop_layout.add_widget(Label(text=f"CAE Otorgado: {cae_devuelto}", bold=True))
        pop_layout.add_widget(Label(text=f"Vto CAE: {vencimiento_cae}", font_size='13sp', color=(0.7,0.7,0.7,1)))

        btn_cerrar = Button(text="ACEPTAR", size_hint_y=None, height=dp(45), background_color=COLOR_PRIMARIO, background_normal='')
        pop_layout.add_widget(btn_cerrar)
        
        popup_afip = Popup(title="WebService AFIP Conectado", content=pop_layout, size_hint=(0.85, 0.45))
        btn_cerrar.bind(on_release=popup_afip.dismiss)
        popup_afip.open()

# ==========================================
# 5. PANTALLA CONTROL DE STOCK (CON ESTILOS)
# ==========================================
class PantallaStock(PantallaBase):
    def on_enter(self):
        self.actualizar_lista()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        layout.add_widget(Label(text="INVENTARIO GLOBAL DE MARCAS", font_size='20sp', bold=True, size_hint_y=None, height=dp(30)))

        # Formulario Estilizado
        self.in_cod = TextInput(placeholder_text="Código de Barras del Armazón", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.2, 0.23, 0.28, 1), foreground_color=(1,1,1,1))
        self.in_mod = TextInput(placeholder_text="Marca / Modelo (Ej: RayBan, Vulk)", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.2, 0.23, 0.28, 1), foreground_color=(1,1,1,1))
        self.in_pre = TextInput(placeholder_text="Precio de Lista al Público $", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.2, 0.23, 0.28, 1), foreground_color=(1,1,1,1))
        self.in_can = TextInput(placeholder_text="Cantidad de Unidades Entrantes", multiline=False, size_hint_y=None, height=dp(40), background_color=(0.2, 0.23, 0.28, 1), foreground_color=(1,1,1,1))
        
        layout.add_widget(self.in_cod); layout.add_widget(self.in_mod); layout.add_widget(self.in_pre); layout.add_widget(self.in_can)

        btn_guardar = Button(text="MODIFICAR O GUARDAR ITEM", bold=True, size_hint_y=None, height=dp(45), background_color=COLOR_PRIMARIO, background_normal='')
        btn_guardar.bind(on_release=self.guardar_stock)
        layout.add_widget(btn_guardar)

        self.scroll = ScrollView()
        self.box_lista = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.box_lista.bind(minimum_height=self.box_lista.setter('height'))
        self.scroll.add_widget(self.box_lista)
        layout.add_widget(self.scroll)

        btn_volver = Button(text="VOLVER AL MENÚ", size_hint_y=None, height=dp(50), background_color=COLOR_TARJETA, background_normal='')
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
            lbl = Label(text=f" 📦 [{r[0]}] {r[1].upper()}\n      Precio Venta: ${r[2]:,.2f} | Disponibles: {r[3]} u.", size_hint_y=None, height=dp(55), halign='left', valign='middle', color=(0.9, 0.93, 0.96, 1))
            lbl.bind(size=lbl.setter('text_size'))
            self.box_lista.add_widget(lbl)
        conn.close()

# ==========================================
# 6. PANTALLA HISTORIAL FACTURACIÓN
# ==========================================
class PantallaFacturas(PantallaBase):
    def on_enter(self):
        self.cargar_facturas()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        layout.add_widget(Label(text="REGISTRO DE COMPROBANTES AFIP", font_size='20sp', bold=True, size_hint_y=None, height=dp(30)))

        self.scroll = ScrollView()
        self.box_lista = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6))
        self.box_lista.bind(minimum_height=self.box_lista.setter('height'))
        self.scroll.add_widget(self.box_lista)
        layout.add_widget(self.scroll)

        btn_volver = Button(text="VOLVER AL MENÚ", size_hint_y=None, height=dp(50), background_color=COLOR_TARJETA, background_normal='')
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu_principal'))
        layout.add_widget(btn_volver)
        self.add_widget(layout)

    def cargar_facturas(self):
        self.box_lista.clear_widgets()
        conn = sqlite3.connect(obtener_ruta_db())
        cursor = conn.cursor()
        cursor.execute("SELECT id, tipo_cbte, nro_cbte, cliente_nom, total, cae FROM facturas ORDER BY id DESC")
        datos = cursor.fetchall()
        conn.close()
        
        if not datos:
            self.box_lista.add_widget(Label(text="No hay transacciones fiscales registradas.", size_hint_y=None, height=dp(40), color=(0.6,0.6,0.6,1)))
        for r in datos:
            lbl = Label(text=f" 🧾 {r[1]} N° {r[2]} - {r[3].upper()}\n      Importe Total: ${r[4]:,.2f} | CAE: {r[5]}", size_hint_y=None, height=dp(55), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
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
