from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QMessageBox, QFileDialog, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import os
import sqlite3
from db.part_tracking.robot_coordinator import RobotCoordinator
from PyQt5.QtWidgets import QApplication, QMessageBox
from utils.helpers import FONT_SIZE, LEN_SIZE
from db.database import ejecutar_y_respaldar, db_path 
from db.part_tracking.part  import Part
from db.part_tracking.program  import Program
import copy
COMPARTIDA_INICIAL = "/home/numtek/Desktop/COMPARTIDA"  
HANG_COL = 0
CONV_COL = 1
STATUS_COL = 2
EN_COL = 3
ID_COL = 4
ORDER_COL = 5
NUM_COL = 6
ASSIGN_COL = 7
ENABLE_COL = 8
class Robot2Window(QWidget):
    def __init__(self, coordinator:RobotCoordinator):
        super().__init__()
        self.coordinator = coordinator
        self.setWindowTitle("ROBOT 2 STATUS")
        self.showMaximized()

        layout = QVBoxLayout()

        titulo = QLabel("ROBOT 2 STATUS")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 30px; font-weight: bold; color: #2596be;") #Og 30px
        layout.addWidget(titulo)

        self.tabla = QTableWidget()
        header = [
            "HANGER NUMBER", "CONVEYOR", "STATUS", "PART ID", "WORK ORDER", "PART NUMBER",
            "ASSIGN/UNASSIGN", "ENABLE/DISABLE", "REASSIGN"
        ]
        self.tabla.setColumnCount(len(header))
        self.tabla.setHorizontalHeaderLabels(header)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        self.cargar_datos()
        layout.addWidget(self.tabla)
        self.setLayout(layout)
        

    def cargar_datos(self):
        currentPart = self.coordinator.currentPart
        if not currentPart or not currentPart.part_id:
            print("NO CURRENT PART")
            emptyProgram = Program()
            emptyProgram.current_hanger = None
            emptyProgram.current_conveyor = "A"
            emptyProgram.hanger_num = None
            emptyProgram.conveyor_start = "A"
            currentPart = Part()
            currentPart.current_step = 0
            currentPart.programs = [emptyProgram]
            
        print(f"CURRENT PART: {currentPart.part_id}")
        print(f"part_num PART: {currentPart.part_num}")
        print(f"status PART: {currentPart.status}")
        filas = [["-", "-", True, True]]

        self.tabla.setRowCount(1)
        self.tabla.setRowHeight(0, FONT_SIZE*2+10)
        #"ASSIGN/UNASSIGN", "ENABLE/DISABLE"
        #self.tabla.resizeRowsToContents()
        program = currentPart.getCurrentProgram()
        item_hang = QTableWidgetItem(program.current_hanger if type(program.current_hanger) is str else str(program.current_hanger))
        item_conv = QTableWidgetItem(program.current_conveyor if type(program.current_conveyor) is str else str(program.current_conveyor))
        item_status = QTableWidgetItem(currentPart.status if type(currentPart.status) is str else str(currentPart.status))
        item_id = QTableWidgetItem(currentPart.part_id if type(currentPart.part_id) is str else str(currentPart.part_id))
        item_order = QTableWidgetItem(program.order_id if type(program.order_id) is str else str(program.order_id))
        item_num = QTableWidgetItem(currentPart.part_num if type(currentPart.part_num) is str else str(currentPart.part_num))
        

        color = QtGui.QColor("#c8f7c5") if currentPart.status else QtGui.QColor("#f7c5c5")
        for it in (item_hang, item_conv, item_status, item_id, item_order, item_num):
            it.setBackground(color)
            it.setFlags(it.flags() & ~Qt.ItemIsEditable)
            it.setTextAlignment(Qt.AlignCenter)
            font = it.font()
            font.setPointSize(FONT_SIZE)
            it.setFont(font)

        self.tabla.setItem(0, 0, item_hang)
        self.tabla.setItem(0, 1, item_conv)
        self.tabla.setItem(0, 2, item_status)
        self.tabla.setItem(0, 3, item_id)
        self.tabla.setItem(0, 4, item_order)
        self.tabla.setItem(0, 5, item_num)

        btn_assign = QPushButton("UNASSIGN" if currentPart.part_num!=None else "ASSIGN")
        font = btn_assign.font()
        font.setPointSize(FONT_SIZE)
        btn_assign.setFont(font)
        btn_assign.setMinimumHeight(FONT_SIZE)
        btn_assign.setMinimumWidth(LEN_SIZE)


        btn_assign.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#d9534f' if currentPart.part_num!=None else '#5cb85c'};
                color: white; font-weight: bold; padding: 6px; border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {'#c9302c' if currentPart.part_num!=None else '#4cae4c'};
            }}
        """)
        #btn_assign.clicked.connect(
        #    lambda _, h=numero_hanger, pn=(part_num), enable=(habilitado), hanger_id=hanger_id: self.assign_unassign(h, pn, enable, hanger_id),
        #)
        cell_assign = QWidget()
        lay_a = QHBoxLayout(cell_assign)
        lay_a.setContentsMargins(16, 4, 16, 4)
        lay_a.setAlignment(Qt.AlignCenter)
        lay_a.addWidget(btn_assign)
        self.tabla.setCellWidget(0, 6, cell_assign)

        btn_toggle = QPushButton("DISABLE" if currentPart.status else "ENABLE")
        font = btn_toggle.font()
        font.setPointSize(FONT_SIZE)
        btn_toggle.setFont(font)
        btn_toggle.setMinimumWidth(LEN_SIZE)
        btn_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#d9534f' if currentPart.status else '#5cb85c'};
                color: white; font-weight: bold; padding: 6px; border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {'#c9302c' if currentPart.status else '#4cae4c'};
            }}
        """)
        #btn_toggle.clicked.connect(
        #    lambda _, h=numero_hanger, cur=habilitado: self.toggle_enabled(h, cur)
        #)
        cell_toggle = QWidget()
        lay_t = QHBoxLayout(cell_toggle)
        lay_t.setContentsMargins(16, 4, 16, 4)
        lay_t.setAlignment(Qt.AlignCenter)
        lay_t.addWidget(btn_toggle)
        self.tabla.setCellWidget(0, 7, cell_toggle)


        reassingBtn = QPushButton("REASSIGN")
        font = reassingBtn.font()
        font.setPointSize(FONT_SIZE)
        reassingBtn.setFont(font)
        reassingBtn.setMinimumWidth(LEN_SIZE)
        reassingBtn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#d9534f' if currentPart.status else '#5cb85c'};
                color: white; font-weight: bold; padding: 6px; border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {'#c9302c' if currentPart.status else '#4cae4c'};
            }}
        """)
        cell_toggle = QWidget()
        lay_t = QHBoxLayout(cell_toggle)
        lay_t.setContentsMargins(16, 4, 16, 4)
        lay_t.setAlignment(Qt.AlignCenter)
        lay_t.addWidget(reassingBtn)
        self.tabla.setCellWidget(0, 8, cell_toggle)


    def assign_unassign(self, numero_hanger: int, part_actual: int, enable: int, hanger_id:int):
        if not enable:
            return 
        #UNASSIGN CASE
        if part_actual!=None:
            resp = QMessageBox.question(
                self, "UNASSIGN PART NUMBER",
                f"¿Quitar el PART NUMBER '{part_actual}' del hanger {numero_hanger}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.Yes:
                ejecutar_y_respaldar(
                    "UPDATE conveyors SET part_id=NULL WHERE hanger_num=? AND conveyor='A'",
                    (numero_hanger,)
                )
                ejecutar_y_respaldar(
                    "UPDATE parts SET hanger_id=NULL, hanger_num=NULL, conveyor=NULL, status='EMPTY' WHERE part_id=?",
                    (part_actual,)
                )
                self.cargar_datos()
            return
        #ASSIGN CASE
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT part_id
            FROM parts
            WHERE hanger_id IS NULL
            ORDER BY part_id
        """)
        rows = cur.fetchall()
        conn.close()

        opciones = [str(r[0]) for r in rows]
        if not opciones:
            QMessageBox.information(
                self, "Sin Part Numbers",
                "No hay PART NUMBERS habilitados con programa asignado.\n"
                "Primero asigna un .ngc en la sección de Part Numbers."
            )
            return

        seleccionado, ok = QInputDialog.getItem(
            self, str("ASSIGN PART NUMBER"),
            str(f"Selecciona PART NUMBER para el hanger {numero_hanger}:"),
            opciones, 0, False)
        if ok and seleccionado:
            ejecutar_y_respaldar(
                "UPDATE conveyors SET part_id=?, status='FULL' WHERE hanger_num=? AND conveyor='A'",
                (seleccionado, numero_hanger)
            )
            ejecutar_y_respaldar(
                """UPDATE parts SET hanger_num=?, hanger_id=?, conveyor='A' WHERE part_id=?""",
                (numero_hanger, hanger_id, seleccionado)
            )
            self.cargar_datos()


    def toggle_enabled(self, numero_hanger: int, habilitado_actual: int):
        nuevo_estado = 0 if habilitado_actual else 1
        texto_accion = "DISABLE" if habilitado_actual else "ENABLE"

        resp = QMessageBox.question(
            self, "CONFIRM ACTION",
            f"¿Deseas {texto_accion} el hanger {numero_hanger}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if resp == QMessageBox.Yes:
            ejecutar_y_respaldar(
                "UPDATE conveyors SET enable=? WHERE hanger_num=? AND conveyor='A'",
                (nuevo_estado, numero_hanger)
            )
            self.cargar_datos()

class SubRobot2Window(QWidget):
    def __init__(self, coordinator:RobotCoordinator):
        super().__init__()
        layout = QVBoxLayout()
        self.coordinator = coordinator
        label = QLabel("WELCOME TO ROBOT 2 STATUS")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: #2596be;")
        layout.addWidget(label)
        boton = QPushButton("ROBOT 2 STATUS")
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
        layout.addWidget(boton)
        boton.clicked.connect(self.abrir_status)

        layout.addStretch()
        self.setLayout(layout)

    def abrir_status(self):
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

        self.win = Robot2Window(self.coordinator)
        app.setProperty('ventana_secundaria', self.win)

        self.win.destroyed.connect(lambda: app.setProperty('ventana_secundaria', None))
        self.win.show()