from opcua import Client
import time
import csv
from datetime import datetime
import sqlite3
import bokeh
from bokeh.io import curdoc
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.models.annotations import Title
import numpy as np

source = ColumnDataSource(dict(vibx=[],viby=[],vibz=[],tim=[]))

t1 = Title()
t2 = Title()
t3 = Title()

fig1 = figure(width=250, height=250, x_axis_type = 'datetime')
fig1.line(source=source, x = 'tim',y = 'vibx',line_width = 2, alpha = 0.85,color = 'red')
t1.text = "Vibration-X"
fig1.title = t1

fig2 = figure(width=250, height=250, x_axis_type = 'datetime')
fig2.line(source=source, x = 'tim',y = 'viby',line_width = 2, alpha = 0.85,color = 'blue')
t2.text = "Vibration-Y"
fig2.title = t2

fig3 = figure(width=250, height=250, x_axis_type = 'datetime')
fig3.line(source=source, x = 'tim',y = 'vibz',line_width = 2, alpha = 0.85,color = 'green')
t3.text = "Vibration-Z"
fig3.title = t3

p = gridplot([[fig1, fig2,fig3]], toolbar_location = None)



row = []
#Dummy_url = "opc.tcp://127.0.0.1:4840"
url = "opc.tcp://169.254.52.188:4842"
client = Client(url)
client.connect()
print("client connected")

def update_data():
    # Data acquisition from opc server
    Vibx = client.get_node("ns=2;i=2")
    Vib_x = Vibx.get_value()
    print(Vib_x)
    Viby = client.get_node("ns=2;i=3")
    Vib_y = Viby.get_value()
    print(Vib_y)
    Vibz = client.get_node("ns=2;i=4")
    Vib_z = Vibz.get_value()
    print(Vib_z)
    temp = client.get_node("ns=2;i=5")
    Temp = temp.get_value()
    print(Temp)
    T = client.get_node("ns=2;i=6")
    Time = T.get_value()
    print(Time)

# Organising data for processing
    new_data = dict(vibx=[Vib_x],viby=[Vib_y],vibz=[Vib_z],tim=[Time])
    row = [Time, Vib_x, Vib_y, Vib_z, Temp]#[Time,Temperature,pressure]
    source.stream(new_data, 100)

# storing data into csv file
    with open('vibration_data.csv','a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
    csvFile.close()

    time.sleep(1)

    # Write files onto SQL Server
    conn = sqlite3.connect('Vibration_data.db')
    print ("Opened database successfully");
    conn.execute("INSERT INTO Vibtration VALUES (?, ?, ?, ?, ?)",row);
    print ("Records created successfully");
    conn.commit()
    conn.close()

curdoc().add_root(p)
curdoc().add_periodic_callback(update_data, 100)
