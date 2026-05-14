from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QMessageBox, QInputDialog, QDialog,
    QComboBox, QLineEdit, QPushButton, QGridLayout, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QMessageBox
from utils.helpers import getDateTime, getNewId
from db.part_tracking.part import Part 
from db.database import selectFromDB

class ReassingWindow(QDialog):
    def __init__(self, current_hanger, current_conveyor, part_id):
        super().__init__()
        self.setWindowTitle("REASSIGN WINDOW")
        self.current_hanger = str(current_hanger)
        self.current_conveyor = str(current_conveyor)
        self.new_hanger = str(current_hanger)
        self.new_conveyor = str(current_conveyor)
        self.conveyor_list = ["A", "B", "C", "D"]
        self.layout = QVBoxLayout()
        hbox = QHBoxLayout()
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
        self.convBox.currentIndexChanged.connect(self.changedConv)
        try:
            index = self.conveyor_list.index(self.current_conveyor)
        except:
            index = 0
        self.convBox.setCurrentIndex(index)
        hbox.addWidget(self.convBox)

        self.layout.addLayout(hbox)
        self.setLayout(self.layout)

    def changedConv(self):
        print("CHANGED")