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
        
        # Obtenemos la ruta interna del dispositivo para guardar la base de datos
        ruta_app = App.get_running_app().user_data_dir
        self.base_datos = os.path.join(ruta_app, "optica_italiana.db")
        self.crear_base_datos_inicial()

        # Layout principal centrado y estético
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))

        # Espaciador superior
        layout.add_widget(Widget(size_hint_y=None, height=dp(40)))

        # Título de la Óptica
        layout.add_widget(Label(text="ÓPTICA ITALIANA", font_size='28sp', bold=True, size_hint_y=None, height=dp(45)))
        layout.add_widget(Label(text="Gestión Móvil v6.0", font_size='16sp', color=(0.7, 0.7, 0.7, 1), size_hint_y=None, height=dp(20)))

        layout.add_widget(Widget(size_hint_y=None, height=dp(30)))

        # Campo: Usuario
        layout.add_widget(Label(text="USUARIO:", font_size='16sp', bold=True, anchor_x='left', size_hint_y=None, height=dp(25)))
        self.input_user = TextInput(multiline=False, font_size='18sp', size_hint_y=None, height=dp(45), write_tab=False)
        layout.add_widget(self.input_user)

        # Campo: Contraseña
        layout.add_widget(Label(text="CONTRASEÑA:", font_size='16sp', bold=True, anchor_x='left', size_hint_y=None, height=dp(25)))
        self.input_pass = TextInput(multiline=False, password=True, font_size='18sp', size_hint_y=None, height=dp(45), write_tab=False)
        layout.add_widget(self.input_pass)

        # Label para mostrar errores de login
        self.lbl_error = Label(text="", font_size='14sp', color=(1, 0.3, 0.3, 1), size_hint_y=None, height=dp(30))
        layout.add_widget(self.lbl_error)

        layout.add_widget(Widget())

        # Botón de Ingreso
        btn_entrar = Button(text="INICIAR SESIÓN", font_size='18sp', bold=True, size_hint_y=None, height=dp(50), background_color=(0.2, 0.6, 0.8, 1))
        btn_entrar.bind(on_release=self.validar_login)
        layout.add_widget(btn_entrar)

        self.add_widget(layout)

    def crear_base_datos_inicial(self):
        """ Inicializa la base de datos con las 5 tablas de tu código de PC """
        conn = sqlite3.connect(self.base_datos)
        cursor = conn.cursor()
        
        # 1. Tabla de Ventas (Fichas de clientes)
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, nombre TEXT, tel TEXT, 
            od_esf TEXT, od_cil TEXT, od_eje TEXT, oi_esf TEXT, oi_cil TEXT, oi_eje TEXT, 
            adicion TEXT, cristal TEXT, armazon TEXT, total REAL, sena REAL, saldo REAL, receta_path TEXT
        )''')
        
        # 2. Tabla de Stock (Artículos y Armazones)
        cursor.execute('''CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE, armazon TEXT, 
            precio REAL, costo REAL, cantidad INTEGER DEFAULT 0
        )''')
        
        # 3. Tabla de Usuarios
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT UNIQUE, password TEXT, nivel INTEGER
        )''')
        
        # 4. Tabla de Emisor (Datos de tu Óptica)
        cursor.execute('''CREATE TABLE IF NOT EXISTS emisor (
            id INTEGER PRIMARY KEY, nombre TEXT, domicilio TEXT, cond_iva TEXT, cuit TEXT, iibb TEXT, inicio_act TEXT
        )''')
        
        # 5. Tabla de Facturas Emitidas
        cursor.execute('''CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, tipo_cbte TEXT, punto_vta TEXT, nro_cbte TEXT, 
            fecha_emision TEXT, cliente_nom TEXT, cliente_cuit TEXT, cliente_iva TEXT, 
            subtotal REAL, iva_total REAL, total REAL, cae TEXT, vto_cae TEXT
        )''')

        # Insertar usuario administrador por defecto si la tabla está vacía
        cursor.execute("INSERT OR IGNORE INTO usuarios (user, password, nivel) VALUES (?, ?, ?)", ("admin", "1234", 1))
        
        # Insertar datos por defecto de la óptica si no existen
        cursor.execute("SELECT COUNT(*) FROM emisor")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''INSERT INTO emisor (id, nombre, domicilio, cond_iva, cuit, iibb, inicio_act) 
                           VALUES (1, 'ÓPTICA ITALIANA', '', 'Monotributista', '', '', '')''')

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
            # Guardamos globalmente quién inició sesión para aplicar los permisos después
            App.get_running_app().usuario_actual = {"nombre": resultado[0], "nivel": resultado[1]}
            
            # Avisamos que el login fue exitoso (Por ahora no cambia de pantalla porque la estamos diseñando)
            self.lbl_error.color = (0.3, 1, 0.3, 1)
            self.lbl_error.text = f"¡Bienvenido {resultado[0].upper()}! Conectando..."
            
            # Próximo paso: Redirigir al menú principal redirigiendo el manager
            # self.manager.current = 'menu_principal'
        else:
            self.lbl_error.color = (1, 0.3, 0.3, 1)
            self.lbl_error.text = "Usuario o contraseña incorrectos."


class OpticaItalianaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuario_actual = None # Acá guardaremos el rango (Admin/Vendedor)

    def build(self):
        sm = ScreenManager()
        sm.add_widget(PantallaLogin(name='login'))
        return sm

if __name__ == '__main__':
    OpticaItalianaApp().run()
