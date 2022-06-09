#import La
from ulab import numpy
import math
import pyb
from pyb import UART
from pyb import Pin
import micropython
import StepperClass
import gc
import cotask
import task_share
pyb.repl_uart(None)

def g(x, theta):
    r = 1
    X = numpy.array(x)
    Theta = numpy.array([r*math.tan(theta[0]*math.pi/180), r*math.tan(theta[1]* math.pi/180)])
    return X -Theta
    
def dg_theta(theta):
    r = 1
    return(numpy.array([[-r*math.pow(1/math.cos(theta[0]*math.pi/180), 2), 0], [0, -r*math.pow(1/math.cos(theta[1]*math.pi/180), 2)]]))
    
def NewtonRaphson(fcn, jacobian, guess, thresh):
    steps = 1
    while (abs(fcn(guess)[0]) > thresh or abs(fcn(guess)[1]) > thresh):
        math = guess - numpy.dot(numpy.linalg.inv(jacobian(guess)),fcn(guess))
        guess = math
        steps += 1
    return guess

#---------------------------------------------
def motorsend():
    i = 3
    current = 2
    while i < len(datax):
        iterations.put(i)
        if datax[i] == "PU":
            LASER.low()
            i+=1
            yield(0)
        elif datax[i] == "PD":
            LASER.high()
            i+=1
            yield(0)
        else:
            xs = numpy.linspace(datax[current],datax[i],5)
            ys = numpy.linspace(datay[current],datay[i],5)
            gc.collect ()
            for j in range(len(xs)):
                TargetX.put(xs[j])
                TargetY.put(ys[j])
                motor.SetTargets(xs[j],ys[j])
                yield(0)
            current = i
            i+= 1

def motorCheck():
    while True:
        actx = ActX.get()
        acty = ActY.get()
        if abs(actx - TargetX.get()) < .5 and abs(acty - TargetY.get()) < .5 :
           next(motorsend)
        yield(0)



def computerSend():
    while True:
        actx = ActX.get()
        acty = ActY.get()
        uart.write(str(actx) +":"+ str(acty) +"\n")
        yield(0)
        
def getActual():
    while True:
        actx,acty = motor.GetActual()
        ActX.put(actx)
        ActY.put(acty)
        yield(0)
#---------------------------------------------------------------------------------------

# run this on startup
if __name__ == "__main__":
    pyb.repl_uart(None)
    print("start")
    uart = UART(2,115200)
    uart.init(115200, bits=8, parity=0, stop=1)
    micropython.alloc_emergency_exception_buf(100)
    LASER = Pin("C4",mode=Pin.OUT, value=0)
    ActX = task_share.Share ('f', thread_protect = False, name = "X Position")
    ActY = task_share.Share ('f', thread_protect = False, name = "Y Position")
    TargetX = task_share.Share ('f', thread_protect = False, name = "TargetX")
    TargetY = task_share.Share ('f', thread_protect = False, name = "TargetY")
    iterations= task_share.Share ('i', thread_protect = False, name = "iterations")
    q0 = task_share.Queue ('f', 4, thread_protect = False, overwrite = False, name = "Queue 0")
    ActX.put(0)
    ActY.put(0)
    TargetX.put(0)
    TargetY.put(0)
    motorsend = motorsend()
    print("actuals", ActX.get(), ActY.get())
    print("Target", TargetX, TargetY)
    pyb.repl_uart(None)
    f = open("Diamond.hpgl","r")
    Line = f.readline()
    List=Line.split(";")
    guess = [0,0]
    scalar = 120
    datax = []
    datay = []

    for command in List:
        if command == "IN":
            print("IN")
            motor = StepperClass.Stepper()
        elif "PU" in command:
            datax.append("PU")
            datay.append("PU")  
            temp = command.replace("PU","")
            temp = temp.split(",")
            if len(temp) != 1:
                for i in range(0, len(temp)-1,2):
                    X = [int(temp[i])/scalar,int(temp[i+1])/scalar]
                    answer = NewtonRaphson(lambda theta : g(X, theta), dg_theta, guess,  .1)
                    datax.append((answer[0]))
                    datay.append((answer[1]))
                    
        elif "PD" in command:
            datax.append("PD")
            datay.append("PD")  
            temp = command.replace("PD","")
            temp = temp.split(",")
            if len(temp) != 1:
                for i in range(0, len(temp)-1,2):
                    X = [int(temp[i])/scalar,int(temp[i+1])/scalar]
                    answer = NewtonRaphson(lambda theta : g(X, theta), dg_theta, guess,  .1)
                    datax.append((answer[0]))
                    datay.append((answer[1]))                               
        else:
            print("NA")
            
    motorcheck = cotask.Task (motorCheck, name = 'motorcheck', priority = 3, period = 500, profile = True, trace = False)
    computersend = cotask.Task (computerSend, name = 'computersend', priority = 1, period = 100, profile = True, trace = False)
    getactual = cotask.Task (getActual, name = 'getactual', priority = 2, period = 50, profile = True, trace = False)
    cotask.task_list.append (motorcheck)
    cotask.task_list.append (computersend)
    cotask.task_list.append (getactual)
    gc.collect ()

    while True:
        cotask.task_list.pri_sched ()
        gc.collect ()
#---------------------------------------------------------------------------------------