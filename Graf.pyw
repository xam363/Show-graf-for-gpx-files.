import tkinter
from tkinter.filedialog import askopenfilename
from math import sin, cos, sqrt, atan2, radians
import matplotlib.pyplot as plt
import numpy as np


def speed(lat1, lon1, lat2, lon2, time1, time2):
    """ Take latitude and longitude and calculate speed in km/h """
    
    R = 6373.0 # approximate radius of earth in km

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    
    dlon = abs(lon2 - lon1)
    dlat = abs(lat2 - lat1)

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    time = abs(time1 - time2)
    try:
       return round(3600 / time * distance, 2) 
    except ZeroDivisionError:
        return 0.0

def distance(lat1, lon1, lat2, lon2):

    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    
    dlon = abs(lon2 - lon1)
    dlat = abs(lat2 - lat1)

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c
 
def gather_data():
    cond = False
    for i in date:   
        # take time from date
        if i.find('<trkseg>') != -1:
            cond = True    
        if i.find('<time>') != -1 and cond:
            time_list_sec.append(int(i[i.find('<time>')+17:i.find('<time>')+19])*60*60
                               + int(i[i.find('<time>')+20:i.find('<time>')+22])*60 
                               + int(i[i.find('<time>')+23:i.find('<time>')+25]))   
        # take latitude from date                       
        if i.strip().find('lat="') != -1:
            latitude_list.append(float(i[i.find('lat="') + 5:i.find('lon=') -2]))
        # take longitude from date 
        if i.strip().find('lon="') != -1:
            longitude_list.append(float(i[i.find('lon="') + 5:i.find('<ele>') -2]))
        # take heard rate from date
        if i.find('<gpxtpx:hr>') != -1:
            pulse_list.append(int(i[i.find('<gpxtpx:hr>')+11:i.find('</gpxtpx:hr>')]))

        # AltitudeMeters  
        if i.find('<ele>') != -1:
            altitude_meters_list.append(float(i[i.find('<ele>') + len('<ele>'):i.find('</ele>')]))

        # if lat and lon the same    
        try:
            if latitude_list[-1] == latitude_list[-2] and longitude_list[-1] == longitude_list[-2]:
                del latitude_list[-1], longitude_list[-1], time_list_sec[-1]
        except IndexError:
            pass
     
def find_speed_distance():
    ''' find speed and distanse '''
    global distance_list_plot
    lat_last = latitude_list[0]
    lon_last = longitude_list[0]
    time_last = time_list_sec[0]
    for lat_now, lon_now, time_now in zip(latitude_list, longitude_list, time_list_sec):
        speed_list.append(speed(lat_last, lon_last, lat_now, lon_now, time_last, time_now))
        distance_list.append(distance(lat_last, lon_last, lat_now, lon_now))
        lat_last, lon_last, time_last = lat_now, lon_now, time_now
    sum_distance = 0
    distance_list_plot = []
    for i in distance_list:
        sum_distance += i * 1000
        distance_list_plot.append(sum_distance)

def del_low_hight():
    # DEL NOTHING
    list_for_del = []
    for count, speed in enumerate(speed_list):
        if speed > 20 or speed < 3.0:
            list_for_del.append(count)
     
    for count in list_for_del[::-1]:
        del time_list_sec[count], speed_list[count], distance_list_plot[count], altitude_meters_list[count]
        if len(pulse_list) > 0:
            del pulse_list[count]

def average_graf(num_average):
    ''' calculate average for each data ''' 
    left = num_average // 2
    right = num_average - left
    global pulse_list, speed_list
    for i in range(len(speed_list)):
        if left > i:
            if len(pulse_list) > 0:
                pulse_list[i] = sum(pulse_list[0 : num_average]) / num_average
            speed_list[i] = sum(speed_list[0 : num_average]) / num_average
        elif i + right < len(speed_list):
            if len(pulse_list) > 0:
                pulse_list[i] = sum(pulse_list[i-left : i+right]) / num_average
            speed_list[i] = sum(speed_list[i-left : i+right]) / num_average
        else:
            temp = right - (len(speed_list) - i)
            if len(pulse_list) > 0:
                pulse_list[i] = sum(pulse_list[i-left-temp : i+right-temp]) / num_average
            speed_list[i] = sum(speed_list[i-left-temp : i+right-temp]) / num_average

def filter_len():
    len_alt = len(altitude_meters_list)
    len_pulse = len(pulse_list)
    len_dis = len(distance_list_plot)

    if len_alt > len_dis:
        del altitude_meters_list[-(len_alt-len_dis)]
    if len_dis > len_alt:
        del distance_list_plot[-(len_dis-len_alt)]

    if len_pulse > 0:
        if len_pulse > len_dis:
            del pulse_list[(-len_pulse-len_dis)]

# open file
tkinter.Tk().withdraw() # close tkinter window after ask the filepath
filename = askopenfilename() # ask filepath
date = open(filename, "r")
# declere lists of date
time_list_sec = []
latitude_list = []
longitude_list = []
speed_list = []
distance_list = []
pulse_list = []
altitude_meters_list = []


gather_data()
find_speed_distance()
del_low_hight()
filter_len()
# average_graf(50)



plt.style.use('bmh') # Setting graf
fig, host = plt.subplots() # Create graf

# make altitude graf
host3 = host.twinx()
host3.plot(distance_list_plot, altitude_meters_list, "green")
host3.axis('off')

host.plot(distance_list_plot, speed_list,  "blue") # Make graf 



poly = np.polyfit(distance_list_plot, speed_list, 15) # graf average line
poly_y = np.poly1d(poly)(distance_list_plot)
host.plot(distance_list_plot, poly_y, 'black')

if len(pulse_list) > 0:
    host2 = host.twinx()
    host2.plot(distance_list_plot, pulse_list,  "red") # Make graf 

    poly = np.polyfit(distance_list_plot, pulse_list, 15) # graf average line
    poly_y = np.poly1d(poly)(distance_list_plot)
    host2.plot(distance_list_plot, poly_y, 'black')


plt.subplots_adjust(left=0.05, right=0.95, top=1.0, bottom=0.1)

plt.show() # Show graf 

