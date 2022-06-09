import pyb
from pyb import Pin
from pyb import SPI
import ustruct


class Stepper:
    def __init__(self):
        self.En1 = Pin("C6",mode=Pin.OUT, value=0)
        self.En2 = Pin("C7",mode=Pin.OUT, value=0)
        self.cs1 = Pin('B6', mode=Pin.OUT, value=1)
        self.cs2 = Pin('B7', mode = Pin.OUT, value = 1)
        self.PB0 = Pin('B0', mode=Pin.OUT_PP)
        
        self.tim = pyb.Timer(1,period = 3, prescaler = 0)
        self.clk = self.tim.channel(2, pin = self.PB0, mode = pyb.Timer.PWM, pulse_width = 2)
        self.spi = SPI(2, SPI.CONTROLLER, baudrate=600000, polarity=1, phase=1,firstbit=SPI.MSB)
        
        #Enabling Stepper Driver
        ba = bytearray([0b01101000,0b00000000,0b00000000,0b00100000])
        self.Send1(ba)
        self.Send2(ba)
        
        #Set Velocities
        self.SetVelocity(0b00110000,0b11111111)
        
        #Set Pulse/Ramp Div
        ba = bytearray([0b00011000,0b00000000,0b01110111,0b00000000])
        self.Send1(ba)
        self.Send2(ba)
        
        #Set Amax
        self.SetAcceleration("None")
        
        #Set Ramp Mode
        ba = bytearray([0b00010100,0b00000000,0b00000011,0b00000000])
        self.Send1(ba)
        self.Send2(ba)
        
        #Set Current Pos
        ba = bytearray([0b00000010,0b00000000,0b00000000,0b00000000])
        self.Send1(ba)
        self.Send2(ba)
        
    def SetVelocity(self,Vmin, Vmax):
        #Enter Numbers in form of bits
        bamin = bytearray([0b00000100,0b00000000,0b00000000,Vmin])
        bamax = bytearray([0b00000110,0b00000000,0b00000000,Vmax])
        self.Send1(bamin)
        self.Send1(bamax)
        self.Send2(bamin)
        self.Send2(bamax)
        
    def SetAcceleration(self,Amax):
        #Amax = 1040
        #Pmul = 128
        #Pdiv = 2**4... 1 register
        #q = .98
        ba = bytearray([0b00001100,0b00000000,0b00000000,0b11110101]) #Amax
        self.Send1(ba)
        self.Send2(ba)
        
        ba = bytearray([0b00010010,0b00000000,0b11110100,0b00000101]) #Pmul 244 / Pdiv 2
        self.Send1(ba)
        self.Send2(ba)
        
    def LimitSwithes(self):
        pass

    def SetTarget1(self, Target):
        SmallRotation = Target * 10
        Steps = round((384 * (SmallRotation/360)))
        ba2 = Steps.to_bytes(3,"big")
        ba = bytearray(([0b000000000, ba2[0], ba2[1],ba2[2]]))
        self.Send1(ba)

        
    def SetTarget2(self, Target):
        SmallRotation = Target * 10
        Steps = round((384 * (SmallRotation/360)))
        ba2 = Steps.to_bytes(3,"big")
        ba = bytearray(([0b000000000, ba2[0], ba2[1],ba2[2]]))
        self.Send2(ba)
    
    def SetTargets(self, x, y):
        self.SetTarget1(x)
        self.SetTarget2(y)
    
    def GetActual(self):
        ba = bytearray([0b00000011,0b00000000,0b00000000,0b00000000])
        data = self.Send1(ba)     
        if data[1]>> 7 == 1:
            Steps = bytearray([0b11111111, data[1], data[2],data[3]])
        else:
            Steps = bytearray([0b00000000, data[1], data[2],data[3]])
        Steps = ustruct.unpack(">l", Steps)[0]
        SmallRotation = ((int(Steps)/384) * 360)
        Target1 = SmallRotation/10

        ba = bytearray([0b00000011,0b00000000,0b00000000,0b00000000])
        data = self.Send2(ba)
        if data[1]>> 7 == 1:
            Steps = bytearray([0b11111111, data[1], data[2],data[3]])
        else:
            Steps = bytearray([0b00000000, data[1], data[2],data[3]])
        Steps = ustruct.unpack(">l", Steps)[0]
        SmallRotation = ((int(Steps)/384) * 360)
        Target2 = SmallRotation/10
        return(Target1,Target2)
        
    def GetVersions(self):
        print("Chip 1")
        ba = bytearray([0b01110011,0b00000000,0b00000000,0b00000000])
        data = self.Send1(ba)
        for idx,byte in enumerate(data): print(f"b{3-idx}: {byte:#010b} {byte:#04x}")
        print("Chip 2")
        data = self.Send2(ba)
        for idx,byte in enumerate(data): print(f"b{3-idx}: {byte:#010b} {byte:#04x}")
        
    def Send1(self,byte):
        self.cs1.low()
        data = self.spi.send_recv(byte)
        self.cs1.high()
        return data
    
    def Send2(self,byte):
        self.cs2.low()
        data = self.spi.send_recv(byte)
        self.cs2.high()
        return data
   
#Motor = Stepper()
#Motor.GetVersions()
#Motor.GetActual()
#Motor.SetTarget(180)

#Motor.SetTargets(0,3)
#pyb.delay(1000)
#Motor.GetActual()

 

    

