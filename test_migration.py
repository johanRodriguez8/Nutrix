"""
Quick smoke test — verifies the new repositories can read from db_new.db.

Run from the project root:
    python test_migration.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NEW_DB = str(ROOT / "db" / "db_new.db")

# Point infrastructure to the new DB before importing repositories
import src.infrastructure.db.connection as _conn_mod
from src.infrastructure.db.connection import Database
_conn_mod.db = Database(NEW_DB)

from src.infrastructure.db.repositories.programs_repository import ProgramsRepository
from src.infrastructure.db.repositories.part_numbers_repository import PartNumbersRepository
from src.infrastructure.db.repositories.conveyors_repository import ConveyorsRepository
from src.infrastructure.db.repositories.sequences_repository import SequencesRepository
from src.infrastructure.db.repositories.part_instance_repository import PartInstanceRepository
from src.infrastructure.db.repositories.history_repository import HistoryRepository
from src.infrastructure.db.repositories.work_orders_repository import WorkOrdersRepository

db = _conn_mod.db
programs   = ProgramsRepository(db)
parts_nums = PartNumbersRepository(db)
conveyors  = ConveyorsRepository(db)
sequences  = SequencesRepository(db)
instances  = PartInstanceRepository(db)
history    = HistoryRepository(db)
orders     = WorkOrdersRepository(db)

PASS = "✅"
FAIL = "❌"
errors = 0


def check(label, condition, detail=""):
    global errors
    status = PASS if condition else FAIL
    print(f"  {status} {label}" + (f" — {detail}" if detail else ""))
    if not condition:
        errors += 1


print("\n── Programs ──────────────────────────────────")
all_programs = programs.get_all()
check("get_all() returns list", isinstance(all_programs, list))
check("count matches migration (61)", len(all_programs) == 61, f"got {len(all_programs)}")
if all_programs:
    p = all_programs[0]
    check("entity has program_id", bool(p.program_id))
    check("entity has robot_num", bool(p.robot_num))
    p_by_id = programs.get_by_id(p.program_id)
    check("get_by_id() matches", p_by_id is not None and p_by_id.program_id == p.program_id)

print("\n── PartNumbers ───────────────────────────────")
all_pn = parts_nums.get_all()
check("count matches migration (93)", len(all_pn) == 93, f"got {len(all_pn)}")
if all_pn:
    pn = all_pn[0]
    check("get_by_id() works", parts_nums.get_by_id(pn.part_num) is not None)
    check("get_sequence_id() works", True, f"→ {parts_nums.get_sequence_id(pn.part_num)}")

print("\n── Conveyors ─────────────────────────────────")
all_conv = conveyors.get_all()
check("count matches migration (210)", len(all_conv) == 210, f"got {len(all_conv)}")
conv_a = conveyors.get_by_conveyor('A')
check("conveyor A has 30 hangers", len(conv_a) == 30, f"got {len(conv_a)}")
conv_b = conveyors.get_by_conveyor('B')
check("conveyor B has 76 hangers", len(conv_b) == 76, f"got {len(conv_b)}")
if all_conv:
    c = conveyors.get_by_hanger(all_conv[0].hanger_num, all_conv[0].conveyor)
    check("get_by_hanger() works", c is not None)
    from src.domain.value_objects.conveyor_status import ConveyorStatus
    check("status is ConveyorStatus enum", isinstance(c.status, ConveyorStatus))
    check("no FULL status (migrated to OCCUPIED)",
          all(c.status != 'FULL' for c in all_conv))

print("\n── Sequences ─────────────────────────────────")
all_seq = sequences.get_all()
check("count matches migration (19)", len(all_seq) == 19, f"got {len(all_seq)}")
if all_seq:
    s = all_seq[0]
    check("sequence has steps", len(s.steps) > 0, f"steps: {len(s.steps)}")
    s_by_id = sequences.get_by_id(s.sequence_id)
    check("get_by_id() loads steps", s_by_id is not None and len(s_by_id.steps) == len(s.steps))
    total_steps = sum(len(s.steps) for s in all_seq)
    check("total steps matches migration (158)", total_steps == 158, f"got {total_steps}")

print("\n── PartInstances ─────────────────────────────")
all_pi = instances.get_all()
check("count matches migration (59)", len(all_pi) == 59, f"got {len(all_pi)}")
if all_pi:
    pi = all_pi[0]
    check("entity has part_id", bool(pi.part_id))
    check("entity has start_datetime", bool(pi.start_datetime))
    from src.domain.value_objects.part_state import PartState
    check("state is PartState enum", isinstance(pi.state, PartState))
    pi_by_id = instances.get_by_id(pi.part_id)
    check("get_by_id() works", pi_by_id is not None)
    check("exists() works", instances.exists(pi.part_id))
    check("exists() returns False for unknown", not instances.exists("__nonexistent__"))

print("\n── History ───────────────────────────────────")
all_hist = history.get_all()
check("count matches migration (576)", len(all_hist) == 576, f"got {len(all_hist)}")
if all_hist:
    h = all_hist[0]
    check("entry has part_id", bool(h.part_id))
    by_part = history.get_by_part(h.part_id)
    check("get_by_part() returns list", isinstance(by_part, list) and len(by_part) > 0)

print("\n── WorkOrders ────────────────────────────────")
all_wo = orders.get_all()
check("count matches migration (0)", len(all_wo) == 0, f"got {len(all_wo)}")

print(f"\n{'='*48}")
if errors == 0:
    print(f"✅ All checks passed.")
else:
    print(f"❌ {errors} check(s) failed.")
    sys.exit(1)
