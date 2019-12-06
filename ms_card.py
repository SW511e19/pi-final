from flask import Flask, url_for, send_from_directory, request
import logging, os
from werkzeug import secure_filename
from keras.models import model_from_json
from pathlib import Path
from keras.preprocessing import image
import numpy as np
from keras.applications import vgg16
from keras import backend as K
import os
import time
import uuid
import importlib
from PIL import Image, ImageChops

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

@app.route('/', methods = ['POST'])
def api_root():
    app.logger.info(PROJECT_HOME)
    if request.method == 'POST' and request.files['image']:
    	app.logger.info(app.config['UPLOAD_FOLDER'])
    	img = request.files['image']
    	img_name = secure_filename(img.filename)
    	create_new_folder(app.config['UPLOAD_FOLDER'])
    	saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
    	app.logger.info("saving {}".format(saved_path))
    	img.save(saved_path)
    	return send_from_directory(app.config['UPLOAD_FOLDER'],img_name, as_attachment=True)
 
@app.route('/isCard')
def isCard():
  class_label_names = [
        "not_card",
        "card"
    ]

  # Load the json file that contains the model's structure
  f = Path("model_structure_cnc.json")
  model_structure = f.read_text()

  # Recreate the Keras model object from the json data
  model = model_from_json(model_structure)

  # Re-load the model's trained weights
  model.load_weights("model_weights_cnc.h5")

  # Load an image file to test, resizing it to 64x64 pixels (as required by this model)
  img = image.load_img("uploads/currentCard.png", target_size=(224, 224))
  #img = image.load_img("green.png", target_size=(224, 224))
  # Convert the image to a numpy array
  image_array = image.img_to_array(img)

  # Add a forth dimension to the image (since Keras expects a bunch of images, not a single image)
  images = np.expand_dims(image_array, axis=0)

  # Normalize the data
  images = vgg16.preprocess_input(images)

  # Use the pre-trained neural network to extract features from our test image (the same way we did to train the model)
  feature_extraction_model = vgg16.VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
  features = feature_extraction_model.predict(images)

  # Given the extracted features, make a final prediction using our own model
  results = model.predict(features)

  # Since we are only testing one image with possible class, we only need to check the first result's first element
  single_result = results[0]
  
  # We will get a likelihood score for all 10 possible classes. Find out which class had the highest score.
  most_likely_class_index = int(np.argmax(single_result))
  class_likelihood = single_result[most_likely_class_index]

  # Get the name of the most likely class
  class_label = class_label_names[most_likely_class_index]
  K.clear_session()
  return class_label

@app.route('/whichCard')
def whichCard():
  return '1'
