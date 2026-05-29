from db.database import selectFromDB, ejecutar_y_respaldar, print_sqlite_table
from utils.helpers import getDateTime
from db.part_tracking.program import Program
import copy
class Part():
    def __init__(self, part_id=None, hanger_num=None, conveyor=None, part_num=None, start_date=None, start_time=None, order_id=None):
        self.part_id = part_id
        self.part_num = part_num
        self.current_step = 0
        self.programs = []
        self.hanger_num = hanger_num
        self.conveyor = conveyor
        self.status = 1
        #print_sqlite_table("parts")
        if part_id:
            partExist = selectFromDB("""
                    SELECT * FROM parts WHERE part_id=?
                """, (self.part_id,))

            if partExist:
                #print(f"Ya existe {partExist}")
                self.getInformation(part_id)
            else:
                #print(f"NO EXISTE {partExist} {part_id}")
                self.init_part_conveyor(part_id, hanger_num, conveyor, part_num, start_date, start_time, order_id)
                self.init_part_in_history(part_id)
                self.getInformation(part_id)
                self.init_current_part(hanger_num, conveyor)
                
    def __hash__(self):
        return hash(self.part_id)

    def __eq__(self, other):
        return isinstance(other, Part) and self.part_id == other.part_id

    def ereaseFromConveyor(self):
        program = self.programs[self.current_step]
        ejecutar_y_respaldar("""
                UPDATE conveyors SET status='EMPTY',part_id=NULL, part_num=NULL 
                WHERE conveyor=? AND hanger_num=? 
                """, (program.conveyor_start, program.hanger_num)) #(program.current_conveyor, program.current_hanger))

    def putInConveyor(self, conveyor, hanger):
        program = self.programs[self.current_step]
        self.ereaseFromConveyor()
        program.current_conveyor = conveyor
        program.current_hanger = hanger
        ejecutar_y_respaldar(
                "UPDATE conveyors SET part_id=?, part_num=?, status='FULL' WHERE hanger_num=? AND conveyor=?",
                (self.part_id, self.part_num, hanger, conveyor ) )

    def updateHistory(self):
        program = self.programs[self.current_step]
        #Update in history
        ejecutar_y_respaldar(
            """
            UPDATE history SET 
            program_id = ?, robot_num = ?, min_drying_time = ?,
            max_drying_time = ?, state = ?, start_date = ?,
            start_time = ?, end_date = ?, end_time = ?, run_time = ?,
            station = ?, hanger_id = ?, hanger_num = ?, hanger_end = ?,
            conveyor_start = ?, conveyor_end = ?, time_deviation = ?
            WHERE part_id=? and step=?
            """,
            ( program.program_id,
        program.robot_num, program.min_drying_time, program.max_drying_time, program.state,
        program.start_date, program.start_time, program.end_date,
        program.end_time, program.run_time, program.station, program.hanger_id,
        program.hanger_num, program.hanger_end, program.conveyor_start, program.conveyor_end, program.time_deviation, self.part_id, program.step)
        )

    def updatePartsHangers(self):
        program = self.programs[self.current_step]
        #Es self.current_step + 1 porque en la base de datos es de 1 a n y aqui es de 0 a n-1 por los arreglos
        ejecutar_y_respaldar(
                """
                UPDATE parts SET sequence_index=?, hanger_num=?, conveyor=?  WHERE part_id=?
                """, (self.current_step+1, program.current_hanger, program.current_conveyor, self.part_id)
            )

    def updateCurrentParts(self):
        program = self.programs[self.current_step]
        ejecutar_y_respaldar("""
        INSERT INTO currentParts(
            part_id, part_num, current_step, program_id,
            robot_num, min_drying_time, max_drying_time, state, 
            start_date, start_time, end_date, end_time, 
            run_time, station, hanger_id, hanger_num, 
            hanger_end, conveyor_start, conveyor_end, time_deviation,
            current_hanger, current_conveyor, order_id
        )  
        VALUES (?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?,
                ?, ?, ?)
        ON CONFLICT(part_id) DO UPDATE SET
            part_num = excluded.part_num,
            current_step = excluded.current_step,
            program_id = excluded.program_id,
            robot_num = excluded.robot_num,
            min_drying_time = excluded.min_drying_time,
            max_drying_time = excluded.max_drying_time,
            state = excluded.state,
            start_date = excluded.start_date,
            start_time = excluded.start_time,
            end_date = excluded.end_date,
            end_time = excluded.end_time,
            run_time = excluded.run_time,
            station = excluded.station,
            hanger_id = excluded.hanger_id,
            hanger_num = excluded.hanger_num,
            hanger_end = excluded.hanger_end,
            conveyor_start = excluded.conveyor_start,
            conveyor_end = excluded.conveyor_end,
            time_deviation = excluded.time_deviation,
            current_hanger = excluded.current_hanger,
            current_conveyor = excluded.current_conveyor,
            order_id = excluded.order_id
    """, (
        self.part_id, self.part_num, self.current_step+1, program.program_id,
        program.robot_num, program.min_drying_time, program.max_drying_time, program.state, 
        program.start_date, program.start_time, program.end_date, 
        program.end_time, program.run_time, program.station, program.hanger_id, 
        program.hanger_num, program.hanger_end, program.conveyor_start, program.conveyor_end, program.time_deviation,
        program.current_hanger, program.current_conveyor, program.order_id
    ))


    def updateAll(self):
        try:
            self.updateCurrentParts()
            self.updateHistory()
            self.updatePartsHangers()
        except Exception as e:
            print(f"ERROR IN PART CLASS: {e}")

    def getCurrentProgram(self):
        return self.programs[self.current_step]
    def endPart(self):
        ejecutar_y_respaldar ("""
        UPDATE parts SET status=0 WHERE part_id=?
        """, (self.part_id,))
        ejecutar_y_respaldar("""
        DELETE FROM currentParts WHERE part_id=?
        """, (self.part_id,))

        status = 0

    def setCurrentProgram(self, program:Program):
        if program in self.programs:
            self.current_step = program.step - 1
            ejecutar_y_respaldar("""
            UPDATE currentParts SET current_step=?, robot_num=?, min_drying_time=?, max_drying_time=?, state='READY',
            start_date=?, start_time=?, end_date=?, end_time=?, run_time=?, station=?, hanger_id=?, hanger_num=?, 
            hanger_end=?, conveyor_start=?, conveyor_end=?, time_deviation=?, program_id=?
            WHERE part_id=? 
            """, (program.step, program.robot_num, program.min_drying_time, program.max_drying_time,  
            program.start_date, program.start_time, program.end_date, program.end_time, program.run_time,
            program.station, program.hanger_id, program.hanger_num, 
            program.hanger_end, program.conveyor_start, program.conveyor_end, program.time_deviation,
            program.program_id, self.part_id))

            ejecutar_y_respaldar("""
            UPDATE parts SET sequence_index=? WHERE part_id=?
            """, (program.step, self.part_id))
            #print_sqlite_table("currentParts")
        else:
            print("ERROR: PROGRAM NOT FOUND IN PROGRAMS LIST")
            
    def updateTimeDeviation(self, timeDev):
        program = self.getCurrentProgram()
        program.time_deviation = timeDev
        ejecutar_y_respaldar("""
        UPDATE history SET time_deviation=? WHERE part_id=? AND step=?
        """, (timeDev, self.part_id, program.step))

    def init_part_in_history(self, part_id):
        #Inicializa toda la información de los programas de una secuencia
        #dentro de la tabla history por referencia cruzada entre todas las tablas
        #selecciona la ubicación e información de la parte
        part = selectFromDB("""
        SELECT part_num, start_date, start_time, hanger_id, hanger_num, conveyor, order_id FROM parts WHERE part_id=?
        """, (part_id, ))
        part = part[0]
        part_num, start_date, start_time, hanger_id, hanger_num, conveyor, order_id = part
        #Obtiene la secuencia en base al número de parte
        sequenceID = selectFromDB("""
            SELECT sequence_id FROM partNumbers WHERE part_num=?
            """, (part_num, ))
        sequenceID = sequenceID[0][0]
        #Obtiene cada programa de la secuencia
        programs = selectFromDB("""
            SELECT program_id, min_drying_time, max_drying_time, step FROM sequences WHERE sequence_id=? ORDER BY step
            """, (sequenceID, ))
        #Inicializa para conteo cada programa
        for i, (program_id, min_drying, max_drying, step) in enumerate(programs):
            values = selectFromDB("SELECT robot_num, conveyor_start, conveyor_end FROM programs WHERE program_id=?", (program_id, ))
            robot_num = values[0][0]
            conveyor_start = values[0][1]
            conveyor_end = values[0][2]
            ejecutar_y_respaldar("""
                INSERT INTO history (part_id, part_num, step,
                program_id, robot_num, min_drying_time, max_drying_time, conveyor_start, conveyor_end, order_id, upload_date) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (part_id, part_num, step, program_id, robot_num, 
            min_drying, max_drying, conveyor_start, conveyor_end, order_id, start_date) )
            if i == 0:
                ejecutar_y_respaldar("""
                UPDATE history SET conveyor_start = ?, hanger_num = ?, state = "READY" WHERE program_id = ? AND part_id = ?
                """, (conveyor, hanger_num, program_id, part_id))

    def init_current_part(self, hanger_num, conveyor):
        self.programs[self.current_step].current_hanger = hanger_num
        self.programs[self.current_step].current_conveyor = conveyor
        self.updateCurrentParts()

    def init_part_conveyor(self, part_id, hanger_num, conveyor, part_number, start_date, start_time, order_id):
        ejecutar_y_respaldar(
                """INSERT INTO parts (part_id, hanger_num, conveyor, part_num, start_date, start_time, sequence_index, order_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (part_id, hanger_num, conveyor, part_number, start_date, start_time, 1, order_id)
            )
        ejecutar_y_respaldar(
                "UPDATE conveyors SET part_id=?, part_num=?, order_id = ?, status='FULL' WHERE hanger_num=? AND conveyor=?",
                (part_id, part_number, order_id, hanger_num, conveyor)
            )
    
    def getInformation(self, part_id):
        part_num = selectFromDB("""
                SELECT part_num, sequence_index, hanger_num, conveyor FROM parts WHERE part_id=?
            """, (self.part_id,))
        if part_num:
            programs  = selectFromDB("""
            SELECT program_id, min_drying_time, max_drying_time, step, conveyor_start,
            hanger_num, state FROM history WHERE part_id=? ORDER BY step
            """, (self.part_id, ))
            self.part_num = part_num[0][0]
            if part_num[0][1] == 0:
                self.current_step = 0
            else:
                self.current_step = part_num[0][1] - 1
            self.hanger_num = part_num[0][2]
            self.conveyor = part_num[0][3]
            current_part = selectFromDB("""
            SELECT program_id, current_hanger, current_conveyor FROM currentParts WHERE part_id=?
            """, (self.part_id, ))
            self.programs = []
            for r, (programId, minTime, maxTime, step, conveyor, hanger_num, state) in enumerate(programs):
                # #TODO: Para reiniciar quita los argumentos, el sistema trackea por medio de estados.
                currentProgram = Program(programId, self.part_id, step)
                self.programs.append(currentProgram)
            
            if current_part and (current_part[0][0] == self.programs[self.current_step].program_id):
                self.programs[self.current_step].current_hanger = current_part[0][1]
                self.programs[self.current_step].current_conveyor = current_part[0][2]
            self.updateAll()
        else:
            print("ERROR: CAN NOT GET INFORMATION FOR THE PART")

    def deletePart(self, part_id, hanger_num, conveyor):
        #print(f"PART DELETE: {part_id} HANGER: {hanger_num}{conveyor}")
        ejecutar_y_respaldar(
                    "UPDATE conveyors SET part_id=NULL, part_num=NULL, status='EMPTY', order_id=NULL WHERE hanger_num=? AND conveyor=?",
                    (hanger_num, conveyor)
                )
        ejecutar_y_respaldar(
            "DELETE FROM parts WHERE part_id=?",
            (part_id,)
        )
        ejecutar_y_respaldar (
            "DELETE FROM currentParts where part_id=?", (part_id, )
        )
        fecha, hora = getDateTime()
        ejecutar_y_respaldar("""
        UPDATE history SET end_date=?, state='DONE' WHERE part_id=? and step=(SELECT MAX(step) FROM history WHERE part_id=?)
        """, (fecha, part_id, part_id))

    def deletePartHistory(self, part_id):
        ejecutar_y_respaldar (
            "DELETE FROM history where part_id=?", (part_id, )
        )