import re
from itertools import product
from datetime import datetime, timedelta
from typing import List, Dict, Any
import toolbelt

courses = []

def schedule(course_id, professor=None):
    listings = toolbelt.get_course_listings(course_id)
    sections = listings['sections']
    credits = listings['credit_amount']
    filtered_listings = []
    if professor is not None:
        for section in sections:
            if professor in section['professor(s)']:
                filtered_listings.append(section)
    else:
        filtered_listings = sections

    return {
        'course': course_id,
        'credits': credits,  # ✅ add this line
        'sections': filtered_listings
    }



potential_courses = [("CMSC320",None),
                     ("CMSC433", None),("BMIN210",None),("CMSC414",None),("MATH141",None),("INST104",None),("DATA110",None)]
sections = []
for course in potential_courses:
    course_id, professor = course
    sections.append(schedule(course_id, professor))




def convert_to_24_hour(time_str: str):
    return datetime.strptime(time_str.strip().lower(), "%I:%M%p").time()


def parse_meeting(meeting: Dict[str, Any]):
    if "days" not in meeting or "start_time" not in meeting or "end_time" not in meeting:
        return []  # Online/asynchronous section

    days = re.findall(r'Tu|Th|M|W|F', meeting["days"])
    start = convert_to_24_hour(meeting["start_time"])
    end = convert_to_24_hour(meeting["end_time"])

    return [{"day": day, "start": start, "end": end} for day in days]


def meetings_conflict(meetings1: List[Dict[str, Any]], meetings2: List[Dict[str, Any]]):
    for m1 in meetings1:
        for m2 in meetings2:
            if m1["day"] == m2["day"]:  # ✅ conflict check only for the SAME day
                if max(m1["start"], m2["start"]) < min(m1["end"], m2["end"]):
                    return True
    return False


def is_online(section: Dict[str, Any]) -> bool:
    for meeting in section.get("meeting_schedule", []):
        if "days" in meeting and "start_time" in meeting and "end_time" in meeting:
            return False
    return True


def build_valid_schedules_with_metadata(section_data_by_course: List[Dict[str, Any]],
                                        credit_range=(12, 18)) -> List[Dict[str, Any]]:
    from itertools import product

    valid_schedules = []

    # Filter and tag each section
    filtered_courses = []
    for course in section_data_by_course:
        course_id = course["course"]
        credits = course.get("credits", 3)

        valid_sections = [
            {
                **section,
                "course": course_id,
                "credits": credits
            }
            for section in course["sections"]
            if section.get("open_seats", 0) > 0
        ]

        if valid_sections:
            filtered_courses.append(valid_sections)

    # Try all combinations (1 section per course)
    for combo in product(*filtered_courses):
        total_credits = sum(sec["credits"] for sec in combo)
        if not (credit_range[0] <= total_credits <= credit_range[1]):
            continue

        meetings_list = []
        has_conflict = False

        for sec in combo:
            if is_online(sec):
                meetings_list.append([])  # no meeting blocks
            else:
                parsed = []
                for m in sec.get("meeting_schedule", []):
                    parsed.extend(parse_meeting(m))
                meetings_list.append(parsed)

        for i in range(len(meetings_list)):
            for j in range(i + 1, len(meetings_list)):
                if meetings_conflict(meetings_list[i], meetings_list[j]):
                    has_conflict = True
                    break
            if has_conflict:
                break

        if not has_conflict:
            valid_schedules.append({
                "total_credits": total_credits,
                "courses": combo
            })

    return valid_schedules



valid = build_valid_schedules_with_metadata(sections, credit_range=(1, 20))


def print_schedules(schedules: List[Dict[str, Any]]):
    if not schedules:
        print("❌ No valid schedules found.")
        return

    for i, sched in enumerate(schedules, 1):
        print(f"\n🗓️ Schedule {i} — Total Credits: {sched['total_credits']}")
        for course in sched["courses"]:
            print(
                f"  📘 {course['course']} — Section {course['section_id']} | {course['credits']} credits")
            print(
                f"     👨‍🏫 Professor(s): {', '.join(course['professor(s)'])}")
            for meeting in course.get("meeting_schedule", []):
                if "days" in meeting and "start_time" in meeting:
                    print(
                        f"     🕒 {meeting['days']} {meeting['start_time']}–{meeting['end_time']} @ {meeting['location']}")
                else:
                    print(
                        f"     💻 Online | {meeting.get('time', 'No details')} @ {meeting.get('location', 'Unknown')}")


# print(valid)
def get_current_week_dates():
    today = datetime.today()
    monday = today - timedelta(days=today.weekday())  # start of week (Monday)
    return {
        "M": monday,
        "Tu": monday + timedelta(days=1),
        "W": monday + timedelta(days=2),
        "Th": monday + timedelta(days=3),
        "F": monday + timedelta(days=4),
    }
# def format_events(schedule):
#     events = []
#     current_week = get_current_week_dates()

#     for course in schedule["courses"]:
#         if is_online(course):
#             # Add as all-day event on Monday for visibility
#             events.append({
#                 "title": f"{course['course']} {course['section_id']} (Online)",
#                 "start": datetime.today().date().isoformat(),
#                 "allDay": True,
#                 "backgroundColor": "#ccccff",  # Optional: give it a light blue background
#                 "borderColor": "#8888ff"
#             })
#         else:
#             for m in course.get("meeting_schedule", []):
#                 if "days" in m:
#                     days = re.findall(r'Tu|Th|M|W|F', m["days"])
#                     for d in days:
#                         if d not in current_week:
#                             continue
#                         date = current_week[d]
#                         start = convert_to_24_hour(m["start_time"])
#                         end = convert_to_24_hour(m["end_time"])
#                         start_dt = datetime.combine(date.date(), start)
#                         end_dt = datetime.combine(date.date(), end)
#                         events.append({
#                             "title": f"{course['course']} {course['section_id']}",
#                             "start": start_dt.isoformat(),
#                             "end": end_dt.isoformat(),
#                         })
#     return events

def format_events(schedule):
    events = []
    online_only_courses = []
    current_week = get_current_week_dates()

    for course in schedule["courses"]:
        course_title = f"{course['course']} {course['section_id']}"
        meetings = course.get("meeting_schedule", [])
        has_scheduled_meeting = any("days" in m and "start_time" in m for m in meetings)
        has_online_marker = any("ONLINE" in m.get("location", "").upper() for m in meetings)

        # Case: Pure online class (no scheduled meetings)
        if has_online_marker and not has_scheduled_meeting:
            online_only_courses.append({
                "title": course_title,
                "professors": course["professor(s)"],
                "location": "ONLINE",
                "notes": meetings[0].get("time", "See ELMS for details")
            })
            continue  # Skip calendar

        # Add scheduled meetings to calendar
        for m in meetings:
            if "days" in m and "start_time" in m:
                days = re.findall(r'Tu|Th|M|W|F', m["days"])
                for d in days:
                    if d not in current_week:
                        continue
                    date = current_week[d]
                    start = convert_to_24_hour(m["start_time"])
                    end = convert_to_24_hour(m["end_time"])
                    start_dt = datetime.combine(date.date(), start)
                    end_dt = datetime.combine(date.date(), end)
                    events.append({
                        "title": course_title,
                        "start": start_dt.isoformat(),
                        "end": end_dt.isoformat(),
                        "backgroundColor": "red" if has_online_marker else None,
                        "borderColor": "#4caf50" if has_online_marker else None
                    })

    return events, online_only_courses
