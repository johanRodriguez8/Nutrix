from db.connection import db


class PartNumbersRepository:
    def get_sequence_id(self, part_num):
        return db.query(
            "SELECT sequence_id FROM partNumbers WHERE part_num=?", (part_num,)
        )

    def list_all(self):
        return db.query("SELECT part_num, sequence_id FROM partNumbers")

    def list_all_ordered(self, ascending=True):
        order = "ASC" if ascending else "DESC"
        return db.query(
            f"SELECT part_num, sequence_id FROM partNumbers ORDER BY sequence_id {order}"
        )

    def all_part_nums(self):
        return db.query("SELECT part_num FROM partNumbers")

    def distinct_part_nums(self):
        return db.query("SELECT DISTINCT part_num FROM partNumbers ORDER BY part_num")

    def insert(self, part_num, sequence_id):
        db.execute(
            "INSERT INTO partNumbers (part_num, sequence_id) VALUES (?, ?)",
            (part_num, sequence_id),
        )

    def update(self, part_num, sequence_id, old_part_num):
        db.execute(
            "UPDATE partNumbers SET part_num=?, sequence_id=? WHERE part_num=?",
            (part_num, sequence_id, old_part_num),
        )

    def delete(self, part_num):
        db.execute("DELETE FROM partNumbers WHERE part_num=?", (part_num,))
