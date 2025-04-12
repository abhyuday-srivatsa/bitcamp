from google import genai
from google.genai import types
import PyPDF2
import string
import toolbelt
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

pdf_path = "audit.pdf"
pdf_text = extract_text_from_pdf(pdf_path)
# print(clean_text(pdf_text).strip())
declarations = [toolbelt.get_course_listings_declaration,toolbelt.get_courses_by_dept_declaration,toolbelt.get_courses_by_gened_declaration,toolbelt.get_professor_grades_declaration]
tools = types.Tool(function_declarations=declarations)
config = types.GenerateContentConfig(tools=[tools])
client = genai.Client(api_key="AIzaSyCzg3wk8xybsgVoWup8DqsRmajsdb1snD0")
prompt = f"""
This is a student course audit for the University of Maryland. Your job is to be a student advisor and help with building the course schedule for next semester. I need you to intepret each section of information. 

Here is student's degree audit:
{pdf_text}
"""

# prompt=f"""
# Get the grade distribution for CMSC320
# """
contents = [
    types.Content(
        role="user",parts=[types.Part(text=prompt)]
    )
]
response = client.models.generate_content(
    model="gemini-2.0-flash", contents=contents, config=config
)
# print(response.candidates[0].content.parts[0].function_call)
print(response.candidates[0].content)

