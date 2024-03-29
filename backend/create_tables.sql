-- Tables - CREATE 
CREATE TABLE Accounts (
    typeID INT AUTO_INCREMENT,
    typeName VARCHAR(255), -- (admin, lecturer, student)
    username VARCHAR(255), -- acting as userid
    password VARCHAR(255),
    PRIMARY KEY (typeID)
);

CREATE TABLE Admins (
    adminID INT AUTO_INCREMENT,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    typeID INT NULL,
    PRIMARY KEY (adminID),
    FOREIGN KEY (typeID) REFERENCES Accounts(typeID)
);

CREATE TABLE Lecturers (
    lecID INT AUTO_INCREMENT,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    typeID INT NULL,
    PRIMARY KEY (lecID),
    FOREIGN KEY (typeID) REFERENCES Accounts(typeID)
);

CREATE TABLE Students (
    studentID INT AUTO_INCREMENT,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    typeID INT NULL,
    PRIMARY KEY (studentID),
    FOREIGN KEY (typeID) REFERENCES Accounts(typeID)
);

CREATE TABLE Courses (
    courseID INT AUTO_INCREMENT,
    courseName VARCHAR(255),
    courseDescription VARCHAR(255),
    PRIMARY KEY (courseID)
);

CREATE TABLE Enrollments (
    enrollmentID INT AUTO_INCREMENT,
    courseID INT NULL,
    studentID INT NULL,
    lecID INT NULL,
    coursesTaught INT CHECK (coursesTaught <= 5),
    coursesEnrolled INT CHECK (coursesEnrolled <= 6),
    numberOfMembers INT CHECK (numberOfMembers >= 10),
    PRIMARY KEY (enrollmentID),
    FOREIGN KEY (courseID) REFERENCES Courses(courseID),
    FOREIGN KEY (studentID) REFERENCES Students(studentID),
    FOREIGN KEY (lecID) REFERENCES Lecturers(lecID)
);

CREATE TABLE DiscussionForums (
    forumID INT AUTO_INCREMENT,
    courseID INT NULL,
    forumName VARCHAR(255),
    PRIMARY KEY (forumID),
    FOREIGN KEY (courseID) REFERENCES Courses(courseID)
);

CREATE TABLE DiscussionThreads (
    threadID INT AUTO_INCREMENT,
    forumID INT NULL,
    threadTitle VARCHAR(255),
    threadContent VARCHAR(255),
    lecID INT NULL,
    studentID INT NULL,
    PRIMARY KEY (threadID),
    FOREIGN KEY (forumID) REFERENCES DiscussionForums(forumID),
    FOREIGN KEY (lecID) REFERENCES Lecturers(lecID),
    FOREIGN KEY (studentID) REFERENCES Students(studentID)
);

CREATE TABLE DiscussionThreadReplies (
    replyID INT AUTO_INCREMENT,
    threadID INT NULL,
    courseID INT NULL,
    replyContent VARCHAR(255),
    PRIMARY KEY (replyID),
    FOREIGN KEY (threadID) REFERENCES DiscussionThreads(threadID),
    FOREIGN KEY (courseID) REFERENCES Courses(courseID)
);

CREATE TABLE Sections (
    sectionID INT AUTO_INCREMENT,
    courseID INT,
    sectionTitle VARCHAR(255),
    PRIMARY KEY (sectionID),
    FOREIGN KEY (courseID) REFERENCES Courses(courseID)
);

CREATE TABLE SectionItems (
    itemID INT AUTO_INCREMENT,
    sectionID INT,
    lecID INT,
    itemType VARCHAR(255),
    -- link, lecture, assignment, quiz, etc
    itemTitle VARCHAR(255),
    itemContent VARCHAR(255),
    PRIMARY KEY (itemID),
    FOREIGN KEY (sectionID) REFERENCES Sections(sectionID),
    FOREIGN KEY (lecID) REFERENCES Lecturers(lecID)
);

CREATE TABLE CalenderEvents (
    eventID INT AUTO_INCREMENT,
    courseID INT,
    lecID INT,
    studentID INT,
    eventTitle VARCHAR(255),
    eventDescription VARCHAR(255),
    eventDate DATE,
    PRIMARY KEY (eventID),
    FOREIGN KEY (courseID) REFERENCES Courses(courseID),
    FOREIGN KEY (lecID) REFERENCES Lecturers(lecID),
    FOREIGN KEY (studentID) REFERENCES Students(studentID)
);

CREATE TABLE Assignments (
    assignmentID INT AUTO_INCREMENT,
    courseID INT,
    studentID INT,
    assignmentTitle VARCHAR(255),
    assignmentDescription VARCHAR(255),
    assignmentDueDate DATE,
    assignmentSubmissionDate DATE,
    PRIMARY KEY (assignmentID),
    FOREIGN KEY (courseID) REFERENCES Courses(courseID),
    FOREIGN KEY (studentID) REFERENCES Students(studentID)
);

CREATE TABLE Grades (
    gradeID INT AUTO_INCREMENT,
    grade DECIMAL(5,2),
    studentID INT NULL,
    assignmentID INT NULL,
    courseID INT NULL,
    PRIMARY KEY (gradeID),
    FOREIGN KEY (studentID) REFERENCES Students(studentID),
    FOREIGN KEY (assignmentID) REFERENCES Assignments(assignmentID),
    FOREIGN KEY (courseID) REFERENCES Courses(courseID)
);