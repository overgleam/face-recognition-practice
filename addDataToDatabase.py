import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://face-recognition-practic-8837b-default-rtdb.asia-southeast1.firebasedatabase.app/'})

ref = db.reference('Students')

data = {
    "123456" : {
        "name" : "Joseph Alforque",
        "major" : "Computer Science",
        "start_year" : 2002,
        "total_attendance" : 6,
        "standing" : "G",
        "year" : 4,
        "last_attendance_time": "2024-12-11 02:16:44"
    },
    "789101" : {
        "name" : "Elon Musk",
        "major" : "Computer Science",
        "start_year" : 2003,
        "total_attendance" : 1,
        "standing" : "G",
        "year" : 3,
        "last_attendance_time": "2024-12-11 02:16:44"
    },
    "112141" : {
        "name" : "Jhanela Dalut",
        "major" : "Marketing Management",
        "start_year" : 2004,
        "total_attendance" : 3,
        "standing" : "G",
        "year" : 2,
        "last_attendance_time": "2024-12-11 02:16:44"
    }, 
     "516178" : {
        "name" : "Mark Zuckerberg",
        "major" : "Computer Science",
        "start_year" : 2005,
        "total_attendance" : 3,
        "standing" : "G",
        "year" : 1,
        "last_attendance_time": "2024-12-11 02:16:44"
    }
}


for key, value in data.items():
    ref.child(key).set(value)