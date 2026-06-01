import os
import subprocess
import ctypes
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from ventana_principal.principal import VentanaPrincipal
from config import settings

VENTANA_LOGIN_ANCHO = 600
VENTANA_LOGIN_ALTO = 400
COLOR_FONDO = "#f0f0f0"
COLOR_BOTON = "#2596be"
COLOR_TEXTO_BOTON = "white"
FONT_LABEL = 20
FONT_INPUT = 20
FONT_BUTTON = 20
FONT_CHECKBOX = 20
INTERVALO_CAPSLOCK = 100

USUARIO_ADMIN = "admin"
CONTRASENA_ADMIN = settings.admin_password

USUARIO_SIMPLE = "user"
CONTRASENA_USUARIO_SIMPLE = "user"


ERROR = "ERROR"
TEXT_USUARIO = "USER:"
TEXT_CONTRASEÑA = "PASSWORD:"
TEXT_INGRESAR = "LOG IN"
TEXT_MOSTRAR = "SHOW PASSWORD"
TEXT_CAPS = "⚠️ BLOQ MAYÚS ACTIVATED"
TEXT_ERROR_LOGIN = "WRONG USER OR PASSWORD."

ruta_recursos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
logo_path = os.path.join(ruta_recursos, "logo.png")

class VentanaLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("START SESION")
        #self.setWindowIcon(QIcon(QPixmap(logo_path)))
        #self.setWindowIcon(QIcon(logo_path))
        self.setFixedSize(VENTANA_LOGIN_ANCHO, VENTANA_LOGIN_ALTO)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        widget = QWidget()
        layout = QVBoxLayout()

        self.label_usuario = QLabel(TEXT_USUARIO)
        self.input_usuario = QLineEdit()
        self.input_usuario.returnPressed.connect(self.validar_credenciales)

        self.label_contraseña = QLabel(TEXT_CONTRASEÑA)
        self.input_contraseña = QLineEdit()
        self.input_contraseña.setEchoMode(QLineEdit.Password)
        self.input_contraseña.returnPressed.connect(self.validar_credenciales)

        self.label_caps = QLabel(TEXT_CAPS)
        self.label_caps.setStyleSheet("color: red;")
        self.label_caps.setVisible(False)

        self.checkbox_mostrar = QCheckBox(TEXT_MOSTRAR)
        self.checkbox_mostrar.stateChanged.connect(self.toggle_password_visibility)

        self.boton_ingresar = QPushButton(TEXT_INGRESAR)
        self.boton_ingresar.clicked.connect(self.validar_credenciales)

        layout.addWidget(self.label_usuario)
        layout.addWidget(self.input_usuario)
        layout.addWidget(self.label_contraseña)
        layout.addWidget(self.input_contraseña)
        layout.addWidget(self.label_caps)
        layout.addWidget(self.checkbox_mostrar)
        layout.addWidget(self.boton_ingresar)
        layout.setAlignment(Qt.AlignCenter)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {COLOR_FONDO}; }}
            QLabel {{ font-size: {FONT_LABEL}px; font-weight: bold; }}
            QLineEdit {{ font-size: {FONT_INPUT}px; padding: 10px; background-color: white; border: 2px solid gray; }}
            QPushButton {{ font-size: {FONT_BUTTON}px; padding: 10px; background-color: {COLOR_BOTON}; color: {COLOR_TEXTO_BOTON}; border-radius: 10px; }}
            QCheckBox {{ font-size: {FONT_CHECKBOX}px; }}
        """)

        self.timer_capslock = QTimer()
        self.timer_capslock.timeout.connect(self.verificar_capslock)
        self.timer_capslock.start(INTERVALO_CAPSLOCK)
        self.verificar_capslock()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.enfocar_input_usuario)

    def enfocar_input_usuario(self):
        self.input_usuario.setFocus()
        self.input_usuario.selectAll()

    def toggle_password_visibility(self, state):
        self.input_contraseña.setEchoMode(QLineEdit.Normal if state == Qt.Checked else QLineEdit.Password)

    def verificar_capslock(self):
        try:
            output = subprocess.check_output(['xset', 'q']).decode()
            caps_on = "Caps Lock:   on" in output
            self.label_caps.setVisible(caps_on)
        except Exception as e:
            print(f"Error to verification of Caps Lock: {e}")
            self.label_caps.setVisible(False)

    def validar_credenciales(self):
        rol: str = ''
        if self.input_usuario.text() == USUARIO_ADMIN and self.input_contraseña.text() == CONTRASENA_ADMIN:
            rol= 'admin'
            print(rol)
        elif self.input_usuario.text() == USUARIO_SIMPLE and self.input_contraseña.text() == CONTRASENA_USUARIO_SIMPLE:
            rol= 'user'

        if rol!='':
            self.abrir_ventana_principal(rol)
        else:
            QMessageBox.warning(self, ERROR, TEXT_ERROR_LOGIN)

    def abrir_ventana_principal(self,rol:str):
        self.ventana_principal = VentanaPrincipal(rol)
        self.ventana_principal.show()
        self.close()


    