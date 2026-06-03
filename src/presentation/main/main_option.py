from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QTabWidget, QMessageBox
)
from PyQt5.QtCore import Qt

from src.presentation.main.robot_main import MainRobotWindow

# Not yet migrated — still imported from original modules
from boton_main.trace_hangers.trace_hangers import TraceHangersWindow
from boton_main.history.history_window import HistoryWindow

from robots.robot import Robot
from robots.robot_loader import RobotLoader
from db.part_tracking.robot_coordinator import RobotCoordinator
from db.part_tracking.parts_timer import PartsTimer
from db.part_tracking.program_queue_manager import ProgramQueueManager
from PyQt5.QtCore import QThread


class SubMainWindow(QWidget):
    def __init__(self, robot1: Robot, robot1Loader: RobotLoader,
                 robot2: Robot, robot2Loader: RobotLoader,
                 robot1Coordinator: RobotCoordinator,
                 robot2Coordinator: RobotCoordinator,
                 partsTimer: PartsTimer,
                 queueManager: ProgramQueueManager,
                 thread1: QThread, thread2: QThread,
                 timer_thread: QThread):
        super().__init__()

        self.timer_thread = timer_thread
        layout = QVBoxLayout()

        label = QLabel("WELCOME TO MAIN")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 30px; font-weight: bold; color: #2596be;")
        layout.addWidget(label)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.onChange)

        self.tabRobot = MainRobotWindow(
            robot1, robot1Loader, robot2, robot2Loader,
            robot1Coordinator, robot2Coordinator, partsTimer, queueManager,
        )
        self.tabRobot.setAttribute(Qt.WA_DeleteOnClose)

        self.tabTrace = TraceHangersWindow(
            robot1, robot1Loader, robot2, robot2Loader,
            robot1Coordinator, robot2Coordinator, partsTimer, queueManager,
            thread1, thread2, timer_thread,
        )

        self.tabHistory = HistoryWindow(
            robot1, robot1Loader, robot2, robot2Loader,
            robot1Coordinator, robot2Coordinator, partsTimer, queueManager,
        )

        self.tabs.addTab(self.tabRobot, "ROBOT MAIN")
        self.tabs.addTab(self.tabTrace, "TRACE HANGERS")
        self.tabs.addTab(self.tabHistory, "HISTORY HANGERS")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def onChange(self, i):
        if i == 1:
            self.tabTrace.timer.updateDryingParts()
            self.tabTrace.loadLayout()
            if not self.timer_thread.isRunning():
                self.timer_thread.start()
        elif i == 2:
            self.tabHistory.loadLayout()
