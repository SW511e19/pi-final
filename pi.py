from keras.models import model_from_json
from pathlib import Path
from keras.preprocessing import image
import numpy as np
from keras.applications import vgg16
import os
import time
import uuid
from PIL import Image, ImageChops
import socket
import requests
import boto3

globals()['upcode'] = 0

f = open("sandbox/file.log", "r")
a = f.read().split(";")
def convert(list):
    list.pop() #removes last empty element due to conversion
    globals()['colNocr'] = list[0] #Store Type of element in symbol table
    list.remove(list[0]) # remove it from the list before going to a static tuple
    return tuple(list)
globals()['box_list'] = convert(a)

# Splits the keywords into individual strings
for entry in box_list:
    entry = entry.split(" ")


def resizer(src, dest):
    im = Image.open(src)
    im2 = im.resize((224, 224), Image.BICUBIC)
    im2.save(dest, "png")
    print(dest)
    
def ocr_image():
    image_path = "/home/pi/Desktop/ocr_card.png"
    os.system("raspistill -sa 55 -q 90 -sh 100 -ISO 50 -t 1000 -o " + image_path )
    # Read document content
    with open(image_path, 'rb') as document:
        imageBytes = bytearray(document.read())

    # Amazon Textract client
    textract = boto3.client('textract')

    # Call Amazon Textract
    response = textract.detect_document_text(Document={'Bytes': imageBytes})

    #print(response)

    # Print detected text
    file = open("card.txt", "w")
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            print ('\033' +  item["Text"] + '\033')
            file.write('\033' +  item["Text"] + '\033 \n')
    file.close()

def assescnc():
    image_path = "/home/pi/Desktop/cnc.png"

    os.system("raspistill -sa 55 -q 90 -sh 100 -ISO 50 -t 1000 -o " + image_path )

    resizer(image_path, image_path)
    
    #Sends image to the server
    url = "http://169.254.182.43:5000"
    files = {'image': open(image_path, 'rb')}
    response = requests.request("POST", url, files=files)
    print(response)

# Setting Up the Server Settings for Raspberry Pi
localIP     = "169.254.204.164"
localPort   = 22222
bufferSize  = 1024

#Defining Attributes
msgFromServer       = "This is sent from the server"
bytesToSend         = str.encode(msgFromServer)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

# Listen for incoming datagrams
def readyToReceive():
    print("UDP server up and listening")
    while(True):
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]
        address = bytesAddressPair[1]
        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)    
        print(clientMsg)

        if b"READY" in message:
            globals()['upcode'] = 1
            break;
        
        if b"REQUEST" in message:
            globals()['upcode'] = 2
            break;

        print(clientIP)
    return bytesAddressPair;

filepath = 'card.txt'
def classification():
    with open(filepath) as fp:
        file = fp.read() # Contents of file saved as string
        matches = []
        keywords = 0
        
        # Iterate through every keyword and their subkeywords
        for entry in box_list: 
            for keyword in entry:
                if keyword in file:
                    keywords += 1
                    
                #Stops looking at a set of keywords if any are missing from text
                else:
                    break
                
                #Returns box number if a set of keywords match
                if len(entry) == keywords:
                    return box_list.index(entry)
            keywords = 0

while(True):
    print("in ready to receive")
    bytesAddr = readyToReceive();
    address = bytesAddr[1]
    print("out of ready to receive")
    
    # Checking if there is a card
    if (upcode == 1):
        print (" Taking Picture and upload to MS")
        assescnc()
        res = requests.get('http://169.254.182.43:5000/isCard')
        bytesToSend = str.encode(res.text)
        UDPServerSocket.sendto(bytesToSend, address)
    
    # Checking OCR of the card
    if (upcode == 2):
        print("In UPCODE 2 + COL IS")
        print(type(colNocr))
        if(colNocr == "0"):
            print (" Taking Picture with AWS")
            ocr_image()
            class_upcode = classification()
            print("THIS BOX INDEX : ")
            print(class_upcode)
            bytesToSend = str.encode(str(class_upcode))
            UDPServerSocket.sendto(bytesToSend, address)
            print (" out of protocol")
        if(colNocr == "1"):
            print (" Assessing color")
            assescnc()
            res = requests.get('http://169.254.182.43:5000/whichCard')
            print("THIS BOX INDEX : ")
            box = box_list.index(res.text)
            print("Read Card color :" +  str(res.text))
            print("Read box index : " + str(box))
            bytesToSend = str.encode(str(box))
            UDPServerSocket.sendto(bytesToSend, address)
