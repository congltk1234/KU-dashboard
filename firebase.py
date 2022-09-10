import pyrebase
import datetime
import pandas as pd
import json

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

def extract_feature(diction):
  time =[]
  feature = []
  for key,val in diction.items():
    time.append(key)
    feature.append(val)
  return feature

def get_json():
  sensor = db.child('Sensor').get().val()
  sensor = json.loads(json.dumps(sensor))
  people = db.get().val()['people']
  data = {'sensors': sensor, 'people':people}
  data = json.dumps(data)
  return data



def get_human_count():
  people = db.get().val()['people']
  time =[]
  count = []
  for key,val in people.items():
    time.append(key)
    count.append(val)
  df = pd.DataFrame(list(zip(time, count)),columns =['TimeStamp', 'People in room'])
  return df



def get_data_sensors_from_firebase():
  data = db.child('Sensor').get()
  # Time and Current
  dict_current = data.val()['Current']
  time =[]
  current = []
  for key,val in dict_current.items():
    time.append(key)
    current.append(val)
  volte = extract_feature(data.val()['Volte'])
  watts = extract_feature(data.val()['Watts'])
  # Humidity
  humi = extract_feature(data.val()['Humidity'])
  # Temperature
  temp = extract_feature(data.val()['Temperature'])
  col =['TimeStamp', 'Current(A)', 'Volete(V)', 'Watts(W)', 'Humidity(%)', 'Temp(°C)']
  #df
  df = pd.DataFrame(list(zip(time, current, volte, watts, humi, temp )), columns =col )
  return df