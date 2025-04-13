from flask import Flask, request, jsonify, render_template, flash, redirect, make_response, url_for

from werkzeug.utils import secure_filename

from gemini import askAgent
import requests
import uuid
import os
import gemini
import toolbelt

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "goon"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

conversation_prompt = ""

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
            if os.path.exists(app.config['UPLOAD_FOLDER']):
                for existing_file in os.listdir(app.config['UPLOAD_FOLDER']):
                    existing_file_path = os.path.join(app.config['UPLOAD_FOLDER'], existing_file)
                    if os.path.isfile(existing_file_path):
                        os.remove(existing_file_path)

            filename = secure_filename(str(uuid.uuid4()))
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + '.pdf'))

            global conversation_prompt
            conversation_prompt += askAgent("PDF", "")

            return render_template('conversation.html')
    else:
        return render_template("home.html")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/conversation')
def upload():
    return render_template("conversation.html")

@app.route('/tinder', methods=['GET', 'POST'])
def tinder():
    return render_template("tinder.html")

@app.route('/schedule')
def schedule():
    return render_template("schedule.html")

@app.route('/ask_agent', methods=['POST'])
def ask_agent():
    global conversation_prompt

    data = request.json
    user_text = data.get('input', '')

    conversation_prompt += f"\nUser: {user_text}\n"
    return ''

@app.route('/final_agent', methods=['POST'])
def final_agent():
    global conversation_prompt
    result = askAgent("Ask", conversation_prompt)
    return jsonify({'response': result})

@app.route('/get_courses', methods=['POST'])
def get_courses():
    data = request.json
    courseID = data.get('input', '')
    print("GETTING: ", courseID)
    result = toolbelt.get_course_listings(courseID)
    return jsonify({'response': result})

@app.route('/get_grades', methods=['POST'])
def get_grades():
    data = request.json
    professor = data.get('professor')
    courseID = data.get('courseID')

    result = toolbelt.get_professor_grades(professor, courseID)
    return jsonify({'response': result})


if __name__ == '__main__':
    app.run(debug=True, port=5001)