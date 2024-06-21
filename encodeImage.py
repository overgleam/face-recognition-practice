import cv2
import face_recognition
import pickle
import os 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'databaseURL':'https://face-recognition-practic-8837b-default-rtdb.asia-southeast1.firebasedatabase.app/','storageBucket': 'face-recognition-practic-8837b.appspot.com'})


folderPath = 'Images' # Set the directory path where the student images are stored
pathList = os.listdir(folderPath) # List all files in the directory
print(pathList)  # Print the list of image files

imgList = []  # Initialize a list to store the images
studentIds = []  # Initialize a list to store the student IDs

for path in pathList: # Loop through each file in the directory
    imgList.append(cv2.imread(os.path.join(folderPath, path))) # Read the image and append to the imgList
    studentIds.append(os.path.splitext(path)[0]) # Extract the student ID from the filename and append to the studentIds list

    fileName = f'{folderPath}/{path}' # Create a file name with the path to the image
    bucket = storage.bucket()  # Get a reference to the Firebase storage bucket
    blob = bucket.blob(fileName)  # Create a blob object for the file in the bucket
    blob.upload_from_filename(fileName)  # Upload the file to Firebase storage

print(studentIds)  # Print the list of student IDs

def findEncodings(imagesList): # Define a function to find face encodings for a list of images
    encodeList = []  # Initialize a list to store the encodings
    for img in imagesList: # Loop through each image in the list
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Convert the image from BGR to RGB color space
        encode = face_recognition.face_encodings(image)[0] # Find the face encodings and take the first encoding if multiple faces are found
        encodeList.append(encode) # Append the encoding to the list

    return encodeList  # Return the list of encodings

print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)  # Find encodings for all images in the list
# print(encodeListKnown)  # Print the list of known encodings
encodeListKnownWithIds = [encodeListKnown, studentIds]  # Combine the encodings with the corresponding student IDs
print("Encoding Complete")

# Open a file to save the encodings
file = open("EncodeFile.pkl", "wb")
pickle.dump(encodeListKnownWithIds, file)  # Serialize and save the data to the file
file.close()  # Close the file
print("File Saved")  # Print a confirmation message
