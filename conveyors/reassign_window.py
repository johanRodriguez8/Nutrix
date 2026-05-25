from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QMessageBox, QInputDialog, QDialog,
    QComboBox, QLineEdit, QPushButton, QGridLayout, QTabWidget, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QMessageBox
from utils.helpers import getDateTime, getNewId
from db.part_tracking.part import Part 
from db.database import selectFromDB, ejecutar, ejecutar_y_respaldar

class ReassingWindow(QDialog):
    def __init__(self, current_hanger, current_conveyor, part_id):
        super().__init__()
        self.setWindowTitle("REASSIGN WINDOW")
        self.current_hanger = str(current_hanger)
        self.current_conveyor = str(current_conveyor)
        self.new_hanger = str(current_hanger)
        self.new_conveyor = str(current_conveyor)
        self.part_id = part_id
        self.conveyor_list = ["A", "B", "C", "D"]
        self.layout = QVBoxLayout()
        hbox = QHBoxLayout()
        self.accept_button = QPushButton("ACCEPT")
        currentHangerLabel = QLabel(f"FROM HANGER: {current_hanger}")
        hbox.addWidget(currentHangerLabel)
        currentConvLabel = QLabel(f"CONVEYOR: {current_conveyor}")
        hbox.addWidget(currentConvLabel)
        self.layout.addLayout(hbox)

        hangers = selectFromDB("""
        SELECT hanger_num FROM conveyors WHERE status=? AND conveyor=?
        """, ("EMPTY", self.new_conveyor))

        hangers = [str(hanger[0]) for hanger in hangers]

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("TO   HANGER: "))
        self.hangerBox = QComboBox()
        self.hangerBox.addItems(hangers)
        try:
            index = hangers.index(self.new_hanger)
        except:
            index = 0
        self.hangerBox.setCurrentIndex(index)
        hbox.addWidget(self.hangerBox)

        hbox.addWidget(QLabel("CONVEYOR: "))

        self.convBox = QComboBox()
        self.convBox.addItems(self.conveyor_list)
        #self.convBox.currentIndexChanged.connect(self.changedConv)


        self.accept_button.clicked.connect(lambda: self.changedConv())
        try:
            index = self.conveyor_list.index(self.current_conveyor)
        except:
            index = 0
        self.convBox.setCurrentIndex(index)
        hbox.addWidget(self.convBox)

        self.layout.addLayout(hbox)
        self.layout.addWidget(self.accept_button)
        self.setLayout(self.layout)

    def changedConv(self):

        new_hanger = self.hangerBox.currentText()
        new_conveyor = self.convBox.currentText()
        print("CHANGED")
        print(f"{new_hanger}")
        print(f"{new_conveyor}")
        print(f"{self.part_id}")

        self.update_part(new_hanger,new_conveyor)


    def update_part(self, new_hanger, new_conveyor):
        resultado = selectFromDB("SELECT part_id, hanger_num, conveyor, hanger_id FROM parts WHERE part_id = ?", (self.part_id,))
        print(f"antes del update: {resultado}")

        if not resultado:
            return 
        part_info = selectFromDB("SELECT part_num, order_id FROM parts WHERE part_id = ?", (self.part_id,))
        part_num = part_info[0][0] if part_info else None
        order_id = part_info[0][1] if part_info else None

        ejecutar_y_respaldar(
            "UPDATE parts SET hanger_num = ?, conveyor = ? WHERE part_id = ?",
            (new_hanger, new_conveyor, self.part_id)
        )

        ejecutar_y_respaldar(
            "UPDATE currentParts SET current_hanger = ?, current_conveyor = ? WHERE part_id = ?",
            (new_hanger, new_conveyor, self.part_id)
        )
        

        ejecutar_y_respaldar(
            "UPDATE conveyors SET status = 'EMPTY', part_id = NULL, part_num = NULL, order_id = NULL WHERE hanger_num = ? AND conveyor = ?",
            (self.current_hanger, self.current_conveyor)
        )

        ejecutar_y_respaldar(
            "UPDATE conveyors SET status = 'FULL', part_id = ?, part_num = ?, order_id = ? WHERE hanger_num = ? AND conveyor = ?",
            (self.part_id, part_num, order_id, new_hanger, new_conveyor)
        )


