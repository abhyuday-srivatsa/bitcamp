import requests, json
from bs4 import BeautifulSoup
#function declarations for model
get_course_listings_declaration = {
    "name": "get_course_listings",
    "description": "Retrieves the current course sections, professors, seats, and locations for a specific course.",
    "parameters": {
        "type": "object",
        "properties": {
            "course_id": {
                "type": "string",
                "description": "The ID of the course for which to retrieve listings. In form of DEPTNUMNUMNUM"
            }
        },
        "required": ["course_id"],
    },
}

get_professor_grades_declaration = {
    "name": "get_professor_grades",
    "description": "Retrieves the grade distribution for a specific professor or course.",
    "parameters": {
        "type": "object",
        "properties": {
            "professor": {
                "type": "string",
                "description": "The ID of the professor whose grades are requested (optional)"
            },
            "course": {
                "type": "string",
                "description": "The course id for which to retrieve grades (optional). Course id in format of DEPTABVNUMNUMNUM"
            }
        },
        "required": [],
    },
}

get_courses_by_gened_declaration = {
    "name": "get_courses_by_gened",
    "description": "Retrieves all courses that fall under a specific general education requirement (Gened).",
    "parameters": {
        "type": "object",
        "properties": {
            "gened": {
                "type": "string",
                "description": "The ID of the Gened for which to retrieve courses. Found in course audit."
            },
            "page_number": {
                "type": "integer",
                "description": "The page number for which to retrieve courses (starting from 1). More pages can be accessed for more courses."
            }
        },
        "required": ["gened"],
    },
}

get_courses_by_dept_declaration = {
    "name": "get_courses_by_dept",
    "description": "Retrieves all courses that fall under a specific department.",
    "parameters": {
        "type": "object",
        "properties": {
            "dept": {
                "type": "string",
                "description": "The ID of the department for which to retrieve courses. Can be found in course audit."
            },
            "page_number": {
                "type": "integer",
                "description": "The page number for which to retrieve courses (starting from 1). More pages can be accessed for more courses."
            }
        },
        "required": ["dept"],
    },
}

#gets current course listings for particular course
def get_course_listings(course_id):
    try:
        term_id = "202508"
        # term_id = "202408"
        url = 'https://app.testudo.umd.edu/soc/search?courseId='+str(course_id)+'&sectionId=&termId='+str(term_id)+'&_openSectionsOnly=on&creditCompare=%3E%3D&credits=0.0&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on'
        page = requests.get(url)
        scraper = BeautifulSoup(page.content,'html.parser')
        sections = scraper.find_all('div',class_= "section")
        if sections == []:
            return {'msg':'The course you are looking for either does not exist or is not being offered.'}
        #get number of credits
        credits = int(scraper.find('span',class_="course-min-credits").text.strip())
        #get course description
        desc = scraper.find('div',class_='approved-course-texts-container').text.strip().replace("\n","")
        #get gen-eds (if applicable)
        geneds = scraper.find_all('span',class_="course-subcategory")
        if geneds != []:
            temp = []
            for gened in geneds:
                temp.append(gened.text.strip().replace("\n","").replace("\t",""))
            geneds = temp
        else:
            geneds = "None"
        complete_sections = []
        for section in sections:
            #get section id
            section_id = section.find('span',class_='section-id').text.strip()
            #get professor(s)
            professor = []
            for p in section.find_all('span',class_='section-instructor'):
                professor.append(p.text.strip())
            #get schedule
            meeting_days = []
            if section.find('span',class_='section-days') !=None:
                days = section.find_all('span',class_='section-days')
                class_start = section.find_all('span',class_='class-start-time')
                class_end = section.find_all('span',class_='class-end-time')
                location = section.find_all('span',class_='class-building')
                index = 0
                for index in range(0,len(days)):
                    meeting_days.append({'days':days[index].text.strip(),'start_time':class_start[index].text.strip(),'end_time':class_end[index].text.strip(),'location':location[index].text.strip().replace("\n","")})
            if section.find('span',class_='elms-class-message') !=None:
                meeting_days.append({'time':section.find('span',class_='elms-class-message').text.strip(),'location':section.find('span',string='ONLINE').text.strip()})
            #get seat counts
            total_seats = section.find('span',class_='total-seats-count').text.strip()
            open_seats = section.find('span',class_='open-seats-count').text.strip()
            waitlist_count = 0
            holdfile_count=0
            if section.find('span',class_='waitlist has-waitlist') !=None:
                waitlist_count = section.find_all('span',class_='waitlist-count')[0].text.strip()
                holdfile_count = section.find_all('span',class_='waitlist-count')[1].text.strip()
                
            else:
                holdfile_count = "N/A"
            complete_sections.append({'section_id':section_id,
                            'professor(s)':professor,
                            'meeting_schedule':meeting_days,
                            'total_seats':int(total_seats),
                            'open_seats':int(open_seats),
                            'waitlist':int(waitlist_count),
                            'holdfile':int(holdfile_count) if holdfile_count!="N/A" else 0
                            })
        return {
                'course_name':f'{str(scraper.find('div',class_='course-id').text)}: {scraper.find('span', class_='course-title').text.strip()}',
                'credit_amount':credits,'course_description':desc,
                'gen-eds satisifed':geneds,
                'sections':complete_sections
                }
    except:
        return None


#gets reviews for professor teaching specific course
def get_professor_ratings(professor_name,review_filter):
    url = 'https://planetterp.com/api/v1/professor?name='+str(professor_name)+'&reviews=true'
    data = requests.get(url).json()
    avg_rating = data['average_rating']
    courses_taught = data['courses']
    professor_name = data['name']
    professor_reviews = data['reviews']
    if review_filter!=None:
        courses_taught = review_filter
        filtered_reviews = []
        course_total = 0
        for review in professor_reviews:
            if review['course'] == review_filter:
                filtered_reviews.append(review)
                course_total+=review['rating']
        avg_rating = course_total/len(filtered_reviews)
        professor_reviews = filtered_reviews[:10]
    return {
        'average_rating':avg_rating,
        'courses':courses_taught,
        'name':professor_name,
        'reviews':professor_reviews
    }
#gets grade distribution for 
def get_professor_grades(professor=None,course=None):
    desc = ""
    if professor is None and course is not None:
        url = 'https://planetterp.com/api/v1/grades?course='+str(course)
        desc = "Response contains overall grade data for "+course
    elif course is None and professor is not None:
         url = 'https://planetterp.com/api/v1/grades?professor='+str(professor)
         desc = "Response contains overall grade data for professor "+professor
    elif course is not None and professor is not None:
         url = 'https://planetterp.com/api/v1/grades?professor='+str(professor)+'&course='+str(course)
         desc = "Response contains grade data for "+str(professor)+" teaching "+str(course)
    else:
        desc = "Invalid options"
    data = requests.get(url).json()
    try:
        grade_key=[
        'A+',"A",'A-','B+', "B",'B-','C+','C','C-','D+','D','D-','F','W','Other'
        ]
        grade_totals = {
        "A+": 0,
        "A": 0,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "W": 0,
        "Other": 0
        }
        for section in data:
            dict_cvt = json.dumps(section)
            dict_cvt = json.loads(dict_cvt)
            for field in dict_cvt:
                if field != 'course' and field!='professor' and field!='semester' and field!='section' and field!="{":
                    grade_totals[field]+=dict_cvt[field]
        grade_list = []
        for grade in grade_totals:
            count = grade_totals.get(grade)
            for x in range(0,count):
                grade_list.append(grade_key.index(grade))
        grade_avg = 0
        for v in grade_list:
            grade_avg+=v
        grade_avg = int(grade_avg/len(grade_list))
        grade_avg = grade_key[grade_avg]
        return {'professor':professor,'course':course,'grade_totals':grade_totals,'response_description':desc,'avg_grade':grade_avg}
    except:
        return {'professor':professor,'course':course,'grade_totals':None,'response_description':desc,'avg_grade':None}

#gets all courses by a particular gen-ed
def get_courses_by_gened(gened,page_number):
    url = "https://api.umd.io/v1/courses?gen_ed="+str(gened)+"&page="+str(page_number)
    return requests.get(url).json()

#get courses by department
def get_courses_by_dept(dept,page_number):
    url = "https://api.umd.io/v1/courses?det_id="+str(dept)+"&page="+str(page_number)
    return requests.get(url).json()