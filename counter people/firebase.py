import pyrebase
import datetime

firebaseConfig = {
  'apiKey': "AIzaSyBzv4wHTERmcKaN5lNL2IpYv0zIUkzhdaQ",
  'authDomain': "kudashboard2022.firebaseapp.com",
  'databaseURL': "https://kudashboard2022-default-rtdb.firebaseio.com",
  'projectId': "kudashboard2022",
  'storageBucket': "kudashboard2022.appspot.com",
  'messagingSenderId': "630601525788",
  'appId': "1:630601525788:web:c1f526ea143c8fe63a8dd9",
  'measurementId': "G-C2HDJ5X3DE"
}
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth = firebase.auth()
email = 'kudashboard@mail.com'
password = '123456'
auth.sign_in_with_email_and_password(email, password)
print("successfully signed in!")

def sendata(number):
    t = datetime.datetime.now()
    current_time = t.strftime("%Y-%m-%d %H:%M:%S")
    data = {'people':number}
    db.child("now").update(data)
    print(current_time)
    data = {current_time:number}
    db.child("people").update(data)

def get_ipcam():
  return db.get().val()['IPCAM']

def get_last_people():
  return db.child('now').get().val()['people']