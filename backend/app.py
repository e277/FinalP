from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import mysql.connector
import bcrypt

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'the-lengenadary-ezra'
# Configure the JWT options
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
# app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=14)
jwt = JWTManager(app)

# Database configuration
db_config = {'host': 'localhost', 'user': 'root', 'password': 'mysql-25', 'database': 'ourvle_clone'}


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
            SELECT * FROM Accounts WHERE username = %s
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
                SELECT * FROM Accounts WHERE typeID = 1
            """)
            admin = cursor.fetchone()
            if admin is None:
                cursor.execute("""
                    INSERT INTO Accounts (type, username, password) VALUES (%s, %s, %s)
                """, (1, username, password_hash))
                conn.commit()
                cursor.execute("""
                    SELECT * FROM Accounts WHERE username = %s
                """, (username,))
                user = cursor.fetchone()
                cursor.execute("""
                    INSERT INTO Admins (firstName, lastName, typeID) VALUES (%s, %s, %s)
                """, (firstName, lastName, user[0]))
                conn.commit()
                return jsonify({'message': 'Admin created successfully'}), 201
            else:
                cursor.execute("""
                    SELECT * FROM Accounts WHERE typeID = 2
                """)
                student = cursor.fetchone()
                if student is None:
                    cursor.execute("""
                        INSERT INTO Accounts (type, username, password) VALUES (%s, %s, %s)
                    """, (2, username, password_hash))
                    conn.commit()
                    cursor.execute("""
                        SELECT * FROM Accounts WHERE username = %s
                    """, (username,))
                    user = cursor.fetchone()
                    cursor.execute("""
                        INSERT INTO Students (firstName, lastName, typeID) VALUES (%s, %s, %s)
                    """, (firstName, lastName, user[0]))
                    conn.commit()
                    return jsonify({'message': 'Student created successfully'}), 201
                else:
                    cursor.execute("""
                        INSERT INTO Accounts (type, username, password) VALUES (%s, %s, %s)
                    """, (3, username, password_hash))
                    conn.commit()
                    cursor.execute("""
                        SELECT * FROM Accounts WHERE username = %s
                    """, (username,))
                    user = cursor.fetchone()
                    cursor.execute("""
                        INSERT INTO Lecturers (firstName, lastName, typeID) VALUES (%s, %s, %s)
                    """, (firstName, lastName, user[0]))
                    conn.commit()
                    return jsonify({'message': 'Lecturer created successfully'}), 201
    except IndexError:
        return jsonify({'error': 'User already exist'}), 400


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
                if user[1] == 1:
                    cursor.execute("""
                        SELECT * FROM Admins WHERE typeID = %s
                    """, (user[0],))
                    admin = cursor.fetchone()
                    return jsonify({'message': 'Login successful', 'access_token': access_token, 'user': admin[3]}), 200
                elif user[1] == 2:
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






# Retrieve all the courses
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
        for courseID, courseName, courseDescription, lecId, studentID, numberOfMembers in cursor:
            course = {}
            course['Course ID'] = courseID
            course['Course Name'] = courseName
            course['Course Description'] = courseDescription
            course['Lecturer ID'] = lecId
            course['Student ID'] = studentID
            course['Number of Members'] = numberOfMembers
            courses.append(course)
        cursor.close()
        conn.close()
        return jsonify({'courses': courses}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Retrieve courses for a particular student
@app.route('/api/courses/<int:student_id>', methods=['GET'])
def get_student_courses(student_id):
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # check if student exist
        cursor.execute("""
            SELECT * FROM Students WHERE studentID = %s
        """, (student_id,))
        student = cursor.fetchone()
        # if the student exist, get all courses else return error
        if student is not None:
            cursor.execute("""
                SELECT * FROM Courses WHERE studentID = %s
            """, (student_id,))
            courses = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({'courses': courses}), 200
        else:
            return jsonify({'error': 'Student not found'}), 404
    except IndexError:
        return jsonify({'error': 'Student not found'}), 404

# Retrieve courses taught by a particular lecturer
@app.route('/api/courses/lecturer/<int:lecturer_id>', methods=['GET'])
def get_lecturer_courses(lecturer_id):
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # check if lecturer exist
        cursor.execute("""
            SELECT * FROM Lecturers WHERE lecID = %s
        """, (lecturer_id,))
        lecturer = cursor.fetchone()
        # if the lecturer exist, get all courses else return error
        if lecturer is not None:
            cursor.execute("""
                SELECT * FROM Courses WHERE lecID = %s
            """, (lecturer_id,))
            courses = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({'courses': courses}), 200
        else:
            return jsonify({'error': 'Lecturer not found'}), 404
    except IndexError:
        return jsonify({'error': 'Courses not found'}), 404

# # My PARTS
# #
# # Register for Course 
# @app.route('/register_course', methods=['POST'])
# def register_course():
#     try:
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor()

#         data = request.get_json()
#         course_name = data['courseName']
#         lecturer_id = data['lecId']
#         cursor.execute('INSERT INTO Courses (courseName, lecId) VALUES (%s, %s)', (course_name, lecturer_id))
#         cursor.commit()
#         cursor.close()
#         conn.close()
#         return jsonify({'message': 'Course registered successfully'})
#     except Exception as e:
#         return make_response({'error': str(e)}, 400)
    

# # Retrieve Members
# @app.route('/members/<course_id>', methods=['GET'])
# def get_members(course_id):
#     try:
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor()
#         cursor.execute('SELECT * FROM users WHERE course_id = %s', (course_id,))
#         members = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         return jsonify({'members': members})
#     except Exception as e:
#         return make_response({'error': str(e)}, 400)

# # Retrieve Course Content
# @app.route('/content/<course_id>', methods=['GET'])
# def retrieve_course_content(course_id):
#     try:
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor()
#         cursor.execute('SELECT * FROM course_content WHERE course_id = %s', (course_id,))
#         content = cursor.fetchall()
#         cursor.close()
#         return jsonify({'content': content})
#     except Exception as e:
#         return make_response({'error': str(e)}, 400)

# # Add Course Content
# @app.route('/content/<course_id>', methods=['POST'])
# def add_course_content(course_id):
#     try:
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor()
#         data = request.get_json()
#         section_title = data['section_title']
#         section_content = data['section_content']
#         cursor = mysql.connection.cursor()
#         cursor.execute('INSERT INTO course_content (course_id, section_title, section_content) VALUES (%s, %s, %s)', (course_id, section_title, section_content))
#         cursor.commit()
#         cursor.close()
#         return jsonify({'message': 'Course content added successfully'})
#     except Exception as e:
#         return make_response({'error': str(e)}, 400)

# Retrieve all calender events for a particular course
@app.route('/api/courses/<int:course_id>/events', methods=['GET'])
def get_course_events(course_id):
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # check if course exist
        cursor.execute("""
            SELECT * FROM Courses WHERE courseID = %s
        """, (course_id,))
        course = cursor.fetchone()
        # if the course exist, get all events else return error
        if course is not None:
            cursor.execute("""
                SELECT * FROM CalenderEvents WHERE courseID = %s
            """, (course_id,))
            events = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({'events': events}), 200
        else:
            return jsonify({'error': 'Course not found'}), 404
    except IndexError:
        return jsonify({'error': 'Events not found'}), 404

# Retrieve all calender events for a particular date for a particular student
@app.route('/api/courses/<int:student_id>/events/<string:date>', methods=['GET'])
def get_student_events(student_id, date):
    # MySQL Connector initialization
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # check if student exist
        cursor.execute("""
            SELECT * FROM Students WHERE studentID = %s
        """, (student_id,))
        student = cursor.fetchone()
        # if the student exist, get all events else return error
        if student is not None:
            cursor.execute("""
                SELECT * FROM CalenderEvents WHERE studentID = %s AND eventDate = %s
            """, (student_id, date))
            events = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({'events': events}), 200
        else:
            return jsonify({'error': 'Student not found'}), 404
    except IndexError:
        return jsonify({'error': 'Events not found'}), 404

# Create a calender event for a particular course
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
        # check if course exist
        cursor.execute("""
            SELECT courseID FROM Courses WHERE courseID = %s
        """, (course_id,))
        course = cursor.fetchone()
        # get all the students in the course that the event is being created for
        cursor.execute("""
            SELECT courseID, studentID FROM Courses WHERE courseID = %s
        """, (course_id,))
        students = cursor.fetchall()
        # find the lecturer creating the event
        cursor.execute("""
            SELECT courseID, lecID FROM Courses WHERE courseID = %s
        """, (course_id,))
        lecturer = cursor.fetchone()
        # if the course exist, create the event else return error
        if course is not None:
            # create the event
            cursor.execute("""
                INSERT INTO CalenderEvents (courseID, lecID, studentID, eventTitle, eventDescription, eventDate)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (course[0], lecID, studentID, eventTitle, eventDescription, eventDate))
            conn.commit()
            cursor.close()
            conn.close()
            # print all the students in the course that the event is being created for
            for student in students:
                print("Students: ", student)
            # print the lecturer creating the event
            print("Lecturer: ", lecturer)
            return jsonify({'message': 'Event created successfully'}), 201
        else:
            return jsonify({'error': 'Course not found'}), 404
    except IndexError:
        return jsonify({'error': 'Course not found'}), 404

# REPORTS
@app.route('/api/reports/courses', methods=['GET'])
def get_courses_report():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # All courses that have 50 or more students
        cursor.execute("""
            SELECT courseID, COUNT(studentID) AS 'Number of Students'
            FROM Courses
            GROUP BY courseID
            HAVING COUNT(studentID) >= 50
        """)
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'courses': courses}), 200
    except IndexError:
        return jsonify({'error': 'Courses not found'}), 404
 

if __name__ == '__main__':
    app.run(debug=True, port=5001)

