import requests, random, json, time

BASE = "http://127.0.0.1:8000"
headers = {"Content-Type": "application/json"}

def post(url, data):
    r = requests.post(BASE + url, json=data)
    print(url, r.status_code)
    try: print(r.json())
    except: print(r.text)
    return r

# ----------------------------------------------------------------------
# 1️⃣ Generate Faculties (40)
# ----------------------------------------------------------------------
faculty_ids = []
for i in range(40):
    fac = {
        "name": f"Faculty_{i}",
        "email": f"faculty{i}@college.com",
        "department": "CSE",
        "max_weekly_load": random.randint(8, 16),
        "subjects_can_teach": [],
        "available_slots": list(range(1, 40)),
        "password": "pass123"
    }
    r = post("/faculty/add", fac)
    if r.status_code == 200:
        faculty_ids.append(r.json()["id"])

# ----------------------------------------------------------------------
# 2️⃣ Generate Subjects (20)
# ----------------------------------------------------------------------
subject_codes = []
subjects = []
for i in range(20):
    code = f"SUB{i:03d}"
    subject_codes.append(code)
    sub = {
        "name": f"Subject_{i}",
        "code": code,
        "department": "CSE",
        "weekly_sessions": random.randint(3, 4),
        "duration_minutes": random.choice([60, 60, 60, 90, 120])
    }
    r = post("/subject/add", sub)
    if r.status_code == 200:
        subjects.append(r.json())

# ----------------------------------------------------------------------
# 2B️⃣ Ensure EVERY subject has at least one faculty assigned
# ----------------------------------------------------------------------
valid_subject_codes = [s["code"] for s in subjects]
subject_to_faculties = {code: [] for code in valid_subject_codes}

# First pass (random)
for fid in faculty_ids:
    teachable = random.sample(valid_subject_codes, random.randint(1, 3))
    for sc in teachable:
        subject_to_faculties[sc].append(fid)

# Second pass (guarantee at least 1 faculty per subject)
for sc in valid_subject_codes:
    if len(subject_to_faculties[sc]) == 0:
        subject_to_faculties[sc].append(random.choice(faculty_ids))

# Update each faculty in DB with final teaching list
for fid in faculty_ids:
    teaches = [sc for sc, facs in subject_to_faculties.items() if fid in facs]
    requests.put(BASE + f"/faculty/update/{fid}",
                 json={"subjects_can_teach": teaches})

# ----------------------------------------------------------------------
# 4️⃣ Create 15 Rooms
# ----------------------------------------------------------------------
for i in range(15):
    room = {
        "name": f"Room_{i}",
        "capacity": random.randint(60, 120),
        "room_type": "CLASSROOM"
    }
    post("/room/add", room)

# ----------------------------------------------------------------------
# 5️⃣ Create 10 Batches (~1000 total students)
#     Each batch gets 4–6 subjects (different sets)
# ----------------------------------------------------------------------
for i in range(10):
    batch = {
        "name": f"BATCH_{i}",
        "year": 2024,
        "department": "CSE",
        "semester": random.randint(1, 8),
        "student_count": random.randint(80, 120),
        "subjects": random.sample(subject_codes, random.randint(4, 6))
    }
    post("/batch/add", batch)

# ----------------------------------------------------------------------
# 6️⃣ CALL SCHEDULER
# ----------------------------------------------------------------------
print("\n🚀 RUNNING TIMETABLE GENERATOR...")
start = time.time()
res = requests.post(BASE + "/schedule/generate", json={})
end = time.time()

print("\n⏱ Solver Time:", end - start, "seconds")
print("📘 Result Code:", res.status_code)

try:
    print(json.dumps(res.json(), indent=2))
except:
    print(res.text)
