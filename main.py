import os
import cv2
import pickle
import face_recognition
import numpy as np
import cvzone
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'databaseURL':'https://face-recognition-practic-8837b-default-rtdb.asia-southeast1.firebasedatabase.app/','storageBucket': 'face-recognition-practic-8837b.appspot.com'})

bucket = storage.bucket()

folder_modes_path = "./Resources/Modes" # Define the path to the folder containing different modes
mode_path_list = os.listdir(folder_modes_path) # List all files in the specified folder
img_mode_list = [] # Initialize a list to store images of different modes

for path in mode_path_list: # Loop through each file path in the list of mode paths
    img_mode_list.append(cv2.imread(os.path.join(folder_modes_path, path))) # Read the image from the path and append to the list

cap = cv2.VideoCapture(0) # Initialize the camera capture object with the first camera device
cap.set(3, 640) # Set the width of the frames in the video stream to 640 pixels
cap.set(4, 480) # Set the height of the frames in the video stream to 480 pixels

image_background = cv2.imread("Resources/background.png") # Load a background image from the specified path

file = open('EncodeFile.pkl','rb') # Open the file containing encoded face data in read-binary mode
encodeListKnownWithIds = pickle.load(file) # Load the encoded face data and associated student IDs from the file
file.close() # Close the file after reading
encodeListKnown, studentIds = encodeListKnownWithIds # Unpack the loaded data into known encodings and student IDs
# print(studentIds) # Print the list of student IDs

modeType = 0 
counter = 0
id = -1
imgStudent = []

while True:
    ret, img = cap.read()  # Read a frame from the video capture
    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25) # Resize the captured image for faster processing
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB) # Convert the resized image from BGR to RGB color space as required by face_recognition

    faceCurrentFrame = face_recognition.face_locations(imgS) # Detect all face locations in the image
    encodeCurrentFrame = face_recognition.face_encodings(imgS, faceCurrentFrame) # Encode the faces found in the current frame


    image_background[162:162+480, 55:55+640] = img # Overlay the captured image onto the background image at specified coordinates
    image_background[44:44+633, 808:808+414] = img_mode_list[modeType] # Overlay the first mode image onto the background image at specified coordinates

    if faceCurrentFrame:
        
        for encodeFace, faceLoc in zip(encodeCurrentFrame, faceCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("Matches", matches)
            # print("Face Distance", faceDistance)

            matchIndex = np.argmin(faceDistance) # Find the index of the face with the smallest distance
            
            if matches[matchIndex]:
                # print(studentIds[matchIndex], " is Detected")q
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                image_background = cvzone.cornerRect(image_background, bbox, rt=0)
                id = studentIds[matchIndex]
            
                if counter == 0:
                    modeType = 1
                    counter = 1

        if counter != 0:

            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                # print(studentInfo)
            
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                imgStudent = cv2.resize(imgStudent, (216,216))

                # Convert the last attendance time from string to datetime object
                dateTimeObject = datetime.strptime(studentInfo['last_attendance_time'], '%Y-%m-%d %H:%M:%S')
                # Calculate the time elapsed since the last attendance in seconds
                secondsElapsed = (datetime.now() - dateTimeObject).total_seconds()
                # Print the elapsed time in seconds
                print(secondsElapsed)
                
                if secondsElapsed > 3000:

                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])

                    ref.child('last_attendance_time').set(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
                else:
                    modeType = 3
                    counter = 0
            
            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
            
                image_background[44:44+633, 808:808+414] = img_mode_list[modeType] # Overlay the first mode image onto the background image at specified coordinates
                
                if counter <= 10:
                    cv2.putText(image_background, str(studentInfo['total_attendance']), (861,125), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 1)
                    cv2.putText(image_background, studentInfo['major'], (1006,550), cv2.FONT_HERSHEY_COMPLEX, 0.4, (0,0,0), 1)
                    cv2.putText(image_background, str(id), (1006,493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 1)
                    cv2.putText(image_background, studentInfo['standing'], (910,625), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 1)
                    cv2.putText(image_background, str(studentInfo['year']), (1025,625), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 1)
                    cv2.putText(image_background, str(studentInfo['start_year']), (1125,625), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 0.8, 1)
                    offset = (414-w) // 2
                    cv2.putText(image_background, studentInfo['name'], (808+offset,445), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0,0,0), 1)

                    image_background[175:175+216, 909:909+216] = imgStudent


                counter += 1

                if counter >= 20:
                    modeType = 0
                    counter = 0
                    studentInfo = []
                    imgStudent = []
                    # image_background[44:44+633, 808:808+414] = img_mode_list[modeType] # Overlay the first mode image onto the background image at specified coordinates
    else:
        modeType = 0
        counter = 0
        studentInfo = []
        imgStudent = []

    cv2.imshow("Image Background", image_background) # Display the modified background image in a window

    if cv2.waitKey(1) & 0xFF == ord('q'): # Break the loop if the 'q' key is pressed
        break
    
cap.release() # Release the video capture object
cv2.destroyAllWindows() # Close all OpenCV windows
