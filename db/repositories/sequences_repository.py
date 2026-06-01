from db.connection import db


class SequencesRepository:
    def distinct_ids(self):
        return db.query("SELECT DISTINCT sequence_id FROM sequences ORDER BY sequence_id")

    def get_programs(self, sequence_id):
        return db.query(
            "SELECT program_id, min_drying_time, max_drying_time, step "
            "FROM sequences WHERE sequence_id=? ORDER BY step",
            (sequence_id,),
        )

    def insert(self, sequence_id, program_id, min_drying_time, max_drying_time, step):
        db.execute(
            "INSERT INTO sequences (sequence_id, program_id, min_drying_time, max_drying_time, step) "
            "VALUES (?, ?, ?, ?, ?)",
            (sequence_id, program_id, min_drying_time, max_drying_time, step),
        )

    def delete(self, sequence_id):
        db.execute("DELETE FROM sequences WHERE sequence_id=?", (sequence_id,))
