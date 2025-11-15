# backend/app/services/scheduler.py
from ortools.sat.python import cp_model
from datetime import datetime, timedelta

# convert slot number to readable time
def slot_to_time(slot, slots_per_day=8):
    # slot 0 => day0 slot0 => Monday 08:00
    base = datetime(2024, 1, 1, 8, 0)
    day = slot // slots_per_day
    hour = slot % slots_per_day
    return base + timedelta(days=day, hours=hour)


async def generate_schedule(subjects, faculties, rooms, batches):
    """
    subjects: list of subject dicts (each must have 'code','name','weekly_sessions','duration_minutes')
    faculties: list of faculty dicts (each must have '_id','name','subjects_can_teach' (list of codes), 'available_slots' (list of ints))
    rooms: list of room dicts (each must have '_id','name','capacity')
    batches: list of batch dicts (each must have 'name','student_count','subject_ids' (list of subject codes))
    """

    # basic sanity checks
    if not subjects or not faculties or not rooms or not batches:
        return {"status": "fail", "message": "Missing data (subjects/faculty/rooms/batches)"}

    DAYS = 5
    SLOTS_PER_DAY = 8
    TOTAL_SLOTS = DAYS * SLOTS_PER_DAY

    model = cp_model.CpModel()

    # index maps
    fac_count = len(faculties)
    room_count = len(rooms)

    # Build sessions: one session instance per subject per weekly session
    sessions = []
    for subj in subjects:
        weekly = int(subj.get("weekly_sessions", 1))
        for s in range(weekly):
            sessions.append({
                "id": f"{str(subj.get('_id'))}_{s}",
                "subject": subj,
                "faculty_var": model.NewIntVar(0, fac_count - 1, f"fac_{subj.get('code')}_{s}"),
                "room_var": model.NewIntVar(0, room_count - 1, f"room_{subj.get('code')}_{s}"),
                "slot_var": model.NewIntVar(0, TOTAL_SLOTS - 1, f"slot_{subj.get('code')}_{s}")
            })

    # Precompute useful mappings:
    # faculty index => its available slots set
    fac_available = []
    fac_teaches_codes = []
    for f in faculties:
        fac_available.append(set(f.get("available_slots", list(range(TOTAL_SLOTS)))))
        fac_teaches_codes.append(set(f.get("subjects_can_teach", [])))

    # For each subject, compute required max batch size (max students among batches that have that subject)
    subj_required_size = {}
    for subj in subjects:
        code = subj.get("code")
        sizes = [b.get("student_count", 0) for b in batches if code in b.get("subject_ids", [])]
        subj_required_size[code] = max(sizes) if sizes else 0

    # Build boolean helper vars for faculty equality and room equality
    # b_fac[i][f] is true iff sessions[i].faculty_var == f
    b_fac = []
    for i, ses in enumerate(sessions):
        row = []
        for f_idx in range(fac_count):
            b = model.NewBoolVar(f"ses{i}_is_fac{f_idx}")
            # link boolean to equality
            model.Add(ses["faculty_var"] == f_idx).OnlyEnforceIf(b)
            model.Add(ses["faculty_var"] != f_idx).OnlyEnforceIf(b.Not())
            row.append(b)
        b_fac.append(row)

    b_room = []
    for i, ses in enumerate(sessions):
        row = []
        for r_idx in range(room_count):
            b = model.NewBoolVar(f"ses{i}_is_room{r_idx}")
            model.Add(ses["room_var"] == r_idx).OnlyEnforceIf(b)
            model.Add(ses["room_var"] != r_idx).OnlyEnforceIf(b.Not())
            row.append(b)
        b_room.append(row)

    # ----------------------------
    # HARD CONSTRAINTS
    # ----------------------------

    # 1) Faculty eligibility + availability
    # We'll constrain (faculty, slot) pairs to allowed pairs for each session based on subject code
    for i, ses in enumerate(sessions):
        subj_code = ses["subject"].get("code")
        allowed_pairs = []
        for f_idx, f in enumerate(faculties):
            # faculty must be able to teach this subject code
            if subj_code in fac_teaches_codes[f_idx]:
                # and faculty must have some available slots
                for slot in fac_available[f_idx]:
                    if 0 <= slot < TOTAL_SLOTS:
                        allowed_pairs.append((f_idx, slot))
        if not allowed_pairs:
            return {"status": "fail", "message": f"No available faculty/slot for subject {subj_code}"}
        # Add allowed pairs constraint on (faculty_var, slot_var)
        model.AddAllowedAssignments([ses["faculty_var"], ses["slot_var"]], allowed_pairs)

    # 2) Room capacity restriction (room chosen must be large enough)
    for i, ses in enumerate(sessions):
        subj_code = ses["subject"].get("code")
        required_size = subj_required_size.get(subj_code, 0)
        if required_size == 0:
            # if no batch includes this subject, allow any room
            continue
        allowed_rooms = [r_idx for r_idx, r in enumerate(rooms) if r.get("capacity", 0) >= required_size]
        if not allowed_rooms:
            return {"status": "fail", "message": f"No room with capacity for subject {subj_code} (required {required_size})"}
        model.AddAllowedAssignments([ses["room_var"]], [[r] for r in allowed_rooms])

    # 3) Prevent faculty double booking:
    # For each pair of sessions and each faculty, if both sessions assigned to same faculty -> slots must differ
    n = len(sessions)
    for i in range(n):
        for j in range(i + 1, n):
            for f_idx in range(fac_count):
                # If both b_fac[i][f_idx] and b_fac[j][f_idx] are true -> enforce slot_i != slot_j
                model.Add(sessions[i]["slot_var"] != sessions[j]["slot_var"]).OnlyEnforceIf([b_fac[i][f_idx], b_fac[j][f_idx]])

    # 4) Prevent room double booking:
    for i in range(n):
        for j in range(i + 1, n):
            for r_idx in range(room_count):
                model.Add(sessions[i]["slot_var"] != sessions[j]["slot_var"]).OnlyEnforceIf([b_room[i][r_idx], b_room[j][r_idx]])

    # 5) Batch-level constraint: for each batch, sessions for subjects that that batch takes must not overlap
    for batch in batches:
        subj_codes = set(batch.get("subject_ids", []))
        # collect indices of sessions that are for subjects in this batch
        idxs = [idx for idx, ses in enumerate(sessions) if ses["subject"].get("code") in subj_codes]
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                i = idxs[a]
                j = idxs[b]
                model.Add(sessions[i]["slot_var"] != sessions[j]["slot_var"])

    # 6) (Optional) Faculty max weekly load - ensure a faculty is not assigned more than max_weekly_load sessions
    # We'll compute number of sessions assigned per faculty and bound it
    for f_idx, f in enumerate(faculties):
        max_load = int(f.get("max_weekly_load", len(sessions)))
        # sum of b_fac[i][f_idx] across i <= max_load
        model.Add(sum(b_fac[i][f_idx] for i in range(n)) <= max_load)

    # ----------------------------
    # No objective (just find any feasible schedule quickly)
    # ----------------------------

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 15
    solver.parameters.num_search_workers = 8

    result = solver.Solve(model)

    if result not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": "fail", "message": "No valid schedule found"}
    
        # ----------------------------
    # STRONG CONSTRAINTS (robust)
    # ----------------------------
    n = len(sessions)

    # Create booleans that indicate whether two sessions are in the same slot
    same_slot = {}
    for i in range(n):
        for j in range(i + 1, n):
            b = model.NewBoolVar(f"same_slot_{i}_{j}")
            # Link b ⇔ (slot_i == slot_j)
            model.Add(sessions[i]["slot_var"] == sessions[j]["slot_var"]).OnlyEnforceIf(b)
            model.Add(sessions[i]["slot_var"] != sessions[j]["slot_var"]).OnlyEnforceIf(b.Not())
            same_slot[(i, j)] = b

    # Prevent faculty double-booking robustly:
    # If two sessions are assigned the same slot AND the same faculty -> forbidden
    for i in range(n):
        for j in range(i + 1, n):
            sslot = same_slot[(i, j)]
            # For each faculty index, if both sessions are assigned to that faculty and same slot -> forbidden
            for f_idx in range(fac_count):
                # If both b_fac[i][f_idx] and b_fac[j][f_idx] are true and same_slot -> this combination is invalid.
                # Enforce: NOT( b_fac[i][f_idx] AND b_fac[j][f_idx] AND sslot )
                # Equivalent: enforce slot_i != slot_j when both b_fac are true (we already have similar), but explicitly:
                model.AddBoolOr([
                    b_fac[i][f_idx].Not(),
                    b_fac[j][f_idx].Not(),
                    sslot.Not()
                ])

    # Prevent room double-booking robustly:
    for i in range(n):
        for j in range(i + 1, n):
            sslot = same_slot[(i, j)]
            for r_idx in range(room_count):
                model.AddBoolOr([
                    b_room[i][r_idx].Not(),
                    b_room[j][r_idx].Not(),
                    sslot.Not()
                ])


    # Build output
    output = []
    for ses in sessions:
        slot = solver.Value(ses["slot_var"])
        fac_idx = solver.Value(ses["faculty_var"])
        room_idx = solver.Value(ses["room_var"])

        output.append({
            "id": ses["id"],
            "subject": ses["subject"].get("name"),
            "subject_code": ses["subject"].get("code"),
            "faculty": faculties[fac_idx].get("name"),
            "room": rooms[room_idx].get("name"),
            "slot": slot,
            "start": slot_to_time(slot, SLOTS_PER_DAY).strftime("%Y-%m-%d %H:%M:%S"),
            "end": (slot_to_time(slot, SLOTS_PER_DAY) + timedelta(minutes=int(ses["subject"].get("duration_minutes", 60)))).strftime("%Y-%m-%d %H:%M:%S")
        })

    return {"status": "success", "schedule": output}


