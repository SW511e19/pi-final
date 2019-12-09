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
from random import randint
from time import strftime
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

globals()['upcode'] = 0
globals()['boxlist'] = () #Da tuple lmao
globals()['colNocr'] = 0

#Setting up the interface for selecting box order
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    surname = TextField('Surname:', validators=[validators.required()])
    
def get_time():
    time = strftime("%Y-%m-%dT%H:%M")
    return time

@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    if request.method == 'POST':
        sort_type=request.form['sorttype']
        globals()['colNocr'] = sort_type
        box1=request.form['box1']
        box2=request.form['box2']
        box3=request.form['box3']
        box4=request.form['box4']
        box5=request.form['box5']
        box6=request.form['box6']
        box7=request.form['box7']
        globals()['boxlist'] = (box1, box2, box3, box4, box5, box6, box7)
        flash('Sorting for: [{}] Box 1 : ({}),Box 2 : ({}), Box 3 : ({}), Box 4 : ({}), Box 5 : ({}), Box 6 : ({}), Box 7 : ({}),'.format(sort_type, box1, box2, box3, box4, box5, box6, box7))
        

    return render_template('index.html', form=form)

if __name__ == "__main__":
    app.run()


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
