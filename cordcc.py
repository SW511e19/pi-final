from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.motor import LargeMotor, OUTPUT_C, OUTPUT_B, SpeedPercent
import time
import socket

colorsensor = ColorSensor()
colorsensor.MODE_COL_COLOR
m1 = LargeMotor(OUTPUT_B) # Cord has to go over the wheel (right of the wheel)
m2 = LargeMotor(OUTPUT_C) # Cord has to go under the wheel

global_speed = 25 # positive is left, negative is right

#Sets the READY message, which means that the ev3 is ready to communicate with the PI
msgFromClient = "READY"

# Settings Up
bytesToSend = str.encode(msgFromClient)
bufferSize = 1024
serverAddressPort = ("169.254.204.164", 22222) # IP and Port of the Raspberry PI

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)

# Runs the motors. Which motor starts first depends on the direction. The motor not pulling the CC begins 
# First to loosen a little of the string the other motor can pull.
def run(speed):
    if speed >= 0:
        m2.on(SpeedPercent(speed * 1.3))
        m1.on(SpeedPercent(speed))
    else:
        m1.on(SpeedPercent(speed * 1.3))
        m2.on(SpeedPercent(speed))

def tighten(speed, seconds):
    print("tightens")
    if speed >= 0:
        m2.on(SpeedPercent(-speed))
        m1.on(SpeedPercent(speed))
    else:
        m1.on(SpeedPercent(speed))
        m2.on(SpeedPercent(-speed))
    time.sleep(seconds)
    stop_motor()

def stop_motor():
    m1.on(SpeedPercent(0))
    m2.on(SpeedPercent(0))

def calibrate():
    iteration = 0
    while (colorsensor.color != colorsensor.COLOR_RED):
        run(25)       
        if iteration % 10 == 0:
            tighten(20, 0.1)
        iteration += 1
    tighten(20, 0.1)

# To compensate for sensor getting false positive by reading a change away from white and back to white again despite not having moved much,
#  iterates a minimum amount of iterations that at least should have passed before looking for a new white. There will be a certain minimum distance
# because there always are a few iterations when moving between each box.
# If the card collector just calibrated it will read red and it should look for white right away since there is very little distance to the first
#  box so iteration will be less than 50 when reaching it.
def cc(box_number, box_offset, speed):
    iteration = 0
    clr_is_white = True
    look_for_white = False
    
    if(colorsensor.color == colorsensor.COLOR_RED):
        look_for_white = True

    while box_number != box_offset:
        run(speed)      
        if iteration % 10 == 0 and iteration != 0:
            tighten(20, 0.1)

        if iteration >= 50:
            look_for_white = True

        if look_for_white:
            if clr_is_white == False and colorsensor.color == colorsensor.COLOR_WHITE:
                clr_is_white = True
                print("was at " + str(box_number))
                if speed >= 0:
                    box_number -= 1
                else:
                    box_number += 1
                print("is at " + str(box_number))   
                look_for_white = False
                iteration = 0

            else: 
                if colorsensor.color != colorsensor.COLOR_WHITE:
                    clr_is_white = False
        iteration += 1
    return box_number

# Go to box 1 to 7. Which direction it goes depends on the current box position and which box it should go to
def go_to_box(current_box, dest_box, speed):
    if(dest_box == current_box):
        print("Was already at box")
    if dest_box < current_box:
        current_box = cc(current_box, dest_box, speed)
    else:
        current_box = cc(current_box, dest_box, -speed)
    stop_motor()
    return current_box

calibrate() # Goes to the red line at the end of the machine before any boxes, position 0
print("done calibrating")
box_num = 1
current_box = 0
num_to_add = 1

while(True):
    current_box = go_to_box(current_box, box_num, global_speed)
    print("Went to box " + str(box_num))
    time.sleep(5)
    if(box_num == 7):
        num_to_add = -1
    if(box_num == 1):
        num_to_add = 1
    box_num += num_to_add
    
#time.sleep(10)
#current_box = go_to_box(current_box, 1, global_speed)

#print("returns: " + str(current_box))
#current_box = go_to_box(2, 4)
