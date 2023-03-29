from PyPDF2 import PdfReader
from faker import Faker
import random

fake = Faker()


# open the pdf file
pdf_file = PdfReader("C:/Users/Ezra Muir/Downloads/final_version_undergraduate_semester_ii_final_examination_timetable_a-z_1.pdf", strict=False)

# number of pages in the pdf file
number_of_pages = len(pdf_file.pages)

# get all the pages
key_words = [
    "ACCT", "ANAT", 
    "BAMS", "BIOC", "BIOL", "BIOT", "BMNG", "BOTN", 
    "CENG", "CHEM", "CHIN", "CLTR", "COMM", "COMP", "CVNG", 
    "DENT", "DIMA", 
    "ECNG", "ECON", "ECSE", "EDIT", "EDMC", "ELET", "ELNG", "ENGM", "ENGR", "EPNG", 
    "FILM", "FOUN", "FREN", 
    "GEOG", "GEOL", "GGEO", "GOVT", 
    "HIST", "HOSP", 
    "INFO", 
    "JAPA", 
    "LANG", "LAW", "LIBS", "LING", "LITS", 
    "MATH", "MDSC", "MGMT", "MICR", "MKTG", "MUSC", 
    "NURS", 
    "OESH", 
    "PHAL", "PHAR", "PHIL", "PHTH", "PHYL", "PHYS", "PSYC", 
    "SOCI", "SOWK", "SPAN", "SPCH", "SPKN", "STAT", "SWEN", 
    "THEO", "TOUR", 
    "ZOOL"
    ]

# loop through all the pages, choose 200 random courses if each line in the page contains a key word, print the line
random_courses = []
for i in range(number_of_pages):
    page = pdf_file.pages[i]
    page_content = page.extract_text()
    lines = page_content.split("\n")
    for line in lines:
        for key_word in key_words:
            if key_word in line:
                random_courses.append(line)
                break
random_courses = random.sample(random_courses, 203)


# Extract the course code and course name from the random courses list, store them in a dictionary with the course code as the key and the course name as the value
# For example, the course code is "ACCT 1001" and the course name is "Introduction to Financial Accounting", so anywhere a word has "Mon", "Tue", "Wed", "Thu", "Fri" in it, exclude everything from that word onwards

# create a dictionary to store the course code and course name
course_dict = {}
for course in random_courses:
    course_code = course.split(" ", 1)[0]
    course_name = course.split(" ", 1)[1]
    for word in course_name.split():
        if "Mon" in word or "Tue" in word or "Wed" in word or "Thu" in word or "Fri" in word:
            course_name = course_name.split(word, 1)[0]
            break
    course_dict[course_code] = course_name

# Insert the course code and course name into a sql file
with open('backend/insert_courses.sql', 'w', newline='') as course_file:
    for value in course_dict.values():
        courseName = value
        courseDescription = fake.text(max_nb_chars=200)
        lecID = fake.random_int(min=1, max=99)
        studentID = fake.random_int(min=1000, max=5999)
        course_file.write('INSERT INTO Courses (courseName, courseDescription, lecID, studentID) VALUES (' + ' "' + courseName + '", "' + courseDescription + '", ' + str(lecID) + ', ' + str(studentID) + ');\n')