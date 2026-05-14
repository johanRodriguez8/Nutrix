from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

def mostrar_splash(splash_path, tiempo, callback):
    splash = QSplashScreen(QPixmap(splash_path).scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    splash.show()
    QTimer.singleShot(tiempo, lambda: (splash.close(), callback()))
