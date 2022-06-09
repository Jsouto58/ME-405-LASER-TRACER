# ME-405-LASER-TRACER
## Created by Jake Souto and Harrison Power
  
###### Project
  The objective for this project was to create a 2½ degree pen plotter with the challenge of making both dimensions non-linear. For our project we chose to control a laser pointer across two radial dimensions taking a long exposure photo of the laser path to “record the drawing”. In addition to this, we plot the curve that the machine is drawing on the computer in real time. Below is our final design as well as some of the drawing we made with it.
  <p align="center">
  <img src="Fullview.jpeg" alt="drawing" align = "center" width="500"/>
  </p>
   <p align="center">
  <img src="Diamond.JPG" alt="drawing" align = "center" width="250"/> <img src="SemiCircle.JPG" alt="drawing" align = "center" width="250"/> <img src="Star.JPG" alt="drawing" align = "center" width="250"/>
  </p> 
  
  
  
###### Chasis
  The chassis of our machine is functional for its purpose but has room for improvements. The supports of our chassis are laser cut wooden T’s which holds the vertical motor and the axles for the gears and platform. The acrylic laser cut gears are fundamental to this project as they gear up our stepper motor 10-1 allowing us to achieve a resolution of 120x120 steps and greatly increase our torque. The resulting shakiness visible in our final images stem from our chassis as the T supports are not fully stable and our laser cut gears don’t perfectly mesh with the metal stepper gears. If we were to improve upon this design, a sturdier and more precise chassis would improve the final product significantly.
  <p align="center">
  <img src="GearView.jpeg" alt="drawing" align = "center" width="400"/> <img src="Topview.jpeg" alt="drawing" align = "center" width="400"/>
  </p> 
  

###### Harware
The Board we used for this project is a Nucleo L476RG which interfaced serially with a TMC 4210 stepper motor IC, which gave commads to the TMC 2208 motor driver. The TMC 4210 and the TMC 2208 were pre-assembled on a custom PCB board which handled the connections between the two devices. The Nucleo was connected to this board and the motors as shown in the diagram below. 
<p align="center">
  <img src="Wiring.png" alt="drawing" align = "center" width="400"/> 
  </p>
The TMC 2208 chips had an on board current limiting potentiometer that we had to adjust manually. This was set by measuring the voltage across the vref pin and ground, and adjusting the potentiometer until the voltage read 0.7 V. The motors we used were 48 step per rotation / 7.5 degree per step four wire stepper motors. We unsoldered the curuit on the face of the motor to maually solder wired directly to the pins to more easily interface with the motors.
<p align="center">
  <img src="TMC2208.png" alt="drawing" align = "center" width="200"/> <img src="Motor.png" alt="drawing" align = "center" width="350"/>
  </p>
 

###### Movement calculaions
To convert the x,y coordinates to radial coordinates that we could write to our stepper motors we used what is called the Newton-Raphson algorithm. This algorithm consecutively approximates any given solution to an equation using the formula below. 

$$\begin{equation}
\frac{df^{-1}}{dθ} = 
  \begin{bmatrix}
    \frac{1}{rsec^2(θ1)} & 0 \\
    0 & \frac{1}{rsec^2(θ2)}
  \end{bmatrix}
\end{equation}$$

$$\begin{equation}
x_{n+1} =  x_n - 
  \begin{bmatrix}
    \frac{1}{rsec^2(θ1)} & 0 \\
    0 & \frac{1}{rsec^2(θ2)}
  \end{bmatrix}
  \begin{bmatrix}
    rtan(θ1)\\
    rtan(θ2)
  \end{bmatrix}
\end{equation}$$

This equation iterated through until the difference between the next step and the current one is less than some threshold; we know that the calculated thetas correspond to the desired x,y coordinates. Implementing this function into python and generating thetas for a simple circle we were able to genereate this gif to prove that our equation was correct for our implementation. 
<p align="center">
  <img src="mygif.gif" alt="drawing" align = "center" width="500"/> 
  </p>


###### Instructions for use
Setup the device facing a wall with ample space below and above the machine. Ensure the laser is pointing appropriately in the center of the Canvas then turn on the power supply to the stepper motors. Apply 5V to the laser pointer circuit and the hardware is set up.

For the software download the code from the git repository. There are three important files, StepperClass.py, Wrapper.py, cotask.py, task_share.py and Bell.py. The Bell.py file stays on the computer while all of the other files will be installed via Thonny onto the Nucleo. Additionally, an hpgl file of the desired path should be installed onto the Nucleo as well. Once all the files are installed, edit Wrapper to ensure that it correctly opens the desired hpgl file. Connect the Nucleo to the desktop and run the Bell.py program (make sure it has the correct com port for your computer) which will wait for the serial input from the Nucleo. Run the Wrapper.py file from the Nucleo and the machine will begin to draw the path and update the live tracker on the computer.
