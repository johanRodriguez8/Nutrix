from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QHBoxLayout, QInputDialog, QMessageBox,
    QApplication, QTableWidget, QTableWidgetItem, QItemDelegate, QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QModelIndex
from conveyors.assign_part_window import AssignPartWindow
from PyQt5 import QtGui
import sqlite3
from PyQt5.QtWidgets import QApplication, QMessageBox
import copy
from db.database import ejecutar_y_respaldar, db_path, ejecutar
from utils.helpers import MultiRowBorderDelegate, FONT_SIZE, LEN_SIZE, getDateTime, getNewId
from db.part_tracking.part import Part 
from conveyors.reassign_window import ReassingWindow

class TablaConveyor(QWidget):
    def __init__(self, conveyor):
        self.conveyor = conveyor
        super().__init__()
        self.setWindowTitle(f"STATUS CONVEYOR {self.conveyor}")
        self.showMaximized()

        layout = QVBoxLayout()

        titulo = QLabel(f"STATUS CONVEYOR {self.conveyor}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 30px; font-weight: bold; color: #2596be;") #Og 30px
        layout.addWidget(titulo)

        self.tabla = QTableWidget()
        headers = [
            "HANGER NUMBER", "STATUS", "ENABLED","PART ID", "WORK ORDER", "PART NUMBER",
            "ASSIGN/UNASSIGN", "ENABLE/DISABLE", "REASSIGN"
        ]
        self.tabla.setColumnCount(len(headers))
        self.tabla.setHorizontalHeaderLabels(headers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla)

        self.setLayout(layout)
        self.cargar_datos()

    def cargar_datos(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            SELECT hanger_id, hanger_num, status, enable, part_id, part_num, order_id
            FROM conveyors
            WHERE conveyor=?
            ORDER BY hanger_num
        """, (self.conveyor, ))
        filas = c.fetchall()
        conn.close()

        self.tabla.setRowCount(len(filas))
        self.delegate = MultiRowBorderDelegate(self.tabla)
        self.tabla.setItemDelegate(self.delegate)
        for r, (hanger_id, numero_hanger, status, habilitado, part_id, part_num, order_id) in enumerate(filas):
            self.tabla.setRowHeight(r, FONT_SIZE*2+10)
            item_num = QTableWidgetItem(str(numero_hanger))

            display_status = status#"LOAD" if (no_parte and str(no_parte).strip()) else "EMPTY"
            item_status = QTableWidgetItem(display_status)
            item_enabled = QTableWidgetItem("YES" if habilitado else "NO")
            item_partId = QTableWidgetItem(str(part_id) or "")
            item_partNum = QTableWidgetItem(str(part_num) or "")
            item_order = QTableWidgetItem(str(order_id) or "")

            color = QtGui.QColor("#c8f7c5") if habilitado else QtGui.QColor("#f7c5c5")
            for it in (item_num, item_status, item_enabled, item_partId, item_partNum, item_order):
                it.setBackground(color)
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)
                it.setTextAlignment(Qt.AlignCenter)
                font = it.font()
                font.setPointSize(FONT_SIZE)
                it.setFont(font)

            self.tabla.setItem(r, 0, item_num)
            self.tabla.setItem(r, 1, item_status)
            self.tabla.setItem(r, 2, item_enabled)
            self.tabla.setItem(r, 3, item_partId)
            self.tabla.setItem(r, 4, item_order)
            self.tabla.setItem(r, 5, item_partNum)

            btn_assign = QPushButton("UNASSIGN" if part_id!=None else "ASSIGN")
            font = btn_assign.font()
            font.setPointSize(FONT_SIZE)
            btn_assign.setFont(font)
            btn_assign.setMinimumHeight(FONT_SIZE)
            btn_assign.setMinimumWidth(LEN_SIZE)
            btn_assign.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'#d9534f' if part_id!=None else '#5cb85c'};
                    color: white; font-weight: bold; padding: 6px; border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {'#c9302c' if part_id!=None else '#4cae4c'};
                }}
            """)
            btn_assign.clicked.connect(
                lambda _, h=numero_hanger, pn=(part_id), enable=(habilitado), hanger_id=hanger_id: self.assign_unassign(h, pn, enable, hanger_id),
            )
            cell_assign = QWidget()
            lay_a = QHBoxLayout(cell_assign)
            lay_a.setContentsMargins(16, 4, 16, 4)
            lay_a.setAlignment(Qt.AlignCenter)
            lay_a.addWidget(btn_assign)
            self.tabla.setCellWidget(r, 6, cell_assign)

            btn_toggle = QPushButton("DISABLE" if habilitado else "ENABLE")
            font = btn_toggle.font()
            font.setPointSize(FONT_SIZE)
            btn_toggle.setFont(font)
            btn_toggle.setMinimumWidth(LEN_SIZE)
            btn_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'#d9534f' if habilitado else '#5cb85c'};
                    color: white; font-weight: bold; padding: 6px; border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {'#c9302c' if habilitado else '#4cae4c'};
                }}
            """)
            btn_toggle.clicked.connect(
                lambda _, h=numero_hanger, cur=habilitado: self.toggle_enabled(h, cur)
            )
            cell_toggle = QWidget()
            lay_t = QHBoxLayout(cell_toggle)
            lay_t.setContentsMargins(16, 4, 16, 4)
            lay_t.setAlignment(Qt.AlignCenter)
            lay_t.addWidget(btn_toggle)
            self.tabla.setCellWidget(r, 7, cell_toggle)

            reassign_btn = QPushButton("REASSIGN")
            font = reassign_btn.font()
            font.setPointSize(FONT_SIZE)
            reassign_btn.setFont(font)
            reassign_btn.setMinimumWidth(LEN_SIZE)
            reassign_btn.setStyleSheet(f"""
                QPushBUtton {{
                    background-color:{'#d9534f' if habilitado else '#d9534f'};
                    color: white; font-weight: bold; padding: 6px; border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: {'#c9302c' if habilitado else '#4cae4c'};
                }}
            """)
            reassign_btn.clicked.connect( lambda _, enable=habilitado, hanger=numero_hanger, pid=part_id:self.reassign(enable, hanger, pid))
            cell_assign = QWidget()
            lay_a = QHBoxLayout(cell_assign)
            lay_a.setContentsMargins(16, 4, 16, 4)
            lay_a.setAlignment(Qt.AlignCenter)
            lay_a.addWidget(reassign_btn)
            self.tabla.setCellWidget(r, 8, cell_assign)
        #self.highlight("6", 2)
        #self.highlight("21", 3)
    def highlight(self, conveyorId, tipo):
        #1:R1, 2:R2, 3:Carga, 4:Descarga
        if tipo == 1:
            color = "red"
        elif tipo == 2:
            color = "blue"
        elif tipo == 3:
            color = "black"
        elif tipo == 4:
            color = "orange"
        rows = self.tabla.rowCount()
        for i in range(rows):
            idItem = self.tabla.item(i, 0)
            if idItem.text() == conveyorId:
                self.delegate.set_row_color(i, color)
                self.tabla.show()

    def assign_unassign(self, numero_hanger: int, part_actual: int, enable: int, hanger_id:int):
        if not enable:
            return 
        #UNASSIGN CASE
        if part_actual!=None:
            self.unassignPart(numero_hanger, part_actual)
            return
        #ASSIGN CASE
        self.assignPartToHanger(numero_hanger=numero_hanger)

    def assignPartToHanger(self, numero_hanger):
        partWind = AssignPartWindow(numero_hanger, self.conveyor)
        partWind.exec()
        self.cargar_datos()
    
    def unassignPart(self, numero_hanger, part_actual):
        resp = QMessageBox.question(
            self, "UNASSIGN PART NUMBER",
                f"¿Quitar el PART NUMBER '{part_actual}' del hanger {numero_hanger}?",
                QMessageBox.Yes | QMessageBox.No
            )
        if resp == QMessageBox.Yes:
            part = Part()
            #part.endPart()
            part.deletePart(part_actual, numero_hanger, self.conveyor)
            self.cargar_datos()
        
    def toggle_enabled(self, numero_hanger: int, enable: int):
        new_enable = 0 if enable else 1
        texto_accion = "DISABLE" if enable else "ENABLE"

        resp = QMessageBox.question(
            self, "CONFIRM ACTION",
            f"¿Deseas {texto_accion} el hanger {numero_hanger}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if resp == QMessageBox.Yes:
            ejecutar_y_respaldar(
                "UPDATE conveyors SET enable=? WHERE hanger_num=? AND conveyor=?",
                (new_enable, numero_hanger, self.conveyor)
            )
            self.cargar_datos()

    def reassign(self, enable, hanger_num, part_id):
        if not enable:
            QMessageBox.warning(self, "HANGER ENABLE", "HANGER BLOCKED, FOR ANY CHANGES TOGGLE THE ENABLE BUTTON.")
            return

        if not part_id:
            QMessageBox.warning(self, "HANGER EMPTY", "THE HANGER IS EMPTY, TO REASSIGN THE HANGER MUST BE FULL.")
            return
        reassignWindow = ReassingWindow(hanger_num, self.conveyor, part_id)
        reassignWindow.exec()
        
class SubventanaConveyor(QWidget):
    def __init__(self, conveyor):
        super().__init__()
        self.conveyor = conveyor
        self.showMaximized()

        layout = QVBoxLayout()

        label = QLabel(f"WELCOME TO CONVEYOR {self.conveyor}")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: #2596be;")
        layout.addWidget(label)

        boton = QPushButton(f"STATUS CONVEYOR {self.conveyor}")
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

        self.win = TablaConveyor(self.conveyor)
        app.setProperty('ventana_secundaria', self.win)
        self.win.destroyed.connect(lambda: app.setProperty('ventana_secundaria', None))
        self.win.show()