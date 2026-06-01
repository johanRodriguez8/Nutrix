from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QMessageBox, QFileDialog, QInputDialog, QDialog,
    QComboBox, QLineEdit, QDialogButtonBox, QPushButton, QGridLayout,QTextEdit, QScrollArea
)
from PyQt5.QtCore import (Qt, QEvent)
from PyQt5 import QtGui
import os
from PyQt5.QtWidgets import QApplication, QMessageBox

from utils.popups import defaultErrorToast

from pyqttoast import Toast, ToastPreset, ToastPosition
from db.repositories import part_numbers_repo, sequences_repo

from utils.helpers import FONT_SIZE, LEN_SIZE

class TablaPartNumbers(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STATUS PART NUMBER")
        self.showMaximized()
        self.sort_asc = True  # <-- estado del orden

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
        self.update_headers()  # <-- encabezados con flecha
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.horizontalHeader().sectionClicked.connect(self.on_header_clicked)  # <-- click en header

        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.horizontalHeader().setHighlightSections(False)
        
        layout.addWidget(self.tabla)

        self.setLayout(layout)
        self.cargar_datos()

        boton_bulk = QPushButton("BULK IMPORT")
        boton_bulk.clicked.connect(self.bulkImport)

        boton_format = QPushButton("FORMAT PART NUMBERS")
        boton_format.clicked.connect(self.formatPartNumbers)

    def update_headers(self):
        arrow = "▲" if self.sort_asc else "▼"
        self.tabla.setHorizontalHeaderLabels([
            "PART NUMBER",
            f"PROGRAM SEQUENCE {arrow}",  # <-- flecha en la columna 1
            "EDIT",
            "DELETE"
        ])

    def on_header_clicked(self, column):
        if column == 1:  # solo columna PROGRAM SEQUENCE
            self.sort_asc = not self.sort_asc
            self.update_headers()
            self.cargar_datos()

    def toggle_sort(self):
        self.sort_asc = not self.sort_asc
        self.boton_sort.setText("▲ ASC" if self.sort_asc else "▼ DESC")
        self.cargar_datos()

    def formatPartNumbers(self):
        filas = part_numbers_repo.list_all()

        to_update = []
        for part, seq in filas:
            clean_part = part.replace('"', '').replace("'", '').replace(',', '')
            clean_seq  = seq.replace('"', '').replace("'", '').replace(',', '')
            if clean_part != part or clean_seq != seq:
                to_update.append((clean_part, clean_seq, part))

        if not to_update:
            QMessageBox.information(self, "FORMAT", "No records need formatting.")
            return

        resp = QMessageBox.question(
            self, "FORMAT PART NUMBERS",
            f"{len(to_update)} records will be cleaned:\n"
            + "\n".join(f"{original} → {new}" for new, _, original in to_update[:10])
            + ("\n..." if len(to_update) > 10 else ""),
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            for clean_part, clean_seq, original in to_update:
                part_numbers_repo.update(clean_part, clean_seq, original)
            self.cargar_datos()
            QMessageBox.information(self, "SUCCESS", f"✅ {len(to_update)} records cleaned.")

    def bulkImport(self):
        win = BulkImportWindow()
        win.exec()
        self.cargar_datos()

    def cargar_datos(self):

        self.tabla.hide()
        filas = part_numbers_repo.list_all_ordered(ascending=self.sort_asc)

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

        self.tabla.show() 

    def deletePart(self, row_id: int):
        resp = QMessageBox.question(self, "DELETE PART NUMBER",
                                    f"¿Eliminar '{row_id}'? Esta acción no se puede deshacer.",
                                    QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            part_numbers_repo.delete(row_id)
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
        sequences = sequences_repo.distinct_ids()
        for seq in sequences:
            self.sequenceId.addItem(seq[0])
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("CANCEL")
        if newPartId != -1:
            self.okButton.clicked.connect(self.editPart)
        else:
            self.okButton.clicked.connect(self.add_part_to_table)
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

    def add_part_to_table(self):
        sequence = self.sequenceId.currentText()
        part = self.partId.text()
        if self.validation(part):
            part_numbers_repo.insert(part, sequence)
            self.accept()
    def editPart(self):
        sequence = self.sequenceId.currentText()
        newPart = self.partId.text()

        # validar duplicados
        if newPart != self.originalPartId:
            if not self.validation(newPart):
                return

        part_numbers_repo.update(newPart, sequence, self.originalPartId)

        self.accept()

    def validation(self, part):
        # if not part.isnumeric():
        #     QMessageBox.warning(self, "ERROR", "PART ID HAS TO BE A NUMBER")
        #     return False
        parts = part_numbers_repo.all_part_nums()
        for parte in parts:
            if part == parte[0]:
                QMessageBox.warning(self, "ERROR", "PART ID ALREADY EXIST, TRY EDIT BUTTON")
                return False
        return True

    def on_scan(self):
        scanned_value = self.partId.text().strip()
        if scanned_value.startswith(("SO", "SP", "EX", "PW")):

            
            defaultErrorToast(self,"INVALID FORMAT")
            self.partId.clear()
            self.partId.setFocus()
            return
        else:
            self.okButton.click()
            print('escaneado jeje')

    

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


class BulkImportWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BULK IMPORT")
        self.setMinimumSize(700, 500)
        layout = QGridLayout()

        layout.addWidget(QLabel("PASTE DATA (format: (\"PART\", \"SEQ\"), ...):"), 0, 0)

        self.dataEdit = QTextEdit()
        self.dataEdit.setPlaceholderText(
            'Paste your data here, e.g.:\n'
            '("PART-001", "012"),\n'
            '("PART-002", "002"),\n'
        )
        layout.addWidget(self.dataEdit, 1, 0)

        self.previewLabel = QLabel("")
        self.previewLabel.setWordWrap(True)
        layout.addWidget(self.previewLabel, 2, 0)

        previewBtn = QPushButton("PREVIEW")
        previewBtn.clicked.connect(self.preview)
        importBtn = QPushButton("IMPORT")
        importBtn.clicked.connect(self.importData)
        cancelBtn = QPushButton("CANCEL")
        cancelBtn.clicked.connect(self.close)

        layout.addWidget(cancelBtn, 3, 0)
        layout.addWidget(previewBtn, 3, 1)
        layout.addWidget(importBtn, 3, 2)
        self.setLayout(layout)

    def getPairs(self):
        import re
        text = self.dataEdit.toPlainText()
        # Match ("PART", "SEQ") ignoring surrounding brackets, commas, whitespace
        pattern = r'\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)'
        matches = re.findall(pattern, text)
        parts = [m[0] for m in matches]
        seqs  = [m[1] for m in matches]
        return parts, seqs

    def preview(self):
        parts, seqs = self.getPairs()
        if not parts:
            self.previewLabel.setText("⚠️ No valid pairs found. Check the format.")
            return
        preview_text = "\n".join(f"{p}  →  {s}" for p, s in zip(parts, seqs))
        self.previewLabel.setText(f"✅ {len(parts)} pairs ready:\n{preview_text}")

    def importData(self):
        parts, seqs = self.getPairs()
        if not parts:
            QMessageBox.warning(self, "ERROR", "No valid pairs found. Check the format.")
            return

        existing = {row[0] for row in part_numbers_repo.all_part_nums()}

        duplicates = [p for p in parts if p in existing]
        new_pairs  = [(p, s) for p, s in zip(parts, seqs) if p not in existing]

        if duplicates:
            resp = QMessageBox.question(
                self, "DUPLICATES FOUND",
                f"{len(duplicates)} already exist and will be skipped:\n"
                + "\n".join(duplicates[:10])
                + ("\n..." if len(duplicates) > 10 else "")
                + f"\n\nImport the remaining {len(new_pairs)}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp == QMessageBox.No:
                return

        for part, seq in new_pairs:
            part_numbers_repo.insert(part, seq)

        QMessageBox.information(self, "SUCCESS",
            f"✅ {len(new_pairs)} parts imported successfully.")
        self.accept()