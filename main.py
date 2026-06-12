Python
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp
import sqlite3
import os

class PantallaLogin(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ruta_app = App.get_running_app().user_data_dir
        self.base_datos = os.path.join(ruta_app, "optica_italiana.db")
        self.crear_base_datos_inicial()

        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))
        layout.add_widget(Widget(size_hint_y=None, height=dp(40)))

        layout.add_widget(Label(text="ÓPTICA ITALIANA", font_size='28sp', bold=True, size_hint_y=None, height=dp(45)))
        layout.add_widget(Label(text="Gestión Móvil v6.0", font_size='16sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(20)))
        layout.add_widget(Widget(size_hint_y=None, height=dp(30)))

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
        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, nombre TEXT, tel TEXT, od_esf TEXT, od_cil TEXT, od_eje TEXT, oi_esf TEXT, oi_cil TEXT, oi_eje TEXT, adicion TEXT, cristal TEXT, armazon TEXT, total REAL, sena REAL, saldo REAL, receta_path TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS stock (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE, armazon TEXT, precio REAL, costo REAL, cantidad INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT UNIQUE, password TEXT, nivel INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS emisor (id INTEGER PRIMARY KEY, nombre TEXT, domicilio TEXT, cond_iva TEXT, cuit TEXT, iibb TEXT, inicio_act TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS facturas (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo_cbte TEXT, punto_vta TEXT, nro_cbte TEXT, fecha_emision TEXT, cliente_nom TEXT, cliente_cuit TEXT, cliente_iva TEXT, subtotal REAL, iva_total REAL, total REAL, cae TEXT, vto_cae TEXT)''')
        cursor.execute("INSERT OR IGNORE INTO usuarios (user, password, nivel) VALUES (?, ?, ?)", ("admin", "1234", 1))
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

        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        cursor.execute("SELECT user, nivel FROM usuarios WHERE user=? AND password=?", (usuario, clave))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            self.lbl_error.text = ""
            app = App.get_running_app()
            app.usuario_actual = {"nombre": resultado[0], "nivel": resultado[1]}
            
            # Limpiamos los campos para cuando se cierre sesión
            self.input_user.text = ""
            self.input_pass.text = ""
            
            # Pasamos a la pantalla del menú principal
            self.manager.current = 'menu_principal'
        else:
            self.lbl_error.text = "Usuario o contraseña incorrectos."


class PantallaMenuPrincipal(Screen):
    def on_enter(self):
        """ Cada vez que entramos al menú, actualizamos el cartel del usuario actual """
        app = App.get_running_app()
        if app.usuario_actual:
            self.lbl_usuario.text = f"USUARIO ACTIVO: {app.usuario_actual['nombre'].upper()}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Barra superior de estado del usuario
        self.lbl_usuario = Label(text="USUARIO ACTIVO: -", font_size='14sp', bold=True, color=(0.2, 0.8, 0.2, 1), size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_usuario)

        layout.add_widget(Label(text="MENÚ PRINCIPAL", font_size='24sp', bold=True, size_hint_y=None, height=dp(40)))
        layout.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # --- BOTONES DEL MENÚ ---
        
        # 1. BOTÓN ESTRELLA: BUSCAR PRECIO CON CÁMARA
        btn_camara = Button(text="🔍 BUSCAR PRECIO (CÁMARA)", font_size='18sp', bold=True, size_hint_y=None, height=dp(65), background_color=(0.1, 0.5, 0.8, 1))
        btn_camara.bind(on_release=self.abrir_escaner)
        layout.add_widget(btn_camara)

        # 2. GESTIÓN DE VENTAS (RECETAS / CLIENTES)
        btn_ventas = Button(text="📋 GESTIÓN DE VENTAS", font_size='16sp', bold=True, size_hint_y=None, height=dp(55))
        btn_ventas.bind(on_release=lambda x: self.ir_a_pantalla('ventas'))
        layout.add_widget(btn_ventas)

        # 3. CONTROL DE STOCK
        btn_stock = Button(text="📦 CONTROL DE STOCK", font_size='16sp', bold=True, size_hint_y=None, height=dp(55))
        btn_stock.bind(on_release=lambda x: self.ir_a_pantalla('stock'))
        layout.add_widget(btn_stock)

        # 4. FACTURACIÓN
        btn_facturas = Button(text="🧾 FACTURACIÓN ELECTRÓNICA", font_size='16sp', bold=True, size_hint_y=None, height=dp(55))
        btn_facturas.bind(on_release=lambda x: self.ir_a_pantalla('facturas'))
        layout.add_widget(btn_facturas)

        layout.add_widget(Widget())

        # Botón Cerrar Sesión
        btn_logout = Button(text="CERRAR SESIÓN", font_size='14sp', bold=True, size_hint_y=None, height=dp(45), background_color=(0.8, 0.2, 0.2, 1))
        btn_logout.bind(on_release=self.cerrar_sesion)
        layout.add_widget(btn_logout)

        self.add_widget(layout)

    def abrir_escaner(self, instance):
        # Próximo paso: Conectar con la cámara nativa
        print("Abriendo cámara para escanear código de barras...")

    def ir_a_pantalla(self, nombre_pantalla):
        # Método genérico para movernos entre secciones más adelante
        print(f"Yendo a la sección: {nombre_pantalla}")

    def cerrar_sesion(self, instance):
        App.get_running_app().usuario_actual = None
        self.manager.current = 'login'


class OpticaItalianaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuario_actual = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(PantallaLogin(name='login'))
        sm.add_widget(PantallaMenuPrincipal(name='menu_principal'))
        return sm

if __name__ == '__main__':
    OpticaItalianaApp().run()
