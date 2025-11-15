# test_setup.py
import requests, json

BASE = "http://127.0.0.1:8000"

data = [
    ("/faculty/add", {
        "name":"Prof. A",
        "email":"a@college.com",
        "department":"CSE",
        "max_weekly_load":10,
        "subjects_can_teach":["CS101"],
        "available_slots":[1,2,3,4,5,6],
        "password":"pass123"
    }),
    ("/faculty/add", {
        "name":"Prof. B",
        "email":"b@college.com",
        "department":"CSE",
        "max_weekly_load":10,
        "subjects_can_teach":["CS102"],
        "available_slots":[1,2,3,4,5,6],
        "password":"pass123"
    }),
    ("/subject/add", {
        "name":"Data Structures",
        "code":"CS101",
        "department":"CSE",
        "weekly_sessions":2,
        "duration_minutes":60,
        "faculty_ids":[]
    }),
    ("/subject/add", {
        "name":"Algorithms",
        "code":"CS102",
        "department":"CSE",
        "weekly_sessions":2,
        "duration_minutes":60,
        "faculty_ids":[]
    }),
    ("/room/add", {
        "name":"Room 101",
        "capacity":80,
        "room_type":"CLASSROOM"
    }),
    ("/batch/add", {
        "name":"CSE-A",
        "year":2024,
        "department":"CSE", 
        "semester": 3,
        "student_count":60,
        "subjects": ["CS101", "CS102"]

    }),
]

for endpoint, payload in data:
    r = requests.post(BASE + endpoint, json=payload)
    print(endpoint, r.status_code, r.text)

print("\nCalling scheduler...")
r = requests.post(BASE + "/schedule/generate", json={})
print("SCHEDULE:", r.status_code)
print(r.text)
