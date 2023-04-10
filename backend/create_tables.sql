-- Tables - CREATE 
CREATE TABLE Accounts (
    typeID INT AUTO_INCREMENT,
    typeName VARCHAR(255), -- (Lecturer/Course Maintainer, Student, Admin)
    username VARCHAR(255), -- userid
    password VARCHAR(255),
    PRIMARY KEY (typeID)
);

CREATE TABLE Admins (
    adminID INT AUTO_INCREMENT,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    typeID INT,
    PRIMARY KEY (adminID),
    FOREIGN KEY (typeID) REFERENCES Accounts(typeID)
);

CREATE TABLE Lecturers (
    lecID INT AUTO_INCREMENT,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    typeID INT,
    coursesTaught INT CHECK (coursesTaught >= 1 AND coursesTaught <= 5),
    PRIMARY KEY (lecID),
    FOREIGN KEY (typeID) REFERENCES Accounts(typeID)
);

CREATE TABLE Students (
    studentID INT AUTO_INCREMENT,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    typeID INT,
    coursesEnrolled INT CHECK (coursesEnrolled >= 3 AND coursesEnrolled <= 6),
    PRIMARY KEY (studentID),
    FOREIGN KEY (typeID) REFERENCES Accounts(typeID)
);

CREATE TABLE Courses (
    courseID INT AUTO_INCREMENT,
    courseName VARCHAR(255),
    courseDescription VARCHAR(255),
    lecID INT,
    studentID INT,
    numberOfMembers INT CHECK (numberOfMembers >= 10),
    PRIMARY KEY (courseID),
    FOREIGN KEY (lecID) REFERENCES Lecturers(lecID),
    FOREIGN KEY (studentID) REFERENCES Students(studentID)
);

CREATE TABLE CourseMembers (
    memberID INT AUTO_INCREMENT,
    courseID INT,
    lecID INT,
    studentID INT,
    PRIMARY KEY (memberID),
    FOREIGN KEY (courseID) REFERENCES Courses(courseID),
    FOREIGN KEY (lecID) REFERENCES Lecturers(lecID),
    FOREIGN KEY (studentID) REFERENCES Students(studentID)
);

CREATE TABLE DiscussionForums (
    forumID INT AUTO_INCREMENT,
    courseID INT,
    forumName VARCHAR(255),
    PRIMARY KEY (forumID),
    FOREIGN KEY (courseID) REFERENCES Courses(courseID)
);

CREATE TABLE DiscussionThreads (
    threadID INT AUTO_INCREMENT,
    forumID INT,
    threadTitle VARCHAR(255),
    threadContent VARCHAR(255),
    lecID INT,
    studentID INT,
    PRIMARY KEY (threadID),
    FOREIGN KEY (forumID) REFERENCES DiscussionForums(forumID),
    FOREIGN KEY (lecID) REFERENCES Lecturers(lecID),
    FOREIGN KEY (studentID) REFERENCES Students(studentID)
);

CREATE TABLE DiscussionThreadReplies (
    replyID INT AUTO_INCREMENT,
    threadID INT,
    courseID INT,
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

CREATE TABLE SectionIems (
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