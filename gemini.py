import google.generativeai as genai
from google.generativeai import types
import PyPDF2
import string
import toolbelt
import os

prompt = ""
UPLOAD_FOLDER = 'uploads'
API_KEY = "AIzaSyCzg3wk8xybsgVoWup8DqsRmajsdb1snD0"

def clean_text(text):
    printable = set(string.printable)
    return ''.join(filter(lambda x: x in printable, text))

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def get_uploaded_pdf_path():
    files = os.listdir(UPLOAD_FOLDER)
    if not files:
        raise FileNotFoundError("No uploaded PDF found.")
    return os.path.join(UPLOAD_FOLDER, files[0])

def askAgent(instruction, data):
    if (instruction == "PDF"):
        # Converting Audit PDf to text
        pdf_path = get_uploaded_pdf_path()
        pdf_text = extract_text_from_pdf(pdf_path)
        text = clean_text(pdf_text).strip()
        prompt = f"""
    This is a student course audit for the University of Maryland. Your job is to be a student advisor and help with building the course schedule for next semester. I need you to intepret each section of information. 
    Your output should be many courses (atleast 20) that would be most beneficial for the student to take. Find specific course ID's by using the tools I gave you.
    Here is student's degree audit:
    {text}
    \n
    """
        return prompt
    elif (instruction == "AddOn"):
        prompt += f"""Consider the following restriction given by the user {data}. Use the tools I have given you to ensure the restrictions are met"""
    elif (instruction == "Ask"):
        # Setting tools
        declarations = [toolbelt.get_course_listings_declaration,toolbelt.get_courses_by_dept_declaration,toolbelt.get_courses_by_gened_declaration,toolbelt.get_professor_grades_declaration]

        # Initialize the client and model
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            tools=[{"function_declarations": declarations}]
        )
        prompt = data
        prompt += "Fetch course ID's for the courses that you think would be of interest to the user."
        prompt += "Do NOT include courses that the user has already taken, these can be found in the degree audit they have submitted. Make sure you suggest atleast 20 courses"
        prompt += "Make sure to enumerate the courses you suggest, like 1. 2. 3."
        response = model.generate_content(prompt)
        print(response)
        return response.candidates[0].content.parts[0].text

