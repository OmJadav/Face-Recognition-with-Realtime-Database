import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendance-a4fe5-default-rtdb.firebaseio.com/"
})

ref=db.reference('Students')

data={
    "312654":
        {
            "name":"Mukesh Ambani",
            "branch":"Chuno lagao",
            "roll":312654,
            "batch":2021,
            "total_attendance":10,
            "last_attendance_time":"2025-02-11 08:16:00",
        },
    "852741":
        {
            "name": "Mark Zuckerburg",
            "branch":"Time pass",
            "roll":852741,
            "batch": 2021,
            "total_attendance": 12,
            "last_attendance_time": "2025-02-11 08:34:23"
        },
    "963852":
        {
            "name": "Elon Musk",
            "branch": "Time pass",
            "roll": 963852,
            "batch": 2021,
            "total_attendance": 5,
            "last_attendance_time": "2025-02-11 08:49:23"
        }

}

for key,value in data.items():
    ref.child(key).set(value)