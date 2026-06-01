from utils.helpers import getDateTime
from db.part_tracking.program import Program
from db.repositories import (
    parts_repo, conveyors_repo, current_parts_repo,
    history_repo, part_numbers_repo, sequences_repo, programs_repo,
)
class Part():
    def __init__(self, part_id=None, hanger_num=None, conveyor=None, part_num=None, start_date=None, start_time=None, order_id=None):
        self.part_id = part_id
        self.part_num = part_num
        self.current_step = 0
        self.programs = []
        self.hanger_num = hanger_num
        self.conveyor = conveyor
        self.status = 1
        if part_id:
            if parts_repo.exists(self.part_id):
                self.getInformation(part_id)
            else:
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
        conveyors_repo.free_by_program(program.conveyor_start, program.hanger_num)

    def putInConveyor(self, conveyor, hanger):
        program = self.programs[self.current_step]
        self.ereaseFromConveyor()
        program.current_conveyor = conveyor
        program.current_hanger = hanger
        conveyors_repo.fill(self.part_id, self.part_num, hanger, conveyor)

    def updateHistory(self):
        program = self.programs[self.current_step]
        history_repo.update_step((
            program.program_id, program.robot_num, program.min_drying_time,
            program.max_drying_time, program.state, program.start_date,
            program.start_time, program.end_date, program.end_time, program.run_time,
            program.station, program.hanger_id, program.hanger_num, program.hanger_end,
            program.conveyor_start, program.conveyor_end, program.time_deviation,
            self.part_id, program.step,
        ))

    def updatePartsHangers(self):
        program = self.programs[self.current_step]
        #Es self.current_step + 1 porque en la base de datos es de 1 a n y aqui es de 0 a n-1 por los arreglos
        parts_repo.update_hangers(
            self.current_step + 1, program.current_hanger, program.current_conveyor, self.part_id
        )

    def updateCurrentParts(self):
        program = self.programs[self.current_step]
        current_parts_repo.upsert((
            self.part_id, self.part_num, self.current_step + 1, program.program_id,
            program.robot_num, program.min_drying_time, program.max_drying_time, program.state,
            program.start_date, program.start_time, program.end_date,
            program.end_time, program.run_time, program.station, program.hanger_id,
            program.hanger_num, program.hanger_end, program.conveyor_start, program.conveyor_end, program.time_deviation,
            program.current_hanger, program.current_conveyor, program.order_id,
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
        parts_repo.set_inactive(self.part_id)
        current_parts_repo.delete(self.part_id)

        status = 0

    def setCurrentProgram(self, program:Program):
        if program in self.programs:
            self.current_step = program.step - 1
            current_parts_repo.update_current_program((
                program.step, program.robot_num, program.min_drying_time, program.max_drying_time,
                program.start_date, program.start_time, program.end_date, program.end_time, program.run_time,
                program.station, program.hanger_id, program.hanger_num,
                program.hanger_end, program.conveyor_start, program.conveyor_end, program.time_deviation,
                program.program_id, self.part_id,
            ))
            parts_repo.set_sequence_index(program.step, self.part_id)
        else:
            print("ERROR: PROGRAM NOT FOUND IN PROGRAMS LIST")

    def updateTimeDeviation(self, timeDev):
        program = self.getCurrentProgram()
        program.time_deviation = timeDev
        history_repo.set_time_deviation(timeDev, self.part_id, program.step)

    def init_part_in_history(self, part_id):
        #Inicializa toda la información de los programas de una secuencia
        #dentro de la tabla history por referencia cruzada entre todas las tablas
        #selecciona la ubicación e información de la parte
        part = parts_repo.get_history_init_info(part_id)
        part = part[0]
        part_num, start_date, start_time, hanger_id, hanger_num, conveyor, order_id = part
        #Obtiene la secuencia en base al número de parte
        sequenceID = part_numbers_repo.get_sequence_id(part_num)
        sequenceID = sequenceID[0][0]
        #Obtiene cada programa de la secuencia
        programs = sequences_repo.get_programs(sequenceID)
        #Inicializa para conteo cada programa
        for i, (program_id, min_drying, max_drying, step) in enumerate(programs):
            values = programs_repo.get_robot_and_conveyors(program_id)
            robot_num = values[0][0]
            conveyor_start = values[0][1]
            conveyor_end = values[0][2]
            history_repo.insert_step(
                part_id, part_num, step, program_id, robot_num,
                min_drying, max_drying, conveyor_start, conveyor_end, order_id, start_date,
            )
            if i == 0:
                history_repo.set_first_step_ready(conveyor, hanger_num, program_id, part_id)

    def init_current_part(self, hanger_num, conveyor):
        self.programs[self.current_step].current_hanger = hanger_num
        self.programs[self.current_step].current_conveyor = conveyor
        self.updateCurrentParts()

    def init_part_conveyor(self, part_id, hanger_num, conveyor, part_number, start_date, start_time, order_id):
        parts_repo.insert(part_id, hanger_num, conveyor, part_number, start_date, start_time, 1, order_id)
        conveyors_repo.fill_with_order(part_id, part_number, order_id, hanger_num, conveyor)

    def getInformation(self, part_id):
        part_num = parts_repo.get_information(self.part_id)
        if part_num:
            programs = history_repo.get_programs_for_part(self.part_id)
            self.part_num = part_num[0][0]
            if part_num[0][1] == 0:
                self.current_step = 0
            else:
                self.current_step = part_num[0][1] - 1
            self.hanger_num = part_num[0][2]
            self.conveyor = part_num[0][3]
            current_part = current_parts_repo.get_program_location(self.part_id)
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
        conveyors_repo.clear(hanger_num, conveyor)
        parts_repo.delete(part_id)
        current_parts_repo.delete(part_id)
        fecha, hora = getDateTime()
        history_repo.mark_last_step_done(fecha, part_id)

    def deletePartHistory(self, part_id):
        history_repo.delete(part_id)
