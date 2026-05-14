from db.database import ejecutar, selectFromDB, ejecutar_y_respaldar 
from db.part_tracking.part  import Part
from db.part_tracking.program  import Program
import threading
from PyQt5.QtCore import QObject,  pyqtSignal as Signal, pyqtSlot as Slot
from utils.helpers import addTimes, getSecondsBetween, formatToTime, secondsToTime
from time import sleep
from datetime import datetime, date, timedelta
WAITING_TIME = 5
class PartsTimer(QObject):
    updateTimer = Signal(str, str)
    updatePart = Signal(Part)
    def __init__(self):
        super().__init__()
        self.dryingParts = {}
        self.stop = False
    def updateDryingParts(self):
        parts = selectFromDB("SELECT part_id from currentParts where state='DRYING' or state='WAITING'")
        self.dryingParts = {}
        for partId in parts:
            currentPart = Part(partId[0])
            endTime, maxEndTime = currentPart.getCurrentProgram().getEndTimes()
            now = datetime.now().strftime("%H:%M:%S")
            secSince = getSecondsBetween(endTime, now)
            self.dryingParts[currentPart] = str(timedelta(seconds=secSince))
        #print("UPDATE TIMER ENDED")

    def addDryingPart(self, newPart):
        program = newPart.programs[newPart.current_step]
        diffMinTime, diffMaxTime = program.getEndTimes()
        now = datetime.now().strftime("%H:%M:%S")
        secLeft = getSecondsBetween(now, diffMinTime)
        self.dryingParts[newPart] = secLeft
        
    def checkTimer(self):
        try:
            while not self.stop:
                #TO MAKE SURE THE DIRECTORY DOESNT CHANGE BY OTHER THREADS
                dryParts = self.dryingParts.copy()
                #print("START CHECKING DRYING AND WAITING TIMES")
                for part in dryParts:
                    program = part.programs[part.current_step]
                    diffMinTime, diffMaxTime = program.getEndTimes()
                    #print(f"END MIN: {diffMinTime}")
                    #print(f"END MAX: {diffMaxTime}") 
                    now = datetime.now().strftime("%H:%M:%S")
                    #SECONDS UNTIL MIN DRY
                    secLeft = getSecondsBetween(now, diffMinTime)
                    #print(f"SEC LEFT: {secLeft}")
                    #SECONDS SINCE MIN DRY
                    secSince = getSecondsBetween(program.end_time, now)
                    auxSecSince = secondsToTime(secSince)
                    #SECONDS UNTIL MAX DRY
                    secToMax = getSecondsBetween(now, diffMaxTime)
                    #print(f"SEC TO MAX: {secToMax}")
                    self.dryingParts[part] = [str(auxSecSince), str(secLeft), str(secToMax)]
                    self.updateTimer.emit(part.part_id, str(auxSecSince))
                    #print(f"SECS LEFT: {secLeft}")
                    if secLeft <= 0:
                        if program.state != "WAITING" or program.state != "DONE":
                            program.state = "WAITING"
                        program.time_deviation = str("-" + secondsToTime(secLeft*-1)) if secToMax > 0 else str(secondsToTime(secToMax*-1))
                        program.current_conveyor = program.conveyor_end
                        program.current_hanger = program.hanger_end
                        currentProgram = selectFromDB("SELECT program_id FROM currentParts WHERE part_id=?", (part.part_id, ))
                        currentProgram = currentProgram[0][0]
                        #NOTA: SI ESTA FLLANDO QUITAR ESTE IF, NO LO QUE CONTIENE
                        if currentProgram == program.program_id:
                            part.updateAll()
                            self.updatePart.emit(part)
                        else:
                            print("CURRENT PARTS IS NOT THE SAME AS TIMER")
                            print("IT SHOULD BE UPDATING IN OTHER THREAD AND NOT HAPPEN CONSECUTIVELY")
                            print(f"CURRENT: {currentProgram} UPDATING: {program.program_id}")
                        #if secToMax <= 10:
                            #TODO: ADD PRIORITY ONCE IT IS DONE
                #print("END CHECKING DRYING PARTS")
                sleep(WAITING_TIME)
        except Exception as e:
            self.connected = True
            print(f"ERROR: {e}")

    def stopTimer(self):
        self.stop = True
        print("Timer stopped and thread finished")