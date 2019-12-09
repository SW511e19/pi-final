from random import randint
from time import strftime
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

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
        box1=request.form['box1']
        box2=request.form['box2']
        box3=request.form['box3']
        box4=request.form['box4']
        box5=request.form['box5']
        box6=request.form['box6']
        box7=request.form['box7']

        flash('Sorting for: [{}] Box 1 : ({}),Box 2 : ({}), Box 3 : ({}), Box 4 : ({}), Box 5 : ({}), Box 6 : ({}), Box 7 : ({}),'.format(sort_type, box1, box2, box3, box4, box5, box6, box7))

    return render_template('index.html', form=form)

if __name__ == "__main__":
    app.run()
