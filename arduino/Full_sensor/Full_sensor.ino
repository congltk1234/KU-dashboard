////Call Library
#include "EmonLib.h"             // Include Emon Library
#include <WiFi.h>
#include <FirebaseESP32.h>
#include "RTClib.h" 
#include "DHT.h"

////// Wifi id/pass
#define WIFI_SSID "stc"                                  
#define WIFI_PASSWORD "suthanhcon"  

////// Firebase Authorization
 //https://kudashboard2022-default-rtdb.firebaseio.com/
#define FIREBASE_HOST "kudashboard2022-default-rtdb.firebaseio.com"      
#define FIREBASE_AUTH "0i4o1e0oHLvXA9hpoIFdqleNXCfPMfG6GdcbqrSp"        
FirebaseData fbdt;
///DHT PINOUT 33, TYPE 11
#define DHTPIN 33
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
//// Electric
EnergyMonitor emon1;             // Create an instance
#define VOLT_CAL 148.7
#define CURRENT_CAL 62.6
//// realtime
RTC_DS3231 rtc;

void setup()
{  
  Serial.begin(9600);
  dht.begin();            //reads dht sensor data 
  rtc.begin();            
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);   /// connect to wifi                               
  Serial.print("Connecting to ");
  Serial.print(WIFI_SSID);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("Connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());                               //prints local IP address
  emon1.voltage(35, VOLT_CAL, 1.7);  // Voltage: input pin, calibration, phase_shift
  emon1.current(34, CURRENT_CAL);       // Current: input pin, calibration.
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);                 // connect to the firebase
}

void loop()
{
  DateTime now = rtc.now();
  String time = String(now.hour()) + String("h") + String(now.minute()) + String("'") + String(now.second()) + String("''");
  String path = String("/now/time/");
  Firebase.setString(fbdt,path, time);
  String date = String(now.year()) + String("-") + String(now.month()) + String("-") + String(now.day());
  time = String(now.hour()) + String(":") + String(now.minute()) + String(":") + String(now.second());
  String datetime = String(date) + String(" ") + String(time);
  path = String("/now/date/");
  Firebase.setString(fbdt,path, datetime);
  Serial.print(datetime);
  Serial.println();
  float h = dht.readHumidity();                                 // Read Humidity
  float t = dht.readTemperature();                              // Read temperature
  if (isnan(h) || isnan(t))                                     // Checking sensor working
  {                                   
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  } 
  emon1.calcVI(20,2000);         // Calculate all. No.of half wavelengths (crossings), time-out

  float currentDraw            = emon1.Irms;             //extract Irms into Variable
  float supplyVoltage   = emon1.Vrms;                    //extract Vrms into Variable
  float watts = currentDraw * supplyVoltage;

  // Print value and push to FireBase
  Serial.print("Humidity: ");  
  Serial.print(h);
  Serial.print("%  Temperature: ");  
  Serial.print(t);  
  Serial.println("°C ");
 
  String key = String("/Sensor/Humidity/") + String(datetime);
  Firebase.setFloat(fbdt,key, h);            //setup path to send Humidity readings
  path = String("/now/humi/");
  Firebase.setFloat(fbdt,path, h);
  key = String("/Sensor/Temperature/") + String(datetime);
  Firebase.setFloat(fbdt,key, t);         //setup path to send Temperature readings
  path = String("/now/temp/");
  Firebase.setFloat(fbdt,path, t);
  Serial.print("Voltage: ");
  Serial.println(supplyVoltage);
  key = String("/Sensor/Volte/") + String(datetime);
  Firebase.setFloat(fbdt,key, supplyVoltage);            //setup path to send Volte readings
  path = String("/now/volte/");
  Firebase.setFloat(fbdt,path, supplyVoltage);
  Serial.print("Current: ");
  Serial.println(currentDraw);
  key = String("/Sensor/Current/") + String(datetime);
  Firebase.setFloat(fbdt,key, currentDraw);            //setup path to send Current readings
  path = String("/now/current/");
  Firebase.setFloat(fbdt,path, currentDraw);
  Serial.print("Watts: ");
  key = String("/Sensor/Watts/") + String(datetime);
  Firebase.setFloat(fbdt,key, watts);            //setup path to send Watts readings
  path = String("/now/watts/");
  Firebase.setFloat(fbdt,path, watts);
  Serial.println(currentDraw * supplyVoltage);
  Serial.println("\n\n");
//// set time: 1s = 1000
  delay(60000);
}
