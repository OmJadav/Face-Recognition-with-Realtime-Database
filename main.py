import os
import pickle
import cvzone
import cv2
import face_recognition
import numpy as np
import requests
import time
from EncodeGenerator import encodeListKnownWithIds
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://faceattendance-a4fe5-default-rtdb.firebaseio.com/"
    })

# Set up webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load background image
imgBackground = cv2.imread('Resources/background.png')

# Load mode images
folderModePath = 'Resources/Modes'
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in os.listdir(folderModePath)]

# Load encodings
print("Loading Encode File...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encodes File Loaded.")

# Variables
modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()
    if not success:
        print("Failed to read from webcam")
        continue

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img

    if imgModeList:
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                print("Known face detected")
                y1, x2, y2, x1 = [val * 4 for val in faceLoc]
                bbox = (55 + x1, 162 + y1, x2 - x1, y2 - y1)
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading...", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                if studentInfo:
                    image_url = studentInfo.get("image_url")
                    if image_url:
                        try:
                            response = requests.get(image_url, timeout=5)
                            if response.status_code == 200:
                                array = np.frombuffer(response.content, np.uint8)
                                imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                                imgStudent = cv2.resize(imgStudent, (216, 216))
                            else:
                                print(f"Failed to load image for {id}, HTTP {response.status_code}")
                        except requests.exceptions.RequestException as e:
                            print(f"Error fetching image: {e}")

                # Update attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondElapsed = (datetime.now() - datetimeObject).total_seconds()

                if secondElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                mode1_start_time = time.time()

            if modeType == 2 and (time.time() - mode1_start_time) > 5:
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            elif modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['branch']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['roll']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['batch']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)
                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, studentInfo['name'], (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (50, 50, 50), 1)
                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

            counter += 1
            if counter >= 20:
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    cv2.imshow("Face Attendance", imgBackground)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break