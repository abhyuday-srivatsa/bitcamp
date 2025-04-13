from flask import Flask, request, jsonify, render_template, flash, redirect, make_response, url_for, session

from werkzeug.utils import secure_filename

from gemini import askAgent
import requests
import uuid
import os
import gemini
import re
from itertools import product
from datetime import datetime, timedelta
from typing import List, Dict, Any
import toolbelt,scheduler

user_reqs = None
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
        return render_template("home.html", title="Cinder: Home")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/chat')
def upload():
    return render_template("conversation.html", title="Chat with Cinder")

@app.route('/tinder', methods=['GET', 'POST'])
def tinder():
    return render_template("tinder.html", title="Match")

# @app.route('/schedule')
# def schedule():
# #     return render_template("schedule.html", title="Build your schedule")
# @app.route("/schedule")
# def show_schedule():
#     all_schedules = scheduler.build_valid_schedules_with_metadata(scheduler.sections, credit_range=(12, 18))

#     if not all_schedules:
#         return "No valid schedules found."

#     best_schedule = all_schedules[0]  # or let user pick one
#     events = scheduler.format_events(best_schedule)  # converts it to calendar-compatible blocks
#     print(events)
#     return render_template("schedule.html", events=events)
@app.route("/generate_schedule", methods=['POST'])
def generate_schedule():
    data = request.json
    course_list = data.get('input', [])

    session["dynamic_courses"] = course_list
    return redirect(url_for("show_dynamic_schedules"))

@app.route("/dynamic_schedule", methods=['GET'])
def show_dynamic_schedules():
    dynamic = session.get("dynamic_courses", [])
    dynamic_tuples = [tuple(sublist) for sublist in dynamic]
    print(dynamic_tuples)
    scheduler.startup(dynamic_tuples)
    all_schedules = scheduler.build_valid_schedules_with_metadata(scheduler.sections, credit_range=(1,20))
    formatted = []
        
    for sched in all_schedules:
        events, online = scheduler.format_events(sched)
        formatted.append({
            "total_credits": sched["total_credits"],
            "events": events,
            "online_courses": online
        })

    return render_template("schedule.html", schedules=formatted)

'''
@app.route("/schedule")
def show_schedules():
    print("goes here!")
    print(user_reqs)
    scheduler.startSchedule(user_reqs)
    return render_template("schedule.html", schedules=scheduler.formatted)

@app.route("/set_sections",methods=["POST"])
def set_sections():
    global user_reqs
    if request.method == "POST":
        data = request.json
        info = data.get('input','')
        user_reqs = info
        return jsonify({'status': 'ok'})
    return "BAD"
'''
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
    app.run(debug=True, port=5000)