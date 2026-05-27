from db.database import ejecutar, selectFromDB, ejecutar_y_respaldar 
from db.part_tracking.part  import Part
from db.part_tracking.program  import Program
import threading
from PyQt5.QtCore import QObject,  pyqtSignal as Signal, pyqtSlot as Slot
from utils.helpers import addTimes, getSecondsBetween, formatToTime, secondsToTime
from time import sleep
from datetime import datetime, date, timedelta

WAITING_TIME = 1

class PartsTimer(QObject):
    updateTimer = Signal(str, str)
    updatePart = Signal(Part)

    def __init__(self):
        super().__init__()
        self.dryingParts = {}
        self.fullStop = False
        self.stopChecking = False
        self._lock = threading.Lock()

    def updateDryingParts(self):
        parts = selectFromDB("SELECT part_id from currentParts where state='DRYING' or state='WAITING'")
        new_dict = {}
        for partId in parts:
            currentPart = Part(partId[0])
            endTime, maxEndTime = currentPart.getCurrentProgram().getEndTimes()
            now = datetime.now().strftime("%H:%M:%S")
            secSince = getSecondsBetween(endTime, now)
            new_dict[currentPart] = str(timedelta(seconds=secSince))
        with self._lock:
            self.dryingParts = new_dict

    def addDryingPart(self, newPart):
        program = newPart.getCurrentProgram()
        diffMinTime, _ = program.getEndTimes()
        now = datetime.now().strftime("%H:%M:%S")
        secLeft = getSecondsBetween(now, diffMinTime)
        with self._lock:
            self.dryingParts[newPart] = secLeft

    def timerCycle(self):
        try:
            print("STARTING TIMER")
            while not self.fullStop:
                if not self.stopChecking:
                    self.checkTimer()
                sleep(WAITING_TIME)
        except Exception as e:
            print(f"ERROR: {e}")

    def checkTimer(self):
        with self._lock:
            dryParts = self.dryingParts.copy()

        for part in dryParts:
            program = part.programs[part.current_step]
            diffMinTime, diffMaxTime = program.getEndTimes()
            now = datetime.now().strftime("%H:%M:%S")
            secLeft = getSecondsBetween(now, diffMinTime)
            secSince = getSecondsBetween(program.end_time, now)
            auxSecSince = secondsToTime(secSince)
            secToMax = getSecondsBetween(now, diffMaxTime)

            with self._lock:
                self.dryingParts[part] = [str(auxSecSince), str(secLeft), str(secToMax)]

            self.updateTimer.emit(part.part_id, str(auxSecSince))

            if secLeft <= 0:
                if program.state != "WAITING" or program.state != "DONE":
                    program.state = "WAITING"
                program.time_deviation = str("-" + secondsToTime(secLeft*-1)) if secToMax > 0 else str(secondsToTime(secToMax*-1))
                program.current_conveyor = program.conveyor_end
                program.current_hanger = program.hanger_end
                currentProgram = selectFromDB("SELECT program_id FROM currentParts WHERE part_id=?", (part.part_id,))
                currentProgram = currentProgram[0][0]
                if currentProgram == program.program_id:
                    part.updateAll()
                    self.updatePart.emit(part)
                else:
                    print("CURRENT PARTS IS NOT THE SAME AS TIMER")
                    print("IT SHOULD BE UPDATING IN OTHER THREAD AND NOT HAPPEN CONSECUTIVELY")
                    print(f"CURRENT: {currentProgram} UPDATING: {program.program_id}")

    def stopTimer(self):
        self.stopChecking = True
        print("Stopped checking the timer")