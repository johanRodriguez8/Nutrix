from db.connection import db


class ProgramsRepository:
    def get_path_and_conveyors(self, program_id):
        return db.query(
            "SELECT path, conveyor_start, conveyor_end FROM programs WHERE program_id=?",
            (program_id,),
        )

    def get_robot_and_conveyors(self, program_id):
        return db.query(
            "SELECT robot_num, conveyor_start, conveyor_end FROM programs WHERE program_id=?",
            (program_id,),
        )

    def get_robot(self, program_id):
        return db.query(
            "SELECT robot_num FROM programs WHERE program_id=?", (program_id,)
        )

    def get_basic(self, program_id):
        return db.query(
            "SELECT program_id, path, robot_num FROM programs WHERE program_id=?",
            (program_id,),
        )

    def list_all(self, ascending=True):
        order = "ASC" if ascending else "DESC"
        return db.query(
            "SELECT program_id, path, robot_num, conveyor_start, conveyor_end "
            f"FROM programs ORDER BY program_id {order}"
        )

    def all_ids(self):
        return db.query("SELECT program_id FROM programs ORDER BY program_id")

    def insert(self, program_id, path, robot_num):
        db.execute(
            "INSERT INTO programs (program_id, path, robot_num) VALUES (?, ?, ?)",
            (program_id, path, robot_num),
        )

    def update_basic(self, new_program_id, path, robot_num, program_id):
        db.execute(
            "UPDATE programs SET program_id = ?, path = ?, robot_num = ? WHERE program_id=?",
            (new_program_id, path, robot_num, program_id),
        )

    def upsert_full(self, program_id, path, robot_num, conveyor_start, conveyor_end):
        db.execute(
            "INSERT OR REPLACE INTO programs "
            "(program_id, path, robot_num, conveyor_start, conveyor_end) "
            "VALUES (?,?,?,?,?)",
            (program_id, path, robot_num, conveyor_start, conveyor_end),
        )

    def delete(self, program_id):
        db.execute("DELETE FROM programs WHERE program_id=?", (program_id,))
