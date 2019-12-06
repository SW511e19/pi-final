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
globals()['boxlist'] = () #Da tuple lmao
globals()['colNocr'] = 0

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
    url = "http://127.0.0.1:5000"
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
        line = fp.readline()
        while line:
            line = fp.readline()
            if "Artifact" in line:
                print("of class Artifact")
                return "box_0"
            if "Artifact Creature" in line:
                print("of class Artifact Creature")
                return "box_1"
            if "Creature" in line:
                print("This is a Creature")
                return "box_2"
            if "Instant" in line:
                print("This is an Instant Spell")
                return "box_3"
            if "Sorcery" in line:
                print("This is a Sorcery Spell")
                return "box_4"
            if "Enchantment" in line:
                print("This is an Enchantment")
                return "box_5"
            if "Land" in line:
                print("This is a Land")
                return "box_6"

while(True):
    print("in ready to receive")
    bytesAddr = readyToReceive();
    address = bytesAddr[1]
    print("out of ready to receive")
    
    # Checking if there is a card
    if (upcode == 1):
        print (" Taking Picture and upload to MS")
        assescnc()
        res = requests.get('http://127.0.0.1:5000/isCard')
        bytesToSend = str.encode(res.text)
        UDPServerSocket.sendto(bytesToSend, address)
    
    # Checking OCR of the card
    if (upcode == 2):
        if(colNocr == 0):
            print (" Taking Picture")
            ocr_image()
            #class_upcode = classification()
            box = box_list.index(res.text) #Might need ta change the ocr function for this to work lul
            bytesToSend = str.encode(box)
            UDPServerSocket.sendto(bytesToSend, address)
            print (" out of protocol")
        if(colNocr == 1):
            print (" Assessing color")
            assescnc()
            res = requests.get('http://127.0.0.1:5000/whichCard')
            box = box_list.index(res.text)
            bytesToSend = str.encode(box)
            UDPServerSocket.sendto(bytesToSend, address)
