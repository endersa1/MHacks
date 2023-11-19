import firebase_admin
from firebase_admin import storage

cred_obj = firebase_admin.credentials.Certificate('alert-563fb-firebase-adminsdk-bssfd-87718064f0.json')
default_app = firebase_admin.initialize_app(cred_obj, 
    {
	'databaseURL':'https://alert-563fb-default-rtdb.firebaseio.com/',
    'storageBucket':'alert-563fb.appspot.com'
	})
fileName = "eye_gaze_coordinates.csv"
bucket = storage.bucket()
blob = bucket.blob(fileName)
blob.upload_from_filename(fileName)