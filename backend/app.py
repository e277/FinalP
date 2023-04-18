from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import datetime
import mysql.connector
import bcrypt


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'comp3161-final-project'
# Configure the JWT options
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
jwt = JWTManager(app)

# import the database configuration from config.py
from config import db_config

# Register - ezra
@app.route('/api/register', methods=['POST'])
def register():
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # get the data from the request
    data = request.get_json()
    username = data['username']
    firstName = data['firstName']
    lastName = data['lastName']

    salt = bcrypt.gensalt()
    password = data['password']
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    # insert the user to the database, if user name already exist return error else create user
    try:
        # get user from the database
        cursor.execute("""
            SELECT username FROM Accounts WHERE username = %s
        """, (username,))
        user = cursor.fetchone()
        if user is not None:
            return jsonify({'error': 'User already exist'}), 400
        else:
            # create user
            # check if Accounts table is empty, if it is then set the user as admin and save that user to Admins table
            # elif Accounts table is not empty, then set the user as student and save that user to Students table
            # else set the user as lecturer and save that user to Lecturers table
            cursor.execute("""
                SELECT typeName FROM Accounts WHERE typeName LIKE 'admin'
            """)
            admin = cursor.fetchone()
            if admin is None:
                cursor.execute("""
                    INSERT INTO Accounts (typeName, username, password) VALUES (%s, %s, %s)
                """, ('admin', username, password_hash))
                conn.commit()
                cursor.execute("""
                    SELECT typeID FROM Accounts WHERE username = %s
                """, (username,))
                user = cursor.fetchone()
                # print(user)
                cursor.execute("""
                    INSERT INTO Admins (firstName, lastName, typeID) VALUES (%s, %s, %s)
                """, (firstName, lastName, user[0]))
                conn.commit()
                return jsonify({'message': 'Admin created successfully'}), 201
            else:
                cursor.execute("""
                    INSERT INTO Accounts (typeName, username, password) VALUES (%s, %s, %s)
                """, ('lecturer', username, password_hash))
                conn.commit()
                cursor.execute("""
                    SELECT typeID FROM Accounts WHERE username = %s
                """, (username,))
                user = cursor.fetchone()
                # print(user)
                cursor.execute("""
                    INSERT INTO Lecturers (firstName, lastName, typeID) VALUES (%s, %s, %s)
                """, (firstName, lastName, user[0]))
                conn.commit()
                return jsonify({'message': 'Lecturer created successfully'}), 201
    except IndexError:
        return jsonify({'error': 'User already exist'}), 400


# Login - ezra
@app.route('/api/login', methods=['POST'])
def login():
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # get the data from the request
    data = request.get_json()
    username = data['username']
    password = data['password']

    # get user from the database
    try:
        cursor.execute("""
            SELECT * FROM Accounts WHERE username = %s
        """, (username,))
        user = cursor.fetchone()
        # check if user exist
        # print(user)
        if user is not None:
            # check if password is correct
            if bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                # create access token
                access_token = create_access_token(identity=user[0])
                # check if user is admin, student or lecturer
                if user[1] == 'admin':
                    cursor.execute("""
                        SELECT * FROM Admins WHERE typeID = %s
                    """, (user[0],))
                    admin = cursor.fetchone()
                    return jsonify({'message': 'Login successful', 'access_token': access_token, 'user': admin[3]}), 200
                elif user[1] == 'lecturer':
                    cursor.execute("""
                        SELECT * FROM Students WHERE typeID = %s
                    """, (user[0],))
                    student = cursor.fetchone()
                    return jsonify({'message': 'Login successful', 'access_token': access_token, 'user': student[3]}), 200
                else:
                    cursor.execute("""
                        SELECT * FROM Lecturers WHERE typeID = %s
                    """, (user[0],))
                    lecturer = cursor.fetchone()
                    return jsonify({'message': 'Login successful', 'access_token': access_token, 'user': lecturer[3]}), 200
            else:
                return jsonify({'error': 'Invalid credential'}), 401
        else:
            return jsonify({'error': 'User does not exist'}), 401
    except IndexError:
        return jsonify({'error': 'User does not exist'}), 401


# Logout - ezra
@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        blacklist = set()
        jwt_token = request.headers.get('Authorization')
        if jwt_token:
            jwt_token = jwt_token.split(" ")[1]
            blacklist.add(jwt_token)
            # print(blacklist)
            return jsonify({'message': 'Logout successful'}), 200
        else:
            return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 401


# @app.route('/api/refresh', methods=(['POST']))
# @jwt_refresh_token_required
# def refresh():
#     # Refresh the users access token
#     current_user = get_jwt_identity()
#     access_token = create_access_token(identity=current_user)

#     # Return the new access token
#     return jsonify(access_token=access_token)


# @app.route('/api/protected', methods=['GET'])
# @jwt_required()
# def protected():
#     try:
#         current_user = get_jwt_identity()
#         name = current_user[1]
#         return jsonify({'message': 'Hello, {}'.format(name)}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 401




# Retrieve all the courses - ezra
@app.route('/api/courses', methods=['GET'])
def get_courses():
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Courses;")
    courses = []
    # print(cursor.fetchall())
    try:
        # get all courses
        for courseID, courseName, courseDescription in cursor:
            course = {}
            course['Course ID'] = courseID
            course['Course Name'] = courseName
            course['Course Description'] = courseDescription
            courses.append(course)
        cursor.close()
        conn.close()
        return jsonify({'courses': courses}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Retrieve courses for a particular student - ezra
@app.route('/api/courses/<int:student_id>', methods=['GET'])
def get_student_courses(student_id):
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # check if student exist
        cursor.execute("""
            SELECT studentID FROM Students WHERE studentID = %s
        """, (student_id,))
        student = cursor.fetchone()
        # if the student exist, get all courses else return error
        # join the courses and enrolled tables to get the courses for a particular student
        if student is not None:
            cursor.execute("""
                SELECT c.courseName, c.courseDescription
                FROM Courses AS c Right JOIN Enrollments AS e ON c.courseID = e.courseID 
                WHERE e.studentID = %s
            """, (student_id,))
            courses = []
            for courseName, courseDescription in cursor:
                course = {}
                course['Course Name'] = courseName
                course['Course Description'] = courseDescription
                courses.append(course)
            cursor.close()
            conn.close()
            return jsonify({'courses for student': courses}), 200
        else:
            return jsonify({'error': 'Student not found'}), 400
    except IndexError:
        return jsonify({'error': 'Courses not found'}), 404

# Retrieve courses taught by a particular lecturer - ezra
@app.route('/api/courses/lecturer/<int:lecturer_id>', methods=['GET'])
def get_lecturer_courses(lecturer_id):
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # check if lecturer exist
        cursor.execute("""
            SELECT lecID FROM Enrollments WHERE lecID = %s
        """, (lecturer_id,))
        lecturer = cursor.fetchall()
        # if the lecturer exist, get all courses else return error
        if lecturer is not None:
            cursor.execute("""
                SELECT c.courseName, c.courseDescription 
                FROM Courses As c LEFT JOIN Enrollments AS e ON c.courseID = e.courseID
                WHERE e.lecID = %s
            """, (lecturer_id,))
            courses = []
            for courseName, courseDescription in cursor:
                course = {}
                course['Course Name'] = courseName
                course['Course Description'] = courseDescription
                courses.append(course)
            cursor.close()
            conn.close()
            return jsonify({'Courses for lecturer': courses}), 200
        else:
            return jsonify({'error': 'Lecturer not found'}), 400
    except IndexError:
        return jsonify({'error': 'Courses not found'}), 404

# My PARTS
#
# Register for Course - Condoleezza
@app.route('/api/register_for_course', methods=['POST'])
def register_for_course():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        data = request.get_json()
        student_id = data['student_id']
        course_id = data['course_id']

        # Check if the course exists
        cursor.execute("SELECT courseID FROM Courses WHERE courseID=%s", (course_id,))
        result = cursor.fetchone()
        if not result:
            return make_response({'error': 'Course does not exist'}, 404)

        # Check if course has a lecturer assigned
        cursor.execute("SELECT lec.lecID FROM Lecturers AS lec LEFT JOIN Accounts AS ac ON ac.typeID = lec.typeID AND ac.typeName = 'lecturer'")
        result = cursor.fetchone()
        if not result:
            return make_response({'error': 'This course does not have a lecturer assigned yet'}, 400)
        
        lecturer_id = result[0]

        # Check if the student is already enrolled in the course
        cursor.execute("SELECT * FROM Enrollments WHERE studentID = %s AND courseID = %s", (student_id, course_id))
        result = cursor.fetchone()
        if result is not None:
            return make_response({'error': 'Student is already enrolled in the course'}, 400)
        else:
            # Assign lecturer to the course
            cursor.execute("INSERT INTO Enrollments (courseID, lecID) VALUES (%s, %s)", (course_id, lecturer_id))
            # Update record with Student ID
            cursor.execute("UPDATE Enrollments SET studentID = %s WHERE enrollmentID = LAST_INSERT_ID()", (student_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Course registration successful'}), 201
    except Exception as e:
        return make_response({'error': str(e)}, 400)
    

# Retrieve Members - Condoleezza
@app.route('/api/retrieve_members/<course_id>', methods=['GET'])
def retrieve_members(course_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT e.courseID, e.studentID, s.firstName, s.lastName, e.lecID FROM Enrollments AS e LEFT JOIN Students AS s ON e.studentID = s.studentID WHERE e.courseID =%s", (course_id,))
        members = []
        for courseID, studentID, firstName, lastName, lecID in cursor:
            member = {}
            member['courseID'] = courseID
            member['studentID'] = studentID
            member['firstName'] = firstName
            member['lastName'] = lastName
            member['lecID'] = lecID
            members.append(member)
        cursor.close()
        conn.close()
        return jsonify({'members': members})
    except Exception as e:
        return make_response({'error': str(e)}, 400)

# Add Course Content - Condoleezza
@app.route('/api/add_course_content/<course_id>', methods=['POST'])
def add_course_content(course_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        data = request.get_json()
        section_title = data['section_title']
        item_type = data['item_type']
        item_title = data['item_title']
        item_content = data['item_content']

        # Checking if the course id exists in Enrollments 
        cursor.execute("SELECT courseID, lecID FROM Enrollments WHERE courseID = %s", (course_id,))
        result = cursor.fetchall()
        print("result", result)
        # Creates content for a particular course
        if result is not None:
            cursor.execute("INSERT INTO Sections (courseID, sectionTitle) VALUES (%s, %s)", (result[0][0], section_title))
            
            # Retrieve sectionID from the Sections table
            cursor.execute("SELECT sectionID FROM Sections WHERE courseID = %s", (course_id,))
            secID = cursor.fetchall()
            print("secID", secID[0][0])
            # Insert new section item
            cursor.execute("INSERT INTO SectionItems (sectionId, lecId, itemType, itemTitle, itemContent) VALUES \
                           (%s,%s,%s,%s,%s)", (secID[0][0], result[0][1], item_type, item_title, item_content))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': 'Course content added successfully.'})
    except Exception as e:
        return make_response({'error': str(e)}, 400)

# Retrieve Course Content - Condoleezza
@app.route('/api/retrieve_course_content/<course_id>', methods=['GET'])
def retrieve_course_content(course_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT s.courseID, s.sectionTitle, i.sectionID, i.itemID, i.itemType, i.itemTitle, i.itemContent FROM SectionItems AS i LEFT JOIN Sections AS s ON s.sectionID = i.sectionID WHERE s.courseID =%s", (course_id,))
        course_content = []
        for courseID, sectionTitle, sectionID, itemID, itemType, itemTitle, itemContent in cursor:
            content = {}
            content['courseID'] = courseID
            content['sectionTitle'] = sectionTitle
            content['sectionID'] = sectionID
            content['itemID'] = itemID
            content['itemType'] = itemType
            content['itemTitle'] = itemTitle
            content['itemContent'] = itemContent
            course_content.append(content)
        cursor.close()
        conn.close()
        return jsonify({'course_content': course_content})
    except Exception as e:
        return make_response({'error': str(e)}, 400)



# Retrieve all calender events for a particular course - ezra
@app.route('/api/courses/<int:course_id>/events', methods=['GET'])
def get_course_events(course_id):
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # check if course exist
        cursor.execute("""
            SELECT courseID FROM Courses WHERE courseID = %s
        """, (course_id,))
        course = cursor.fetchone()
        # if the course exist, get all events else return error
        if course is not None:
            cursor.execute("""
                SELECT * FROM CalenderEvents WHERE courseID = %s
            """, (course_id,))
            events = []
            for eventID, courseID, lecID, studentID, eventTitle, eventDescription, eventDate in cursor:
                event = {}
                event['eventID'] = eventID
                event['courseID'] = courseID
                event['lecID'] = lecID
                event['studentID'] = studentID
                event['eventTitle'] = eventTitle
                event['eventDescription'] = eventDescription
                event['eventDate'] = str(eventDate)
                events.append(event)
            cursor.close()
            conn.close()
            return jsonify({'events': events})
        else:
            return jsonify({'error': 'Course not found'}), 404
    except IndexError:
        return jsonify({'error': 'Events not found'}), 404

# Retrieve all calender events for a particular date for a particular student - ezra
@app.route('/api/courses/<string:date>/events/<int:student_id>', methods=['GET'])
def get_student_events(date, student_id):
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # check if student exist
        cursor.execute("""
            SELECT studentID FROM Enrollments WHERE studentID = %s
        """, (student_id,))
        student = cursor.fetchone()
        # if the student exist, get all events else return error
        if student is not None:
            cursor.execute("""
                SELECT e.courseID, e.studentID, c.eventTitle, c.eventDescription, c.eventDate 
                FROM CalenderEvents AS c 
                    LEFT JOIN Enrollments AS e ON e.courseID = c.courseID 
                WHERE e.studentID = %s AND c.eventDate = %s
            """, (student_id, date))
            events = []
            for courseID, studentID, eventTitle, eventDescription, eventDate in cursor:
                event = {}
                event['courseID'] = courseID
                event['studentID'] = studentID
                event['eventTitle'] = eventTitle
                event['eventDescription'] = eventDescription
                event['eventDate'] = str(eventDate)
                events.append(event)
            cursor.close()
            conn.close()
            return jsonify({'events': events})
        else:
            return jsonify({'error': 'Student not found'}), 404
    except IndexError:
        return jsonify({'error': 'Events not found'}), 404


# Create a calender event for a particular course - ezra
@app.route('/api/courses/<int:course_id>/events', methods=['POST'])
def create_course_event(course_id):
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # get the data from the request
    data = request.get_json()
    # courseID = data['courseID']
    lecID = data['lecID']
    studentID = data['studentID']
    eventTitle = data['eventTitle']
    eventDescription = data['eventDescription']
    eventDate = data['eventDate']

    # get user from the database
    try:
        # check if course exist and if the lecturer is the one creating the event, a student is registered for the course already
        cursor.execute("""
            SELECT * FROM Courses WHERE courseID = %s
        """, (course_id,))
        course = cursor.fetchone()
        # if the course exist, get all events else return error
        if course is not None:
            cursor.execute("""
                SELECT e.lecID, e.studentID
                FROM Enrollments AS e LEFT 
                    JOIN Lecturers AS l ON e.lecID = l.lecID
                    LEFT JOIN Students AS s ON e.studentID = s.studentID
                WHERE e.courseID = %s AND e.lecID = %s AND e.studentID = %s
            """, (course_id, lecID, studentID))
            result = cursor.fetchone()
            # if the lecturer is the one creating the event, a student is registered for the course already
            if result is not None:
                # create the event
                cursor.execute("""
                    INSERT INTO CalenderEvents (courseID, lecID, studentID, eventTitle, eventDescription, eventDate)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (course_id, lecID, studentID, eventTitle, eventDescription, eventDate))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': 'Event created successfully.'}), 201
            else:
                return jsonify({'error': 'Lecturer or student not assigned'}), 404
        else:
            return jsonify({'error': 'Course not found'}), 404
    except IndexError:
        return jsonify({'error': 'Events not found'}), 404


        

# API routes

#Forum - Dukie
@app.route('/courses/<int:course_id>/forums', methods=['GET'])
def get_forums(course_id):

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM Courses WHERE courseID = %s""", (course_id,))
    course = cursor.fetchone()

    if course is not None:
        cursor.execute (""" SELECT * FROM DiscussionForums WHERE courseID = %s""", (course_id))
        forums = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify ({'forums' : forums}), 200
    else:
        return jsonify({'error': 'Course not found'}), 404

# Dukie
@app.route('/courses/<int:course_id>/forums', methods=['POST'])
def create_forum(course_id):

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    data = request.get_json()


    courseID = data['courseID']
    forumName = data['forumName']

    try:
        cursor.execute (""" SELECT courseID FROM Courses WHERE courseID = %s """, (course_id))
        course = cursor.fetchone()

        if course is not None:

            cursor.execute ("""INSERT INTO DiscussionForums (courseID, forumName) VALUES (%s, %s) """),(courseID, forumName)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify ({'message': 'Forum Created'}), 201
        else:
            return jsonify ({'error': 'Course not found'}), 404
        
    except IndexError:
        return jsonify({'error': 'Course not found'}), 404

#Thread - Dukie
@app.route('/forums/<int:forum_id>/threads', methods=['GET'])
def get_threads(forum_id):

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM DiscussionForums WHERE forumID = %s """, (forum_id,))
    forum = cursor.fetchone()

    if forum is not None:
        cursor.execute (""" SELECT * FROM DiscussionThreads WHERE forumID = %s""", (forum_id))
        threads = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify ({'threads' : threads}), 200
    else:
        return jsonify({'error': 'Forum not found'}), 404

# Dukie
@app.route('/forums/<int:forum_id>/threads', methods=['POST'])
def create_thread(forumID):

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    data = request.get_json()

    forumID = data['forumID']
    threadTitle = data['threadTitle']
    threadContent = data['threadContent']
    lecID = data['lecID']
    studentID = data['studentID']

    try:
        cursor.execute (""" SELECT forumID FROM DiscussionForums WHERE forumID = %s """, (forumID))

        forum = cursor.fetchone()

        if forum is not None:

            cursor.execute ("""INSERT INTO DiscussionThreads (forumID, threadTitle, threadContent, lecID, studentID ) VALUES (%s, %s, %s, %s, %s) """),(forumID, threadTitle, threadContent, lecID, studentID )

            conn.commit()
            cursor.close()
            conn.close()

            return jsonify ({'message': 'Thread Created'}), 201

        else:
            return jsonify ({'error': 'Forumn not found'}), 404
        
    except IndexError:
        return jsonify({'error': 'Forumn not found'}), 404

#Replies - Dukie
@app.route('/threads/<int:thread_id>/replies', methods=['POST'])
def create_reply(thread_id):

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    data = request.get_json()


    threadID = data['threadID']
    courseID = data['courseID']
    replyContent = data['replyContent']

    try:
        cursor.execute (""" SELECT threadID FROM DiscussionThreads WHERE threadID = %s """, (thread_id))
        thread = cursor.fetchone()

        if thread is not None:

            cursor.execute ("""INSERT INTO DiscussionThreadReplies (threadID, courseID, replyContent ) VALUES (%s, %s, %s,) """),(threadID, courseID, replyContent )
            
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify ({'message': 'Reply Sent'}), 201
        else:
            return jsonify ({'error': 'Thread not found'}), 404
        
    except IndexError:
        return jsonify({'error': 'Thread not found'}), 404
    
# Dukie
@app.route('/forums/<int:thread_id>/replies', methods=['GET'])
def get_replies(thread_id):

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        cursor.execute (""" SELECT threadID FROM DiscussionThreads WHERE threadID = %s """, (thread_id))
        thread = cursor.fetchone()

        if thread is not None:
            cursor.execute (""" SELECT * FROM DiscussionThreadReplies WHERE threadID = %s""", (thread_id))
            replies = cursor.fetchall()

            cursor.close()
            conn.close()

            return jsonify ({'replies' : replies}), 200
        else:
            return jsonify({'error': 'Thread not found'}), 404
        
    except IndexError:
        return jsonify({'error': 'Thread not found'}), 404



# REPORTS


# Main function
if __name__ == '__main__':
    app.run(debug=True, port=5001)

