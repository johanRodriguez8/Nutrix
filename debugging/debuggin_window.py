from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QListWidget, QFrame
)
from PyQt5.QtCore import Qt
import copy
from opcua import Client
import paramiko
import re
import platform
import subprocess
from db.part_tracking.parts_service import load_part, create_part
from db.database import print_sqlite_table, init_users_table, init_programs_table, init_sequences_table, init_conveyors_tables, init_parts_table, init_partNumbers_table, init_currentParts_table, init_history_table
from db.connection import db
from db.repositories import conveyors_repo, history_repo, current_parts_repo, parts_repo
from db.part_tracking.program import Program
from utils.helpers import MultiRowBorderDelegate, FONT_SIZE, LEN_SIZE, getDateTime, getNewId
# ================= ESTILO =================
FONT_SIZE = 20
BOTON_STYLE = f"""
QPushButton {{
    background-color: #2596be;
    color: white;
    font-weight: bold;
    font-size: {FONT_SIZE}px;
    padding: 7px;
    border-radius: 5px;
}}
QPushButton:hover {{
    background-color: #1f7fa0;
}}
"""
TITULO_STYLE = f"font-size: {FONT_SIZE+10}px; font-weight:bold; color: #2596be;"


# ================= VENTANA PRINCIPAL =================
class SubVentanaDebug(QWidget):
    def __init__(self, robot1=None, robot2=None):
        super().__init__()
        self.robot1 = robot1
        self.robot2 = robot2
        self.setWindowTitle("DEBUG TOOLS")
        self.showMaximized()

        layout = QVBoxLayout()
        tables = ["parts", "conveyors", "history", "currentParts", "partNumbers", "programs"]
        title = QLabel("DEBUG TOOLS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(TITULO_STYLE)
        layout.addWidget(title)

        # BOTONES
        for table in tables:
            btn_ip = QPushButton(f"RESET {table}")
            btn_ip.setStyleSheet(BOTON_STYLE)
            btn_ip.clicked.connect(lambda _, tabla=table: self.resetTable(tabla))
            layout.addWidget(btn_ip)
        for table in tables:
            btn_ip = QPushButton(f"PRINT {table}")
            btn_ip.setStyleSheet(BOTON_STYLE)
            btn_ip.clicked.connect(lambda _, tabla=table: print_sqlite_table(tabla))
            layout.addWidget(btn_ip)
            
        restartBtn = QPushButton(f"RESTART HISTORY AND CURRENTPARTS")
        restartBtn.setStyleSheet(BOTON_STYLE)
        restartBtn.clicked.connect(lambda _: self.restartEverythingCurrent())
        layout.addWidget(restartBtn)

        restartBtn = QPushButton(f"RESTART PARTS-CONVEYOR-HISTORY-CURRENT")
        restartBtn.setStyleSheet(BOTON_STYLE)
        restartBtn.clicked.connect(lambda _: self.restartParts())
        layout.addWidget(restartBtn)

        convABtn = QPushButton(f"FILL CONVEYOR A")
        convABtn.setStyleSheet(BOTON_STYLE)
        convABtn.clicked.connect(lambda _: self.fillConveyor("A"))
        layout.addWidget(convABtn)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        layout.addWidget(separator)

        outputsTitle = QLabel("TEST DE SALIDAS BOOLEANAS (set_bool_output)")
        outputsTitle.setAlignment(Qt.AlignCenter)
        outputsTitle.setStyleSheet(TITULO_STYLE)
        layout.addWidget(outputsTitle)

        for robot, robotName in [(self.robot1, "Robot1"), (self.robot2, "Robot2")]:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{robotName} - Indice de output:"))

            indexInput = QLineEdit("0")
            indexInput.setFixedWidth(50)
            row.addWidget(indexInput)

            onBtn = QPushButton(f"{robotName} OUTPUT ON")
            onBtn.setStyleSheet(BOTON_STYLE)
            onBtn.clicked.connect(lambda _, r=robot, n=robotName, i=indexInput: self.testBoolOutput(r, n, i, True))
            row.addWidget(onBtn)

            offBtn = QPushButton(f"{robotName} OUTPUT OFF")
            offBtn.setStyleSheet(BOTON_STYLE)
            offBtn.clicked.connect(lambda _, r=robot, n=robotName, i=indexInput: self.testBoolOutput(r, n, i, False))
            row.addWidget(offBtn)

            layout.addLayout(row)

        layout.addStretch()
        self.setLayout(layout)

    def testBoolOutput(self, robot, robotName, indexInput, value):
        if robot is None:
            QMessageBox.warning(self, "ERROR", f"{robotName} no fue provisto a la ventana de debug")
            return
        try:
            index = int(indexInput.text())
        except ValueError:
            QMessageBox.warning(self, "ERROR", "El indice debe ser un numero entero")
            return

        robot.set_bool_output(index, value)

        if robot.connected:
            print(f"{robotName}: output {index} -> {value} enviado OK")
        else:
            msg = f"{robotName}: fallo al enviar output {index}. Revisar consola/conexion."
            print(msg)
            QMessageBox.warning(self, "ERROR DE COMUNICACION", msg)

    def restartParts(self):
        inits = {
        "conveyors": init_conveyors_tables,
        "parts": init_parts_table,
        "currentParts" : init_currentParts_table,
        "history": init_history_table
            }
        for table, function in inits.items():
            db.drop_table(table)
            function()
            if table == "conveyors":
                conveyors = {
                    'A': 30,
                    'B': 76,
                    'C': 74,
                    'D': 30
                }
                j = 1
                for nombre_tabla, cantidad_hangers in conveyors.items():
                    #llena de hangers la tabla
                    for i in range(1, cantidad_hangers + 1):
                        conveyors_repo.insert_hanger(j, i, nombre_tabla, None)
                        j = j + 1

    def resetTable(self, table):
        inits = {
    "conveyors": init_conveyors_tables,
    "parts": init_parts_table,
    "partNumbers" : init_partNumbers_table,
    "currentParts" : init_currentParts_table,
    "history": init_history_table,
    "programs": init_programs_table
        }
        db.drop_table(table)
        inits[table]()
        if table == "conveyors":
            conveyors = {
                'A': 30,
                'B': 76,
                'C': 74,
                'D': 30
            }
            j = 1
            for nombre_tabla, cantidad_hangers in conveyors.items():
                #llena de hangers la tabla
                for i in range(1, cantidad_hangers + 1):
                    conveyors_repo.insert_hanger(j, i, nombre_tabla, None)
                    j = j + 1
                    
    def restartEverythingCurrent(self):
        partsId = history_repo.distinct_part_ids()

        for partId in partsId:
            part = load_part(partId[0])
            for program in part.programs:
                programAux = Program()
                history_repo.reset_step(
                    programAux.state, programAux.start_date, programAux.start_time,
                    programAux.end_date, programAux.end_time, programAux.run_time,
                    programAux.station, programAux.time_deviation, part.part_id, program.step,
                )
                if program.step == "1" or program.step == 1:

                    part.setCurrentProgram(program)

                    current_parts_repo.reset_to_ready(
                        program.step, programAux.start_date, programAux.start_time,
                        programAux.end_date, programAux.end_time, programAux.run_time,
                        programAux.station, programAux.time_deviation, program.program_id, part.part_id,
                    )
                    history_repo.set_first_step_state_ready(part.part_id, program.program_id)
                    parts_repo.set_sequence_index(program.step, part.part_id)
                        
    def fillConveyor(self, conveyor):
        if conveyor == "A":
            length = 30
        elif conveyor == "B":
            length = 76
        elif conveyor == "C":
            length = 74
        elif conveyor == "D":
            length = 30
        
        for i in range(length):

            newId = getNewId()
            fecha, hora = getDateTime()
            parte = create_part(newId, i+1, "A", (i%4)+1, fecha, hora, "WO00100")

class DualConsole:
    def __init__(self):
        self.file1 = open("console1.log", "w", buffering=1)
        self.file2 = open("console2.log", "w", buffering=1)

    def print(self, message: str, console: int = 1):
        print(message)
        if console == 1:
            self.file1.write(message + "\n")
            self.file1.flush()
        elif console == 2:
            self.file2.write(message + "\n")
            self.file2.flush()
        else:
            raise ValueError("Console must be 1 or 2")