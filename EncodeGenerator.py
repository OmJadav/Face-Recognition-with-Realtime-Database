# import os
# import cv2
# import pickle
#
# import dotenv
# import face_recognition
# import cloudinary
# import dotenv
# import cloudinary.uploader
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
#
# dotenv.load()
# cred = credentials.Certificate("serviceAccountKey.json")
# firebase_admin.initialize_app(cred,{
#     'databaseURL':"https://faceattendance-a4fe5-default-rtdb.firebaseio.com/",
# })
#
# CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
# CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
# CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
#
# # Initialize Cloudinary
# cloudinary.config(
#     cloud_name = f'{CLOUDINARY_CLOUD_NAME}',
#     api_key =  f'{CLOUDINARY_API_KEY}',
#     api_secret =  f'{CLOUDINARY_API_SECRET}',
# )
# folderPath='Images'
# pathList=os.listdir(folderPath)
# imgList=[]
# studentIds=[]
#
# for path in pathList:
#     imgList.append(cv2.imread(os.path.join(folderPath,path)))
#     studentIds.append(os.path.splitext(path)[0])
#     fileName =f'{folderPath}/{path}'
#     bucket=storage.bucket()
#     blob=bucket.blob(fileName)
#     blob.upload_from_filename(fileName)
#
# print(studentIds)
#
# def findEncodings(imagesList):
#     encodeList=[]
#
#     for img in imagesList:
#         img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
#         encode=face_recognition.face_encodings(img)[0]
#         encodeList.append((encode))
#     return encodeList
# print("Encoding Started...")
# encodeListKnown = findEncodings(imgList)
# encodeListKnownWithIds = [encodeListKnown,studentIds]
# print("Encoding Completed.")
#
# file=open("EncodeFile.p",'wb')
# pickle.dump(encodeListKnownWithIds,file)
# file.close()
# print("File Saved.")
#
#


import os
import cv2
import pickle
import dotenv
import face_recognition
import cloudinary
import cloudinary.uploader
import firebase_admin
from firebase_admin import credentials, db

# Load environment variables
dotenv.load()

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-a4fe5-default-rtdb.firebaseio.com/"
})

# Initialize Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []

ref = db.reference('Students')

for path in pathList:
    studentId = os.path.splitext(path)[0]
    studentIds.append(studentId)

    # Read the image
    img = cv2.imread(os.path.join(folderPath, path))
    imgList.append(img)

    # Upload image to Cloudinary
    response = cloudinary.uploader.upload(os.path.join(folderPath, path), folder="face_attendance")
    image_url = response['secure_url']

    # Update Firebase database with Cloudinary image URL
    ref.child(studentId).update({"image_url": image_url})

print(studentIds)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Completed.")

# Save the encodings to a file
with open("EncodeFile.p", 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)

print("File Saved.")
