#HW2
import numpy
import math
import matplotlib.animation as ani
import matplotlib.pyplot as plt
import serial
from PIL import Image

plt.ion()
fig  = plt.figure()
ax = fig.add_subplot(111)
plt.xlim([-2,2])
plt.ylim([-2,2])
plt.ylabel('theta 2: Yaxis')
plt.xlabel('theta 1: Xaxis')
with serial.Serial("com21",115200,timeout = 1) as ser:
    ser.flush()
    datax = []
    datay= []
    line1, = ax.plot(datax, datay, 'b-')
    while True:
        while ser.in_waiting == 0:
            pass
        stuff = ser.readline()
        print(stuff)
        interp = stuff.decode().split(":")
        print(interp)
        try:
            datax.append(math.tan(float(interp[0])*math.pi/180))
            datay.append(math.tan(float(interp[1])*math.pi/180))
            line1.set_xdata(datax)
            line1.set_ydata(datay)
            fig.canvas.draw()
            fig.canvas.flush_events()
        except:
            pass
