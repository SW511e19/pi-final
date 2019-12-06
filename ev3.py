import ev3dev.ev3 as ev3
from time import perf_counter
import time
import socket

backWheel = ev3.LargeMotor('outA')
frontWheel = ev3.LargeMotor('outB')
piston = ev3.MediumMotor('outC')

#Sets the READY message, which means that the ev3 is ready to communicate with the PI
msgFromClient = "READY"

# Settings Up
bytesToSend = str.encode(msgFromClient)
bufferSize = 1024
serverAddressPort = ("169.254.204.164", 22222) # IP and Port of the Raspberry PI

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)

# Set Postion of each Motor in Symboltable for global reference and updating.
globals()['backPos'] = 0
globals()['frontPos'] = 0
globals()['pistonPos'] = 0
globals()['doPushPiston'] = 0

def runBackCycle(new_pos):
    backWheel.run_to_abs_pos(position_sp=new_pos, speed_sp = 200)
    time.sleep(8)
    backWheel.run_to_abs_pos(position_sp=new_pos, speed_sp = 50)
    time.sleep(3)
    return

def runFrontCycle(new_pos):
    frontWheel.run_to_abs_pos(position_sp=new_pos, speed_sp = 40)
    time.sleep(2)
    return

def runPiston(new_pos):
    piston.run_to_abs_pos(position_sp=new_pos, speed_sp = 400)
    time.sleep(5)
    return

def calibrateMachine():
    position = 0
    print("Starting Calibration...")
    backWheel.run_to_abs_pos(position_sp=position, speed_sp = 1000)
    frontWheel.run_to_abs_pos(position_sp=position, speed_sp = 1000)
    piston.run_to_abs_pos(position_sp=position, speed_sp = 400)
    time.sleep(30)
    backWheel.run_to_abs_pos(position_sp=position, speed_sp = 50)
    frontWheel.run_to_abs_pos(position_sp=position, speed_sp = 50)
    time.sleep(30)
    print("Calibrated")
    print("Place cards within 20 seconds...")
    time.sleep(10)
    print("Calibration done - starting")
    return

def backMotor(position):
    # Updating Symbol Table to Move One Cycle
    globals()['backPos'] = position - 1000
    # Setting the position to the new target
    position = globals()['backPos']
    # Running one Cycle to the targeted position. // Optimiation, test with only symble table call
    runBackCycle(position)
    return 

def frontMotor(position):
    # Updating Symbol Table to Move One Cycle
    globals()['frontPos'] = position - 50
    # Setting the position to the new target
    position = globals()['frontPos']
    # Running one Cycle to the targeted position.
    runFrontCycle(position)
    return position

def pushPiston(position):
     # Updating Symbol Table to Move One Cycle
    globals()['pistonPos'] = position + 360
    # Setting the position to the new target
    position = globals()['pistonPos']
    # Running one Cycle to the targeted position.
    runPiston(position)
    return

def checkCardPlacement():
    # Asks the Pi if there is card or not. Card:No_card
    # Timeout on 15 seconds
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    msg = "Card check upcode from the Rasberry Pi {}".format(msgFromServer[0])
    print(msg)
    if ("b'card'" in msg):
        print("Read Card")
        globals()['doPushPiston'] = 1
        return True
    if ("not_card" in msg):
        print("Read Not Card")
        globals()['doPushPiston'] = 0
        return False
    # In case of no Upcode we just return false.
    return False

def getCardPlacement():
    # Asks the Pi if there is card or not. Card:No_card
    # Timeout on 15 seconds
    msgFromClient = "REQUEST"
    bytesToSend = str.encode(msgFromClient)
    bufferSize = 1024
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    msg = "Card check upcode from the Rasberry Pi {}".format(msgFromServer[0])
    print(msg)

def positionCardCollector():
    pushPiston()
    
    
# Calibrating the Machine for first time use
calibrateMachine()
# Starting the Cyclic Executive Loop
while(1):
    #Running the back motor, filling up an average of 5 cards
    backMotor(backPos)
    # Running the first iteration of the front motor.∂
    for x in range(18):
        frontMotor(frontPos)
        checkCardPlacement()
        if (doPushPiston == 1):
            getCardPlacement()
            pushPiston(pistonPos)
