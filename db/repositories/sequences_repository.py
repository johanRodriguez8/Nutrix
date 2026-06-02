from db.repositories.base_repository import BaseRepository


class SequencesRepository(BaseRepository):
    def distinct_ids(self):
        return self._db.query("SELECT DISTINCT sequence_id FROM sequences ORDER BY sequence_id")

    def get_programs(self, sequence_id):
        return self._db.query(
            "SELECT program_id, min_drying_time, max_drying_time, step "
            "FROM sequences WHERE sequence_id=? ORDER BY step",
            (sequence_id,),
        )

    def insert(self, sequence_id, program_id, min_drying_time, max_drying_time, step):
        self._db.execute(
            "INSERT INTO sequences (sequence_id, program_id, min_drying_time, max_drying_time, step) "
            "VALUES (?, ?, ?, ?, ?)",
            (sequence_id, program_id, min_drying_time, max_drying_time, step),
        )

    def delete(self, sequence_id):
        self._db.execute("DELETE FROM sequences WHERE sequence_id=?", (sequence_id,))
