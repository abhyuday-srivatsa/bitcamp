from flask import Flask, request, jsonify, render_template, flash, redirect, make_response, url_for

from werkzeug.utils import secure_filename

import requests
import uuid
import os

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "goon"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

@app.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(str(uuid.uuid4()))
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + '.pdf'))
            return redirect('/conversation')
    else:
        return render_template("home.html", title="Cinder: Home")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/chat')
def upload():
    return render_template("conversation.html", title="Chat with Cinder")

@app.route('/match')
def tinder():
    return render_template("tinder.html", title="Match")

@app.route('/schedule')
def schedule():
    return render_template("schedule.html", title="Build your schedule")

if __name__ == '__main__':
    app.run(debug=True, port=5001)