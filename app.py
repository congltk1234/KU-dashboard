import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
from datetime import datetime
import plost
import os
from PIL import Image

import pyrebase
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



### Seting current working
owd = os.getcwd()

st.set_page_config(
    page_title = 'KU Dashboard',
    page_icon = '✅',
    layout = 'wide',
    menu_items={'About': """# Recorded Data from sensor and Camera 
                            This is an *extremely* cool app!"""}    
)

# dashboard title
st.title("KU Real-Time Dashboard")

DATE_COLUMN = 'TimeStamp'


def load_data():
# Load data into the dataframe.
    df = get_data_sensors_from_firebase()
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
    sensors = list(df.columns)
    sensors = sensors[1:]
    ##### HUMAN COUNT ####
    human_count = get_human_count()
    human_count['TimeStamp'] = pd.to_datetime(human_count['TimeStamp'])
    return df, human_count

@st.cache
def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return df.to_csv().encode('utf-8')

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
df, human_count = load_data()
sensors = list(df.columns)
sensors = sensors[1:]
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

# timestamp = data['TimeStamp']
# from datetime import time
# appointment = st.slider("Schedule your appointment:",value=(time(11, 30), time(12, 45)))
# st.write("You're scheduled for:", appointment)

# start_time = st.slider("When do you start?", value=datetime(2022, 9, 1, 0, 0),format="MM/DD/YY - hh:mm:ss")
# st.write("Start time:", start_time)

# hour_to_filter = st.slider('TimeStamp', df['TimeStamp'].min(), df['TimeStamp'].max(), df['TimeStamp'].max())  # min: 0h, max: 23h, default: 17h

#### Make output dir
try:
    os.mkdir('output')
except:
    pass


##### SIDEBAR ####
with st.sidebar:
    #### QUERY TIME ####
    st.header("OPTIONAL")
    if st.button('Reload'):
        df, human_count = load_data()
    start_dt = st.sidebar.date_input('Start Time', value=df['TimeStamp'].min())
    df = df[df['TimeStamp'] > datetime(start_dt.year, start_dt.month, start_dt.day)]
    human_count = human_count[human_count['TimeStamp'] > datetime(start_dt.year, start_dt.month, start_dt.day)]
    type_dashboard = st.radio("Choose Type of Dashboard for show:", ('RealTime', 'RangeTime'))
    if type_dashboard == 'RangeTime':
        end_dt = st.sidebar.date_input('End Time', value=df['TimeStamp'].max())
        if start_dt <= end_dt:
            df = df[df['TimeStamp'] < datetime(end_dt.year, end_dt.month, end_dt.day+1)]
            human_count = human_count[human_count['TimeStamp'] < datetime(end_dt.year, end_dt.month, end_dt.day+1)]
        else:
            st.error('Start date must be > End date')
        

    ## Checkbox show data
    show_data = st.checkbox('Show data')   
    # show_human_data = st.checkbox('Show human counting')

    # Save data
    if st.button('Export all data to CSV'):
        os.chdir('output')
        df.to_csv('sensors.csv')
        human_count.to_csv('people_count.csv')
        st.success("Alrady export data to Output folder!")
        os.chdir(owd)


    json_data = get_json()
    json_button = st.download_button(label="Download JSON",
    file_name="data.json", mime="application/json",data=get_json())
    if json_button:
        st.success("Already export data to JSON!")
    st.json(json_data, expanded=False)
    ### Message
    with st.spinner("Loading..."):
        time.sleep(1)
    
def sensor_button(show_data):
    if show_data:
            st.subheader('Raw sensor data')
            query = ['TimeStamp']
            for i in options_sensors:
                query.append(i)
            ## Button Export CSV 
            csv = convert_df(df[query])
            sensors = st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='sensors.csv',
                    mime='text/csv')
            if sensors:
                st.success("Data downloaded successfully!")       
            st.table(df[query])

color = {'Current(A)':'#ddf542', 'Volete(V)':'#ff1900', 'Watts(W)': '#ed6b00', 'Humidity(%)':'#10ed00', 'Temp(°C)':'#0043ed' }
label = {'Current(A)':'Current', 'Volete(V)':'Volete', 'Watts(W)': 'Watts', 'Humidity(%)':'Humidity', 'Temp(°C)':'Temperature' }
unit = {'Current(A)':'A', 'Volete(V)':'V', 'Watts(W)': 'W', 'Humidity(%)':'%', 'Temp(°C)':'°C' }
avg = {'Current(A)':df['Current(A)'].mean(),
         'Volete(V)':df['Volete(V)'].mean(),
         'Watts(W)': df['Watts(W)'].mean(),
         'Humidity(%)':df['Humidity(%)'].mean(),
          'Temp(°C)':df['Temp(°C)'].mean()}
about_tab, sensor_tab, people_tab= st.tabs(["About the Project","📈Sensors", "👥People count"])
with about_tab:
    st.header("Describe about the Project")
    st.subheader("Which Hardware used??")
    image = Image.open('hardware.png')
    st.image(image, caption='Sensors System', width=500)
with sensor_tab:
    if type_dashboard == 'RealTime':
        tit, cur_time =  st.columns(2)
        tit.header("Sensors data")
        t = datetime.now()
        t = t.strftime("%Y-%m-%d %H:%M:%S")
        cur_time.header(f'{t}')
    options_sensors = st.multiselect('Select sensors for show:',sensors)

    # creating Metric
    if len(options_sensors) > 0:
        metric1, metric2, metric3, metric4, metric5 = st.columns(5)
        try: 
            with metric1:
                st.metric(label=label[options_sensors[0]], value=f"{avg[options_sensors[0]]:.2f} {unit[options_sensors[0]]}", delta=f"10 {unit[options_sensors[0]]}")
            with metric2:
                st.metric(label=label[options_sensors[1]], value=f"{avg[options_sensors[1]]:.2f} {unit[options_sensors[1]]}", delta=f"10 {unit[options_sensors[1]]}")
            with metric3:
                st.metric(label=label[options_sensors[2]], value=f"{avg[options_sensors[2]]:.2f} {unit[options_sensors[2]]}", delta=f"10 {unit[options_sensors[2]]}")
            with metric4:
                st.metric(label=label[options_sensors[3]], value=f"{avg[options_sensors[3]]:.2f} {unit[options_sensors[3]]}", delta=f"10 {unit[options_sensors[3]]}")
            with metric5:
                st.metric(label=label[options_sensors[4]], value=f"{avg[options_sensors[4]]:.2f} {unit[options_sensors[4]]}", delta=f"10 {unit[options_sensors[4]]}")
        except:
            pass
    else:
        st.caption('Please choose at least one parameter for view.')


    #plots
    if len(options_sensors) > 2:
        graph1, graph2 = st.columns(2)
        with graph1:
            st.subheader(f"{options_sensors[0]} data")
            plost.line_chart(df, x='TimeStamp',  # The name of the column to use for the x axis.
            y= (options_sensors[0]),  # The name of the column to use for the data itself.
            color = color[options_sensors[0]],
            width=450, pan_zoom='minimap')
        with graph2:
            st.subheader(f"{options_sensors[1]} data")
            plost.line_chart(df, x='TimeStamp',  # The name of the column to use for the x axis.
            y= (options_sensors[1]),  # The name of the column to use for the data itself.
            color = color[options_sensors[1]],
            width=450, pan_zoom='minimap')
        try:
            graph3, graph4 = st.columns(2)
            with graph3:
                st.subheader(f"{options_sensors[2]} data")
                plost.line_chart(df, x='TimeStamp',  # The name of the column to use for the x axis.
                y= (options_sensors[2]),  # The name of the column to use for the data itself.
                color = color[options_sensors[2]],
                width=450, pan_zoom='minimap')
            with graph4:
                st.subheader(f"{options_sensors[3]} data")
                plost.line_chart(df, x='TimeStamp',  # The name of the column to use for the x axis.
                y= (options_sensors[3]),  # The name of the column to use for the data itself.
                color = color[options_sensors[3]],
                width=450, pan_zoom='minimap')
        except:
            pass
        try:
            graph5, graph6 = st.columns(2)
            with graph5:
                st.subheader(f"{options_sensors[4]} data")
                plost.line_chart(df, x='TimeStamp',  # The name of the column to use for the x axis.
                y= (options_sensors[4]),  # The name of the column to use for the data itself.
                color = color[options_sensors[4]],
                width=500, pan_zoom='minimap')
        except:
            pass
        sensor_button(show_data)

    elif len(options_sensors) > 0:
        for i in options_sensors:
            st.subheader(f"{i} data")
            plost.line_chart(df, x='TimeStamp',  # The name of the column to use for the x axis.
            y= (i),  # The name of the column to use for the data itself.
            color = color[i],
            width=1000, pan_zoom='minimap')
        sensor_button(show_data)



with people_tab:
    if type_dashboard == 'RealTime':
        tit, cur_time =  st.columns(2)
        tit.header("People Counting")
        t = datetime.now()
        t = t.strftime("%Y-%m-%d %H:%M:%S")
        cur_time.header(f'{t}')    
    a, curr, avg , b =  st.columns(4)
    with curr:
        current_people = np.array(human_count['People in room'])
        st.metric(label='Current People', value=f"{current_people[-1]}")
    with avg:
        st.metric(label='AVG People', value=f"{human_count['People in room'].mean():.0f}")

    if show_data:
        graph, data_col= st.columns([3, 1])
        with graph:
            plost.line_chart(  human_count, x='TimeStamp',  # The name of the column to use for the x axis.
                y= ( 'People in room'), height=400, width=700,pan_zoom='minimap')
        with data_col:
            st.subheader('Data Record')
            st.write(human_count)
        ## Button Export CSV
            csv = convert_df(human_count)
            people = st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='human_count.csv',
                    mime='text/csv')
            if people:
                st.success("Data downloaded successfully!")
    else:
        plost.line_chart( human_count, x='TimeStamp',  # The name of the column to use for the x axis.
                        y= ( 'People in room'), width=1000,pan_zoom='minimap')    

# https://plost.streamlitapp.com/
# https://github.com/Socvest/streamlit-on-Hover-tabs
# https://github.com/PablocFonseca/streamlit-aggrid
