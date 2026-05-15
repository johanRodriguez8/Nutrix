from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QHBoxLayout,
    QMessageBox,
    QInputDialog,
    QDialog,
    QComboBox,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QTabWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from utils.helpers import getDateTime, getNewId
from db.part_tracking.part import Part
from db.database import selectFromDB
from utils.popups import defaultErrorToast


class AssignPartWindow(QDialog):
    def __init__(self, numero_hanger, conveyor):
        super().__init__()
        self.hanger_num = numero_hanger
        self.conveyor = conveyor
        self.setWindowTitle("ADD PART")
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.selectPart = selectPartNumWindow(
            numero_hanger=numero_hanger, conveyor=conveyor, closeFunct=self.close
        )
        self.writePart = writePartNumWindow(
            numero_hanger=numero_hanger, conveyor=conveyor, closeFunct=self.close
        )
        self.tabs.addTab(self.writePart, "WRITE")
        self.tabs.addTab(self.selectPart, "SELECT")
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.writePart.orderLine.setFocus()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            event.ignore()
        else:
            super().keyPressEvent(event)


class selectPartNumWindow(QWidget):
    def __init__(self, numero_hanger, conveyor, closeFunct):
        super().__init__()
        self.layout = QGridLayout()
        self.closeFunc = closeFunct
        self.hanger_num = numero_hanger
        self.conveyor = conveyor
        rawPartNum = selectFromDB(
            """
            SELECT part_num
            FROM partNumbers
            ORDER BY part_num """
        )

        rawOrder = selectFromDB(
            "SELECT DISTINCT order_id FROM workOrders ORDER BY order_id"
        )

        if not rawPartNum:
            self.partNumLabel = QLabel("NO PART NUMBERS")
            self.layout.addWidget(self.partNumLabel, 2, 1)
        else:
            partNum = [str(r[0]) for r in rawPartNum]
            self.partNumBox = QComboBox()
            self.partNumBox.addItems(partNum)
            self.partNumBox.setCurrentIndex(0)
            self.layout.addWidget(QLabel("ASSIGN LABEL"), 1, 1)
            self.layout.addWidget(self.partNumBox, 2, 1)

        if not rawOrder:
            self.workOrderLabel = QLabel("NO WORK ORDERS")
            self.layout.addWidget(self.workOrderLabel, 2, 2)
        else:
            workOrders = [str(r[0] for r in rawOrder)]
            self.workOrderBox = QComboBox()
            self.workOrderBox.addItems(workOrders)
            self.layout.addWidget(QLabel("ASSIGN WORK ORDER"), 2, 2)
            self.layout.addWidget(self.workOrderBox, 2, 2)

        okBtn = QPushButton("OK")
        okBtn.clicked.connect(self.addPartToConv)
        self.layout.addWidget(okBtn, 3, 2)
        cancelBtn = QPushButton("CANCEL")
        cancelBtn.clicked.connect(closeFunct)
        self.layout.addWidget(cancelBtn, 3, 1)

        self.setLayout(self.layout)

    def addPartToConv(self):
        # TODO: ADD WORK ORDER TO TABLE
        if hasattr(self, "partNumBox"):
            partNum = self.partNumBox.currentText()
        if hasattr(self, "workOrderBox"):
            workOrder = self.workOrderBox.currentText()
        newId = getNewId()
        fecha, hora = getDateTime()
        parte = Part(newId, self.hanger_num, self.conveyor, partNum, fecha, hora)
        self.close()
        self.closeFunc()


class writePartNumWindow(QWidget):
    def __init__(self, numero_hanger, conveyor, closeFunct):
        super().__init__()

        self.hanger_num = numero_hanger
        self.conveyor = conveyor
        self.closeFunc = closeFunct

        self.setWindowTitle("ADD PART")

        self.layout = QVBoxLayout()

        self.orderLine = QLineEdit()
        self.orderLine.setPlaceholderText("SCAN WORK ORDER")

        self.partNumLine = QLineEdit()
        self.partNumLine.setPlaceholderText("SCAN PART NUMBER")

        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("CANCEL")

        self.orderLine.returnPressed.connect(self.focusPartNumber)
        self.partNumLine.returnPressed.connect(self.processScan)

        self.okButton.clicked.connect(self.addPartToConv)
        self.cancelButton.clicked.connect(closeFunct)

        self.layout.addWidget(QLabel("WORK ORDER"))
        self.layout.addWidget(self.orderLine)

        self.layout.addWidget(QLabel("PART NUMBER"))
        self.layout.addWidget(self.partNumLine)

        self.layout.addWidget(self.okButton)
        self.layout.addWidget(self.cancelButton)

        self.setLayout(self.layout)

        self.orderLine.setFocus()

    def focusPartNumber(self):

        workOrder = self.orderLine.text().strip()

        if not self.workOrderValidation():
            return

        self.partNumLine.setFocus()
        self.partNumLine.selectAll()

    def processScan(self):

        if not self.partNumValidation():
            return

        self.addPartToConv()

    def addPartToConv(self):
        if self.partNumValidation() and self.workOrderValidation():
            partNum = self.partNumLine.text().strip()
            workOrder = self.orderLine.text().strip()
            newId = getNewId()
            fecha, hora = getDateTime()

            try:
                parte = Part(
                    newId, self.hanger_num, self.conveyor, partNum, fecha, hora, workOrder
                )
                print("PART ADDED")
                self.close()
                self.closeFunc()
            except IndexError:
                defaultErrorToast(self,f"PART NUMBER {partNum} NOT FOUND")

                self.partNumLine.clear()
                self.partNumLine.setFocus()

    def partNumValidation(self):
        partNum = self.partNumLine.text().strip()
        if self.validate_initials(partNum):
            defaultErrorToast(self,"INVALID FORMAT")
            self.partNumLine.clear()
            self.partNumLine.setFocus()
            return False
        return True

    def workOrderValidation(self):
        workOrder: str = self.orderLine.text().strip()
        # print(f"Work Order: {workOrder}")
        if not self.validate_initials(workOrder):
            defaultErrorToast(self,"INVALID FORMAT")
            self.orderLine.clear()
            self.orderLine.setFocus()
            return False
        return True

    @staticmethod
    def validate_initials(work_order: str) -> bool:

        VALID_INITIALS = ["SO", "SP", "EX", "PW"]
        work_order_initials = work_order[0:2]

        return work_order_initials in VALID_INITIALS
