from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QScrollArea, QMainWindow, QSizePolicy, QRadioButton, QButtonGroup
)

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot as Slot
from PyQt5 import QtGui
import threading
from db.part_tracking.part  import Part
from db.part_tracking.program  import Program
import time
from utils.helpers import MultiRowBorderDelegate, FONT_SIZE, secondsToTime
from db.database import selectFromDB
from db.part_tracking.robot_coordinator import RobotCoordinator
from db.part_tracking.parts_timer import PartsTimer
from db.part_tracking.program_queue_manager import ProgramQueueManager
from robots.robot import Robot
from robots.robot_loader import RobotLoader
TIME_OUT = 300 #Tiempo que espera una conexion antes de desconectarse. Esta definida en segundos
ID_COL = 0
PROGRAM_COL = ID_COL+1
ROBOT_COL = PROGRAM_COL+1
MINDRY_COL = ROBOT_COL+1
MAXDRY_COL = MINDRY_COL+1
CURDRY_COL = MAXDRY_COL+1
STATE_COL = CURDRY_COL+1
DATE_COL = STATE_COL+1
START_COL = DATE_COL+1
END_COL = START_COL+1
RUN_COL = END_COL+1
# HANGER_COL = RUN_COL+1
# FROM_COL = HANGER_COL+1
# TOHANGER_COL = FROM_COL+1
# TO_COL = TOHANGER_COL+1
CURHANG_COL = RUN_COL+1
CURCONV_COL = CURHANG_COL+1
DEV_COL = CURCONV_COL+1
WAITING_TIME = 1 #seconds
WAIT_LED_TIME = 10000 #ms
class TraceHangersWindow(QMainWindow):

    update_conn_signal = pyqtSignal(list)
    update_table_signal = pyqtSignal(str, int, str)

    def __init__(self, robot1:Robot, robot1Loader:RobotLoader, robot2:Robot, robot2Loader:RobotLoader, 
        robot1Coordinator:RobotCoordinator, robot2Coordinator:RobotCoordinator, partsTimer:PartsTimer, queueManager:ProgramQueueManager):
        super().__init__()
        self.queueManager = queueManager

        self.robot1Coordinator = robot1Coordinator
        

        self.robot2Coordinator = robot2Coordinator


        self.timer = partsTimer
        self.timer_thread = QThread()
        self.timer.moveToThread(self.timer_thread)
        self.timer_thread.started.connect(self.timer.checkTimer)
        self.timer.updateTimer.connect(self.updateCurrentTimer)
        self.timer.updatePart.connect(self.updateTimeDev)

        self.robot1 = robot1
        self.robot1Loader = robot1Loader
        self.robot2 = robot2
        self.robot2Loader = robot2Loader
        self.isListening = False
        self.setWindowTitle("TRACE HANGERS")
        self.showMaximized()
        self.loadLayout()
        self.lastPartIdR1 = None
        self.lastPartIdR2 = None

    def loadLayout(self):
        # ---------- MAIN LAYOUT ----------
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignTop)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll.setWidget(container)
        self.setCentralWidget(scroll)

        # Title
        titulo = QLabel("TRACE HANGERS")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:30px;font-weight:bold;color:#2596be;")
        layout.addWidget(titulo)

        # Radio buttons group (so only one can be selected at a time)
        self.robotButtonGroup = QButtonGroup()

        # LEDS
        padding_space = 110
        padding = QLabel("")
        padding.setFixedWidth(padding_space)
        hbox = QHBoxLayout()
        hbox.addWidget(padding)

        # *** Radio button ROBOT 1 ***
        self.radioR1 = QRadioButton("ASSIGN ROBOT 1 TO CONVEYOR B")
        self.radioR1.setFont(QFont(self.radioR1.font().family(), FONT_SIZE))
        self.radioR1.setChecked(True)
        self.robotButtonGroup.addButton(self.radioR1, 1)
        hbox.addWidget(self.radioR1)

        aux = QLabel("ROBOT 1: ")
        custom_font = aux.font()
        custom_font.setPointSize(FONT_SIZE)
        aux.setFont(custom_font)
        aux.setAlignment(Qt.AlignRight)
        hbox.addWidget(aux)
        color = QLabel("■")
        color.setStyleSheet("color:red")
        hbox.addWidget(color)

        aux = QLabel("CONNECTED:")
        custom_font = aux.font()
        custom_font.setPointSize(FONT_SIZE)
        aux.setFont(custom_font)
        aux.setAlignment(Qt.AlignRight)
        hbox.addWidget(aux)
        self.ledR1 = QLabel("●")
        self.ledR1.setStyleSheet(f"color:gray; font-size:{FONT_SIZE+4}px;")
        self.ledR1.setAlignment(Qt.AlignLeft)
        hbox.addWidget(self.ledR1)
        layout.addLayout(hbox)

            # *** PROGRAM STARTED - ROBOT 1 ***
        aux = QLabel("PROGRAM STARTED:")
        custom_font = aux.font()
        custom_font.setPointSize(FONT_SIZE)
        aux.setFont(custom_font)
        aux.setAlignment(Qt.AlignRight)
        hbox.addWidget(aux)
        self.ledR1Started= QLabel("●")
        self.ledR1Started.setStyleSheet(f"color:gray; font-size:{FONT_SIZE+4}px;")
        self.ledR1Started.setAlignment(Qt.AlignLeft)
        hbox.addWidget(self.ledR1Started)

        padding = QLabel("")
        padding.setFixedWidth(padding_space)
        hbox = QHBoxLayout()
        hbox.addWidget(padding)

        # *** Radio button ROBOT 2 ***
        self.radioR2 = QRadioButton("ASSIGN ROBOT 2 TO CONVEYOR B")
        self.radioR2.setFont(QFont(self.radioR2.font().family(), FONT_SIZE))
        self.robotButtonGroup.addButton(self.radioR2, 2)
        hbox.addWidget(self.radioR2)

        aux = QLabel("ROBOT 2: ")
        custom_font = aux.font()
        custom_font.setPointSize(FONT_SIZE)
        aux.setFont(custom_font)
        aux.setAlignment(Qt.AlignRight)
        hbox.addWidget(aux)
        color = QLabel("■")
        color.setStyleSheet("color:blue")
        hbox.addWidget(color)


        aux = QLabel("CONNECTED:")
        custom_font = aux.font()
        custom_font.setPointSize(FONT_SIZE)
        aux.setFont(custom_font)
        aux.setAlignment(Qt.AlignRight)
        hbox.addWidget(aux)
        self.ledR2 = QLabel("●")
        self.ledR2.setStyleSheet(f"color:gray; font-size:{FONT_SIZE+4}px;")
        self.ledR2.setAlignment(Qt.AlignLeft)
        hbox.addWidget(self.ledR2)
        layout.addLayout(hbox)

            # *** PROGRAM STOPPED - ROBOT 2 ***
        aux = QLabel("PROGRAM STOPPED:")
        custom_font = aux.font()
        custom_font.setPointSize(FONT_SIZE)
        aux.setFont(custom_font)
        aux.setAlignment(Qt.AlignRight)
        hbox.addWidget(aux)
        self.ledR2Stopped = QLabel("●")
        self.ledR2Stopped.setStyleSheet(f"color:gray; font-size:{FONT_SIZE+4}px;")
        self.ledR2Stopped.setAlignment(Qt.AlignLeft)
        hbox.addWidget(self.ledR2Stopped)

        layout.addLayout(hbox)

        recordButton = QPushButton("START PROGRAM")
        recordButton.clicked.connect(
            lambda _:  self.startCycle()
        )
        stopBtn = QPushButton("STOP CYCLE")
        stopBtn.clicked.connect(lambda _: self.stopUpdate())
        layout.addWidget(recordButton)
        layout.addWidget(stopBtn)
        self.update_conn_signal.connect(self.updateConn)
        self.update_table_signal.connect(self.updateTableCell)
        # ---------- TIMER FOR LED UPDATE ----------
        self.timerConn = QTimer(self)
        self.timerConn.timeout.connect(self.threadConnUpdate)
        self.timerConn.start(WAIT_LED_TIME)

        # ---------- LOAD PARTS ----------
        ids = selectFromDB(
            "SELECT DISTINCT part_id FROM currentParts ORDER BY part_id"
        )
        piezas = []
        for id in ids:
            aux = selectFromDB(
                """
                SELECT part_id, part_num, start_date, start_time, hanger_id, conveyor
                FROM parts WHERE part_id=?
                """,
                id
            )
            piezas.append(aux[0])

        self.mainTable = QTableWidget()
        self.mainTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.mainDelegate = MultiRowBorderDelegate(self.mainTable)
        self.mainTable.setItemDelegate(self.mainDelegate)
        titles = [
                "PART ID", "PROGRAM", "ROBOT", "MIN DRY", "MAX DRY", "CURRENT DRY",
                "STATE", "DATE", "START", "END", "RUN", "CUR HANG", "CUR CONV", "TIME DEV"
            ]
        self.mainTable.setColumnCount(len(titles))
        self.mainTable.setHorizontalHeaderLabels(titles)
        header = self.mainTable.horizontalHeader()
        self.mainTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for col in range(self.mainTable.columnCount()):
            #header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
            if col in [ID_COL, DATE_COL, STATE_COL, START_COL, END_COL, RUN_COL, DEV_COL, CURDRY_COL]:
                header.setSectionResizeMode(col, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.mainTable.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.mainTable)
        self.loadDataOnTable(piezas)

        self.radioR1.clicked.connect(self.on_robot_selected)
        self.radioR2.clicked.connect(self.on_robot_selected)


    def highlightProgram(self, partId, rowSearch=None, color="red"):

        rows = self.mainTable.rowCount()

        for row in range(rows):
            item = self.mainTable.item(row, 0)
            if item and item.text() == partId:
                #self.mainDelegate.clear()  # remove previous highlight
                self.mainDelegate.set_row_color(row, color)
                break


    def dehighlightProgram(self, partId):
        rows = self.mainTable.rowCount()
        for row in range(rows):
            item = self.mainTable.item(row, 0)
            if item and item.text() == partId:
                #self.mainDelegate.clear()  # remove previous highlight
                self.mainDelegate.remove_row(row)
                #self.mainDelegate.set_row_color(row, color)
                break

    def clearHighlights(self, robotNum):
        if robotNum == 1 and self.lastPartIdR1:
            self.dehighlightProgram(self.lastPartIdR1)
            self.lastPartIdR1 = None
        if robotNum == 2 and self.lastPartIdR2:
            self.dehighlightProgram(self.lastPartIdR2)
            self.lastPartIdR2 = None

    # ---------- LOAD TABLE DATA ----------
    def loadDataOnTable(self, piezas):

        self.mainTable.setRowCount(len(piezas))

        for r, pieza in enumerate(piezas):

            partId = pieza[0]
            partNum = pieza[1]
            programs = selectFromDB(
                """
                SELECT program_id, min_drying_time, max_drying_time, 
                robot_num, state, start_date, start_time, end_date, end_time,
                run_time, hanger_num, conveyor_start, conveyor_end, time_deviation, hanger_end,
                current_hanger, current_conveyor
                FROM currentParts
                WHERE part_id=?
                """,
                (partId,)
            )
            programId, minTime, maxTime, robot, state, start_date, start_time, end_date, end_time, \
            run_time, hanger_num, conveyor_start, conveyor_end, time_deviation, hanger_end, current_hanger, current_conveyor = programs[0]

            self.mainTable.setRowHeight(r, FONT_SIZE * 2 + 10)
            statusItem =  QTableWidgetItem(state)
            currentItem = QTableWidgetItem("")
            items = [
                QTableWidgetItem(partId),
                QTableWidgetItem(programId),
                QTableWidgetItem(str(robot)),
                QTableWidgetItem(minTime),
                QTableWidgetItem(maxTime),
                currentItem,
                statusItem,
                QTableWidgetItem(start_date),
                QTableWidgetItem(start_time),
                QTableWidgetItem(end_time),
                QTableWidgetItem(run_time),
                QTableWidgetItem(str(current_hanger)),
                QTableWidgetItem(str(current_conveyor)),
                QTableWidgetItem(time_deviation)
            ]
            nonColorValues = [0, None, "00/00/00", "00:00", "IDLE", "", " "]
            color = QtGui.QColor("#c8f7c5")

            for i, item in enumerate(items):
                aux = item.text()
                if not (item.text() in nonColorValues):
                    item.setBackground(color)
                item.setTextAlignment(Qt.AlignCenter)
                font = item.font()
                font.setPointSize(FONT_SIZE)
                item.setFont(font)

                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                self.mainTable.setItem(r, i, item)
            self.mainTable.resizeRowsToContents()
            self.adjustTableHeight(self.mainTable)
            self.mainTable.updateGeometry()

    # ---------- LED UPDATE ----------
    def threadConnUpdate(self):

        self.update_conn_signal.emit(
            [self.robot1.connected, self.robot2.connected]
        )
    def updateConn(self, states):
        leds = [self.ledR1, self.ledR2]
        for i, led in enumerate(leds):
            if states[i]:
                color = "green"
            else:
                color = "red"
            led.setStyleSheet(
                f"color:{color}; font-size:{FONT_SIZE+4}px;"
            )

    @Slot(str, int, str)
    def updateTableCell(self, partId, column=None, value=None):
        rows = self.mainTable.rowCount()
        for row in range(rows):
            item = self.mainTable.item(row, 0)
            if item and item.text() == partId:
                newItem = QTableWidgetItem(str(value))
                newItem.setTextAlignment(Qt.AlignCenter)
                font = newItem.font()
                font.setPointSize(FONT_SIZE)
                newItem.setFont(font)
                if column == DEV_COL:
                    if value[0] == "-":
                        newItem.setBackground(QtGui.QColor("red"))
                    else:
                        newItem.setBackground(QtGui.QColor("#c8f7c5"))
                    newItem.setText(value)
                else:
                    newItem.setBackground(QtGui.QColor("#c8f7c5"))
                    
                self.mainTable.setItem(row, column, newItem)
                break

    @Slot(Part, Program)
    def updateTablePart(self, part:Part, program:Program):
        cols = [*range(0, CURDRY_COL), *range(STATE_COL, DEV_COL+1)]
        vals = [part.part_id, program.program_id, program.robot_num, program.min_drying_time, program.max_drying_time, \
            program.state, program.start_date, program.start_time, program.end_time, program.run_time,  \
                program.current_hanger, program.current_conveyor, program.time_deviation]
        vals = [str(x) for x in vals]
        rows = self.mainTable.rowCount()
        for row in range(rows):
            item = self.mainTable.item(row, 0)
            if item and item.text() == part.part_id:
                for column, value in  zip(cols, vals):
                    newItem = QTableWidgetItem(str(value))
                    newItem.setTextAlignment(Qt.AlignCenter)
                    font = newItem.font()
                    font.setPointSize(FONT_SIZE)
                    newItem.setFont(font)
                    if column == DEV_COL:
                        if value[0] == "-":
                            newItem.setBackground(QtGui.QColor("red"))
                        else:
                            newItem.setBackground(QtGui.QColor("#c8f7c5"))
                        newItem.setText(value)
                    else:
                        newItem.setBackground(QtGui.QColor("#c8f7c5"))

                    self.mainTable.setItem(row, column, newItem)
                break

    def startCycle(self):
        #TODO: SIMPLIFY SIGNALS
        #Inician los coordinadores
        self.isListening = True
        self.startRobot1()
        self.startRobot2()
        self.startTimer()

    def startTimer(self):
        self.timer.stop = False
        self.timer.updateDryingParts()
        self.timer_thread.start()

    def startRobot1(self):
        self.coordinator1Thread = QThread()
        self.robot1Coordinator.moveToThread(self.coordinator1Thread)
        self.coordinator1Thread.started.connect(self.robot1Coordinator.startCycle)
        self.robot1Coordinator.programRunning.connect(self.updateTablePart) #= pyqtSignal(str, str, str, str)
        self.robot1Coordinator.programEnded.connect(self.updateTablePart)
        self.robot1Coordinator.changedPart.connect(self.updateLastPart)
        self.robot1Coordinator.updateTimeDev.connect(self.updateTimeDev)
        self.robot1Coordinator.showPreliminarNextProgram.connect(self.updatePreliminarCharacteristics)
        self.robot1Coordinator.updateProgramPart.connect(self.updateTablePart)
        self.robot1Coordinator.startPart.connect(self.startFirstPart)
        self.robot1Coordinator.noPart.connect(self.clearHighlights)
        self.robot1Coordinator.stop = False
        self.coordinator1Thread.start()
    
    def startRobot2(self):
        self.coordinator2Thread = QThread()
        self.robot2Coordinator.moveToThread(self.coordinator2Thread)
        self.coordinator2Thread.started.connect(self.robot2Coordinator.startCycle)
        self.robot2Coordinator.programRunning.connect(self.updateTablePart) #= pyqtSignal(str, str, str, str)
        self.robot2Coordinator.programEnded.connect(self.updateTablePart)
        self.robot2Coordinator.changedPart.connect(self.updateLastPart)
        self.robot2Coordinator.updateTimeDev.connect(self.updateTimeDev)
        self.robot2Coordinator.showPreliminarNextProgram.connect(self.updatePreliminarCharacteristics)
        self.robot2Coordinator.updateProgramPart.connect(self.updateTablePart)
        self.robot2Coordinator.startPart.connect(self.startFirstPart)
        self.robot2Coordinator.noPart.connect(self.clearHighlights)
        self.robot2Coordinator.stop = False
        self.coordinator2Thread.start()

    def on_robot_selected(self):
        print("SEÑAL RECIBIDA")  # ← ¿aparece esto?
        selected = self.robotButtonGroup.checkedId()
        print(f"ID seleccionado: {selected}")
        if selected == 1:
            self.queueManager.priority = 1
            print("Robot 1 seleccionado")
        elif selected == 2:
            self.queueManager.priority = 2
            print("Robot 2 seleccionado")

#Deberia haber 10 hilosXD
    @Slot(Part, Program)
    def updatePreliminarCharacteristics(self, part:Part, nextProgram:Program):
        self.update_table_signal.emit(
                    part.part_id,
                    PROGRAM_COL,
                    str(nextProgram.program_id)
                )
        self.update_table_signal.emit(
                    part.part_id,
                    ROBOT_COL,
                    str(nextProgram.robot_num)
                )
        self.update_table_signal.emit(
                    part.part_id,
                    CURHANG_COL,
                    str(nextProgram.current_hanger)
                )
        self.update_table_signal.emit(
                    part.part_id,
                    CURCONV_COL,
                    str(nextProgram.current_conveyor)
                )

    @Slot(Part, int)
    def startFirstPart(self, part:Part, robotNum):
        if robotNum == 1:
            self.highlightProgram(part.part_id)
            self.lastPartIdR1 = part.part_id
        else:
            self.highlightProgram(part.part_id, color="blue")
            self.lastPartIdR2 = part.part_id
        program = part.getCurrentProgram()
        self.updateTablePart(part, program)

    @Slot(Part, Part, int)
    def updateLastPart(self, lastPart, newPart, robotNum):
            if robotNum == 1:
                if self.lastPartIdR1:
                    self.dehighlightProgram(self.lastPartIdR1)
                self.highlightProgram(newPart.part_id)
                self.lastPartIdR1 = newPart.part_id
            else:
                if self.lastPartIdR2:
                    self.dehighlightProgram(self.lastPartIdR2)
                self.highlightProgram(newPart.part_id, color="blue")
                self.lastPartIdR2 = newPart.part_id
            program = newPart.getCurrentProgram()
            self.updateTablePart(newPart, program)
            #TODO: QUITAR EL SIGUIENTE BLOQUE DE CODIGO, PARECE REDUNDANTE O QUE DEBERIA ESTAR EN COORDINADOR
            if lastPart != newPart and lastPart != None:
                lastProgram = newPart.getCurrentProgram()
                self.updateTablePart(newPart, lastProgram)
    @Slot(Part)
    def updateTimeDev(self, part:Part):
        program = part.getCurrentProgram()
        self.update_table_signal.emit(
                    part.part_id,
                    STATE_COL,
                    str(program.state)
                )
        #print(f"TIME DEV: {doneProgram.time_deviation}")
        self.update_table_signal.emit(
                    part.part_id,
                    DEV_COL,
                    str(program.time_deviation)
                )

    @Slot(str, str)
    def updateCurrentTimer(self, partId, currentTime):
         self.update_table_signal.emit(
                    partId,
                    CURDRY_COL,
                    str(currentTime)
                )
 
    def stopUpdate(self):
        self.isListening = False
        self.stopRobot1()
        self.stopRobot2()
        self.stopTimer()

    def stopTimer(self):
        self.timer_thread.requestInterruption() # 1. Solicitar alto
        self.timer_thread.quit()                # 3. Salir del bucle de eventos
        self.timer_thread.wait()

    def stopRobot1(self):
        self.robot1Coordinator.stopCycle()
        self.coordinator1Thread.requestInterruption() # 1. Solicitar alto
        self.coordinator1Thread.quit()                # 3. Salir del bucle de eventos
        self.coordinator1Thread.wait()
    
    def stopRobot2(self):
        self.robot2Coordinator.stopCycle()
        self.coordinator2Thread.requestInterruption() # 1. Solicitar alto
        self.coordinator2Thread.quit()                # 3. Salir del bucle de eventos
        self.coordinator2Thread.wait()

    def adjustTableHeight(self, table):
        table.resizeRowsToContents()

        height = table.horizontalHeader().height()

        for row in range(table.rowCount()):
            height += table.rowHeight(row)

        if table.horizontalScrollBar().isVisible():
            height += table.horizontalScrollBar().height()

        # small buffer to avoid clipping
        table.setMinimumHeight(height)
        table.setMaximumHeight(height)
