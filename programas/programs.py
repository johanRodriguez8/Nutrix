from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QHBoxLayout, QInputDialog, QMessageBox, QDialog,QFileDialog,
    QDialogButtonBox, QComboBox, QGridLayout, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import sqlite3
from PyQt5.QtWidgets import QApplication, QMessageBox
from db.database import ejecutar_y_respaldar, db_path
from utils.helpers import FONT_SIZE, LEN_SIZE
import os
import paramiko

R1_IP = '10.170.83.210'
R2_IP = "10.170.83.211"
port = 22 # Default SSH port
username = 'numtek'
password = '123' # Or use key-based authentication for better security
ROBOT_USER = "numtek"
ROBOT_PASSWORD = "123"
ROBOT_PROGRAM_DIR = "/home/numtek/Desktop/COMPARTIDA"

COMPARTIDA_INICIAL = "/home/numtek/Desktop/COMPARTIDA"
class VentanaProgramas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PROGRAMS")
        self.showMaximized()
        self.sort_asc = True  # <-- estado del orden

        layout = QVBoxLayout()

        titulo = QLabel("PROGRAMS")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 30px; font-weight: bold; color: #2596be;")
        layout.addWidget(titulo)

        boton_add = QPushButton("ADD PROGRAM")
        boton_add.setStyleSheet("""
            QPushButton {
                background-color: #2596be;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #1f7fa0; }
        """)
        boton_add.clicked.connect(self.addProgram)
        layout.addWidget(boton_add)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.update_headers()  # <-- headers con flecha
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.horizontalHeader().setHighlightSections(False)  # <-- sin azul al hacer click
        self.tabla.horizontalHeader().sectionClicked.connect(self.on_header_clicked)  # <-- click en header
        layout.addWidget(self.tabla)

        self.setLayout(layout)
        self.cargar_datos()

    def update_headers(self):
        arrow = "▲" if self.sort_asc else "▼"
        self.tabla.setHorizontalHeaderLabels([
            f"PROGRAM {arrow}",  # <-- flecha en columna 0
            "ROBOT", "FROM CONVEYOR", "TO CONVEYOR", "PATH", "EDIT", "DELETE"
        ])

    def on_header_clicked(self, column):
        if column == 0:  # solo columna PROGRAM
            self.sort_asc = not self.sort_asc
            self.update_headers()
            self.cargar_datos()

    def cargar_datos(self):
        self.tabla.hide()  # <-- oculta mientras carga

        order = "ASC" if self.sort_asc else "DESC"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(f"""
            SELECT program_id, path, robot_num, conveyor_start, conveyor_end 
            FROM programs 
            ORDER BY program_id {order}
        """)
        filas = c.fetchall()
        conn.close()

        self.tabla.setRowCount(len(filas))

        for r, (program_id, program_path, robot, conveyor_start, conveyor_end) in enumerate(filas):
            self.tabla.setRowHeight(r, FONT_SIZE*2+10)
            id_item = QTableWidgetItem(str(program_id))
            path_item = QTableWidgetItem(str(program_path))
            robot_item = QTableWidgetItem(str(robot))
            start_item = QTableWidgetItem(str(conveyor_start))
            end_item = QTableWidgetItem(str(conveyor_end))
            for it in (id_item, path_item, robot_item, start_item, end_item):
                if it.text() not in (None, "", "None"):
                    it.setBackground(QtGui.QColor("#c8f7c5"))
                    it.setFlags(it.flags() & ~Qt.ItemIsEditable)
                    it.setTextAlignment(Qt.AlignCenter)
                    font = it.font()
                    font.setPointSize(FONT_SIZE)
                    it.setFont(font)
                else:
                    it.setText("")
            self.tabla.setItem(r, 0, id_item)
            self.tabla.setItem(r, 1, robot_item)
            self.tabla.setItem(r, 2, start_item)
            self.tabla.setItem(r, 3, end_item)
            self.tabla.setItem(r, 4, path_item)

            self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
            self.tabla.horizontalHeader().setHighlightSections(False)

            btn_edit = QPushButton("EDIT")
            font.setPointSize(FONT_SIZE)
            btn_edit.setFont(font)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white; font-weight: bold; padding: 6px; border-radius: 6px;
                }
                QPushButton:hover { background-color: #5a6268; }
            """)
            btn_edit.clicked.connect(lambda _, id=id_item.text(): self.editProgram(id))
            cell_edit = QWidget()
            lay_d = QHBoxLayout(cell_edit)
            lay_d.setContentsMargins(16, 4, 16, 4)
            lay_d.setAlignment(Qt.AlignCenter)
            btn_edit.setMinimumWidth(LEN_SIZE)
            lay_d.addWidget(btn_edit)
            self.tabla.setCellWidget(r, 5, cell_edit)

            btn_delete = QPushButton("DELETE")
            font.setPointSize(FONT_SIZE)
            btn_delete.setFont(font)
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #d9534f;
                    color: white; font-weight: bold; padding: 6px; border-radius: 6px;
                }
                QPushButton:hover { background-color: #c9302c; }
            """)
            btn_delete.clicked.connect(lambda _, id=id_item.text(): self.deleteProgram(id))
            cell_delete = QWidget()
            lay_d = QHBoxLayout(cell_delete)
            lay_d.setContentsMargins(16, 4, 16, 4)
            lay_d.setAlignment(Qt.AlignCenter)
            btn_delete.setMinimumWidth(LEN_SIZE)
            lay_d.addWidget(btn_delete)
            self.tabla.setCellWidget(r, 6, cell_delete)

        self.tabla.show()  

    def addProgram(self):
        pid = "000"
        program_path = "ADD PATH"
        robot = "1"
        dialogo = self.tableInputDialog(pid, program_path, robot)
        dialogo.exec()
        self.cargar_datos()

    def editProgram(self, program_id):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT program_id, path, robot_num FROM programs WHERE program_id=?", (program_id,))
        filas = c.fetchall()
        conn.close()
        dialogo = self.tableInputDialog(filas[0][0], filas[0][1], filas[0][2])
        dialogo.exec()
        self.cargar_datos()

    def deleteProgram(self, program_id):
        resp = QMessageBox.question(self, "DELETE PART NUMBER",
                                    f"ARE YOU SURE TO DELETE PROGRAM '{program_id}'? THIS ACTION CAN NOT BE UNDONE.",
                                    QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            ejecutar_y_respaldar(
                "DELETE FROM programs WHERE program_id=?", (program_id,)
            )
            self.cargar_datos()

    # tableInputDialog y SubVentanaProgramas sin cambios...

    class tableInputDialog(QDialog):
        def __init__(self, program_id, program_path, robot):
            super().__init__()
            self.layout = QGridLayout()
            self.setWindowTitle("Data Table")
            #self.setGeometry(100, 100, 500, 150) # (x, y, width, height)

            # Create the table widget
            self.tableWidget = QTableWidget()
            self.tableWidget.setRowCount(1)
            self.tableWidget.setColumnCount(3)
            
            labels = [
                "PROGRAM", "ROBOT", "PATH"
            ]
            i = 1
            for label in labels:
                self.layout.addWidget(QLabel(label), 1, i)
                i = i + 1
            self.programWidget = QLineEdit(str(program_id))
            self.layout.addWidget(self.programWidget, 2, 1)
            self.comboWidget = QComboBox()
            self.comboWidget.addItems(["1", "2"])
            self.comboWidget.currentTextChanged.connect(self.downloadFiles)
            self.comboWidget.setCurrentIndex(0) if robot=="1" else self.comboWidget.setCurrentIndex(1)
            self.layout.addWidget(self.comboWidget, 2, 2)
            #self.pathWidget = QPushButton(program_path)
            self.pathWidget = QComboBox()
            files = self.downloadFiles()
            if program_path != "ADD PATH":
                for r, (file) in enumerate(files):
                    if file == program_path:
                        self.pathWidget.setCurrentIndex(r)
            #self.pathWidget.clicked.connect(self.openFiles)
            self.layout.addWidget(self.pathWidget, 2, 3)        
            # Create a button box for standard OK/Cancel buttons
            self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.buttonBox.accepted.connect(lambda id=program_id: self.update(id))
            self.buttonBox.rejected.connect(self.close)

            # Set up the layout
            #self.layout.addWidget(self.tableWidget)
            self.layout.addWidget(self.buttonBox, 3, 2, 1, 2)
            self.setLayout(self.layout)
            #self.tableWidget.resizeColumnsToContents()

        def update(self, program_id):
            new_program_id = self.programWidget.text()
            robot_num = self.comboWidget.currentText()
            path = self.pathWidget.currentText()
            if len(self.programWidget.text()) != 3:
                QMessageBox.warning(self, "ERROR", "THE ID HAS TO BE 3 DIGITS")
                return
            # if not os.path.exists(self.pathWidget.text()):
            #     QMessageBox.warning(self, "ERROR", "THE PATH HAS TO BE A VALID DIRECORY")
            #     return
            try:
                if program_id == "000":
                    ejecutar_y_respaldar(
                    "INSERT INTO programs (program_id, path, robot_num) VALUES (?, ?, ?, ?, ?)",
                    (new_program_id, path, robot_num)
                    )
                else:
                    ejecutar_y_respaldar(
                        f"""UPDATE programs SET 
                            program_id = ?,
                            path = ?,
                            robot_num = ?
                            WHERE program_id=?""",
                            (new_program_id, path, robot_num, program_id)
                        )

                self.close()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo asignar el programa: {e}")
        def verification(self):
            #TODO VERIFICATION FOR REPEATED IDS
            program_id = self.programWidget.text()
            robot_num = self.comboWidget.currentText()
            path = self.pathWidget.text()
            # if len(self.programWidget.text()) != 3:
            #     QMessageBox.warning(self, "ERROR", "THE ID HAS TO BE 3 DIGITS")
            #     return
            if not os.path.exists(self.pathWidget.text()):
                QMessageBox.warning(self, "ERROR", "THE PATH HAS TO BE A VALID DIRECORY")
                return
            try:
                ejecutar_y_respaldar(
                    "INSERT INTO programs (program_id, path, robot_num) VALUES (?, ?, ?)",
                    (program_id, path, robot_num)
                    )
                self.close()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo asignar el programa: {e}")

        def openFiles(self):
            ruta, _ = QFileDialog.getOpenFileName(
                self,
                "Selecciona archivo .ngc",
                COMPARTIDA_INICIAL
                #"NGC files (*.ngc);;All files (*)"
            )
            file_path = QFileDialog.getOpenFileName(None, "Open Remote File", "/mnt/remote_data")
            print(file_path)
            self.pathWidget.setText(str(ruta))
            if not ruta:
                return
            return ruta
        def str2Time(self, tiempo: str):
            hora = tiempo[0] + tiempo[1]
            minuto = tiempo[3] + tiempo[4]
            hora = int(hora)
            minuto = int(minuto)
            return hora, minuto
        def verifyTimeFormat(self, tiempo:str):
            isTime = True
            if len(tiempo) != 5:
                isTime = False
            elif not tiempo[0:1].isdigit():
                isTime = False
            elif not tiempo[3:4].isdigit():
                isTime = False
            return isTime
        def downloadFiles(self):
            files = []
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                robot_num = self.comboWidget.currentText()
                if robot_num == "1":
                    currentIp = R1_IP
                else:
                    currentIp = R2_IP
                client.connect(currentIp, port, username, password)
                sftp_client = client.open_sftp()
                #print(f"Listing files in {COMPARTIDA_INICIAL}:")
                for entry in sftp_client.listdir(COMPARTIDA_INICIAL):
                    #print(entry)
                    if entry[1:4].isnumeric():
                        files.append(entry)
                sftp_client.close()
                client.close()
            except Exception as e:
                print(f"An error occurred: {e}")
                files.append("Unconnected")
            self.pathWidget.clear()
            files = sorted(files)
            self.pathWidget.setCurrentIndex(0)
            for file in files:
                self.pathWidget.addItem(file)
            return files





class SubVentanaProgramas(QWidget):
    def __init__(self):
        super().__init__()
        self.showMaximized()

        layout = QVBoxLayout()

        label = QLabel("WELCOME TO PROGRAMS")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: #2596be;")
        layout.addWidget(label)

        boton = QPushButton("ENTER TO PROGRAMS")
        boton.setStyleSheet("""
            QPushButton {
                background-color: #2596be;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #1f7fa0; }
        """)
        boton.clicked.connect(self.abrir_status_conveyor_a)
        layout.addWidget(boton)

        layout.addStretch()
        self.setLayout(layout)

    def abrir_status_conveyor_a(self):
        app = QApplication.instance()
        vent_act = app.property('ventana_secundaria')

        if vent_act is not None and vent_act.isVisible():
            QMessageBox.information(
                self,
                "Ventana ya abierta",
                "Debes cerrar la ventana abierta antes de abrir otra."
            )
            try:
                vent_act.raise_()
                vent_act.activateWindow()
            except Exception:
                pass
            return

        self.win = VentanaProgramas()
        app.setProperty('ventana_secundaria', self.win)
        self.win.destroyed.connect(lambda: app.setProperty('ventana_secundaria', None))
        self.win.show()

