from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QMessageBox, QFileDialog, QInputDialog, QDialog,
    QComboBox, QLineEdit, QDialogButtonBox, QPushButton, QGridLayout
)
from PyQt5.QtCore import (Qt, QEvent)
from PyQt5 import QtGui
import os
import sqlite3
from PyQt5.QtWidgets import QApplication, QMessageBox

from utils.popups import defaultErrorToast

from pyqttoast import Toast, ToastPreset, ToastPosition
from db.database import ejecutar_y_respaldar, ejecutar, db_path

from utils.helpers import FONT_SIZE, LEN_SIZE
COMPARTIDA_INICIAL = "/home/numtek/Desktop/COMPARTIDA"  

class TablaPartNumbers(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STATUS PART NUMBER")
        self.showMaximized()

        layout = QVBoxLayout()

        titulo = QLabel("STATUS PART NUMBER")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 30px; font-weight: bold; color: #2596be;")
        layout.addWidget(titulo)

        boton_add = QPushButton("ADD PART NUMBER")
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
        boton_add.clicked.connect(self.addPart)
        layout.addWidget(boton_add)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels([
            "PART NUMBER", "PROGRAM SEQUENCE", "EDIT", "DELETE"
        ])

        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla)

        self.setLayout(layout)
        self.cargar_datos()


    def cargar_datos(self):
        #Base de datos
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT part_num, sequence_id FROM partNumbers ORDER BY part_num;")
        filas = cur.fetchall()
        conn.close()
        self.tabla.setRowCount(len(filas))

        for r, (partNum, seqId) in enumerate(filas):
            self.tabla.setRowHeight(r, FONT_SIZE*2+10)
            item_part = QTableWidgetItem(str(partNum))
            seqIdItem = QTableWidgetItem(str(seqId))
            color = "#c8f7c5" 
            for it in (item_part, seqIdItem):
                it.setBackground(QtGui.QColor(color))
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)
                it.setTextAlignment(Qt.AlignCenter)
                font = it.font()
                font.setPointSize(FONT_SIZE)
                it.setFont(font)
            self.tabla.setItem(r, 0, item_part)
            self.tabla.setItem(r, 1, seqIdItem)
            #Edit button
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
            btn_edit.clicked.connect(lambda _, id=partNum: self.editPart(str(id)))
            cell_edit = QWidget()
            lay_d = QHBoxLayout(cell_edit)
            lay_d.setContentsMargins(16, 4, 16, 4)
            lay_d.setAlignment(Qt.AlignCenter)
            btn_edit.setMinimumWidth(LEN_SIZE)
            lay_d.addWidget(btn_edit)
            self.tabla.setCellWidget(r, 2, cell_edit)
            btn_delete = QPushButton("DELETE")
            font.setPointSize(FONT_SIZE)
            btn_delete.setFont(font)
            btn_delete.setMinimumWidth(120)
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #d9534f;
                    color: white; font-weight: bold; padding: 6px; border-radius: 6px;
                }
                QPushButton:hover { background-color: #c9302c; }
            """)
            btn_delete.clicked.connect(lambda _, _id=partNum: self.deletePart(_id))

            cell_delete = QWidget()
            lay_d = QHBoxLayout(cell_delete)
            lay_d.setContentsMargins(16, 4, 16, 4)
            lay_d.setAlignment(Qt.AlignCenter)
            btn_delete.setMinimumWidth(LEN_SIZE)
            lay_d.addWidget(btn_delete)
            self.tabla.setCellWidget(r, 3, cell_delete)

    def deletePart(self, row_id: int):
        resp = QMessageBox.question(self, "DELETE PART NUMBER",
                                    f"¿Eliminar '{row_id}'? Esta acción no se puede deshacer.",
                                    QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            ejecutar_y_respaldar("DELETE FROM partNumbers WHERE part_num=?", (row_id,))
            self.cargar_datos()
    def addPart(self):
        windowPart = addPartWindow()
        windowPart.exec()
        self.cargar_datos()
    def editPart(self, newId):
        windowPart = addPartWindow(newId)
        windowPart.exec()
        self.cargar_datos()


class addPartWindow(QDialog):
    def __init__(self, newPartId=-1):
        super().__init__()
        self.setWindowTitle("EDIT")
        self.layout = QGridLayout()
        self.partId = ScanLineEdit()
        self.partId.returnPressed.connect(self.on_scan)
        if newPartId != -1:
            self.partId.setText(newPartId)

        self.originalPartId = newPartId
        self.sequenceId = QComboBox()
        self.sequenceId.setAccessibleName("Sequence")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT sequence_id FROM sequences ORDER BY sequence_id;")
        sequences = cur.fetchall()
        conn.close()
        for seq in sequences:
            self.sequenceId.addItem(seq[0])
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("CANCEL")
        if newPartId != -1:
            self.okButton.clicked.connect(self.editPart)
        else:
            self.okButton.clicked.connect(self.addPartToTable)
        self.cancelButton.clicked.connect(self.close)

        self.okButton.setAutoDefault(False)
        self.okButton.setDefault(False)

        self.cancelButton.setAutoDefault(False)
        self.cancelButton.setDefault(False)

        self.layout.addWidget(QLabel("ADD PART"), 1, 1)
        self.layout.addWidget(self.partId, 2, 1)
        self.layout.addWidget(QLabel("SEQUENCE"), 1, 2)
        self.layout.addWidget(self.sequenceId, 2, 2)
        self.layout.addWidget(self.cancelButton, 3, 1)
        self.layout.addWidget(self.okButton, 3, 2)
        self.setLayout(self.layout)
    def addPartToTable(self):
        sequence = self.sequenceId.currentText()
        part = self.partId.text()
        if self.validation(part):
            ejecutar("""
                INSERT INTO partNumbers (part_num, sequence_id) VALUES (?, ?) 
            """, (part, sequence))
            self.accept()
    def editPart(self):
        sequence = self.sequenceId.currentText()
        newPart = self.partId.text()

        # validar duplicados
        if newPart != self.originalPartId:
            if not self.validation(newPart):
                return

        ejecutar("""
            UPDATE partNumbers 
            SET part_num=?, sequence_id=? 
            WHERE part_num=? 
        """, (newPart, sequence, self.originalPartId))

        self.accept()

    def validation(self, part):
        # if not part.isnumeric():
        #     QMessageBox.warning(self, "ERROR", "PART ID HAS TO BE A NUMBER")
        #     return False
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT part_num FROM partNumbers;")
        parts = cur.fetchall()
        conn.close()
        for parte in parts:
            if part == parte[0]:
                QMessageBox.warning(self, "ERROR", "PART ID ALREADY EXIST, TRY EDIT BUTTON")
                return False
        return True

    def on_scan(self):
        scanned_value = self.partId.text().strip()
        if scanned_value.startswith(("SO", "SP", "EX", "PW")):

            
            defaultErrorToast(self)
            self.partId.clear()
            self.partId.setFocus()
            return
        else:
            self.okButton.click()

    

class SubventanaNumerodeParte(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        label = QLabel("WELCOME TO PART NUMBER PAGE")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: #2596be;")
        layout.addWidget(label)

        botones_texto = [
            "STATUS PART NUMBER"
        ]

        for texto in botones_texto:
            boton = QPushButton(texto)
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

            if texto == "STATUS PART NUMBER":
                boton.clicked.connect(self.abrir_status_part_number)
            elif texto == "ASSIGN/UNASSIGN PART NUMBER":
                boton.clicked.connect(self.abrir_status_part_number)  
            elif texto == "ENABLED/DISABLE PART NUMBER":
                boton.clicked.connect(self.abrir_status_part_number)  
            elif texto == "ADD PART NUMBER":
                boton.clicked.connect(self.abrir_status_part_number)  
            elif texto == "DELETE PART NUMBER":
                boton.clicked.connect(self.abrir_status_part_number)  

        layout.addStretch()
        self.setLayout(layout)

    def abrir_status_part_number(self):
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

        self.win = TablaPartNumbers()
        app.setProperty('ventana_secundaria', self.win)

        self.win.destroyed.connect(lambda: app.setProperty('ventana_secundaria', None))
        self.win.show()

class ScanLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # NO hacer submit
            self.returnPressed.emit()
            return
        super().keyPressEvent(event)