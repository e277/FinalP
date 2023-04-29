select * from SectionItems limit 15;
INSERT INTO Enrollments (courseID, lecID) VALUES (1, 1);
UPDATE Enrollments SET studentID = 425 WHERE courseID = 1 AND lecID = 1 ;
UPDATE Enrollments SET studentID = (SELECT studentID FROM Students WHERE studentID = 310 LIMIT 1) WHERE courseID = 1 AND lecID = 1;
SELECT e.courseID, e.studentID, s.firstName, s.lastName, e.lecID FROM Enrollments AS e LEFT JOIN Students AS s ON e.studentID = s.studentID WHERE e.courseID = 1;
DELETE FROM Enrollments WHERE studentID is NULL;
SELECT s.courseID, i.* FROM SectionItems AS i LEFT JOIN Sections AS s ON s.sectionID = i.sectionID WHERE s.courseID = 1;
select * from Accounts; select * from students; select * from lecturers; select * from Admins; select * from Enrollments;

-- No student can do more than 6 courses
SELECT studentID, COUNT(*) AS num_courses FROM Enrollments GROUP BY studentID HAVING num_courses > 6;
    
-- A student must be enrolled in at least 3 courses
SELECT studentID FROM Enrollments GROUP BY studentID HAVING COUNT(*) < 3;
    
-- Each course must have at least 10 members
SELECT courseID, COUNT(*) AS num_students FROM Enrollments GROUP BY courseID HAVING num_students < 10;
    
-- No lecturer can teach more than 5 courses
SELECT lecID, COUNT(*) AS num_courses FROM Courses GROUP BY lecID HAVING num_courses > 5;
    
-- A lecturer must teach at least 1 course
SELECT lecID FROM Courses GROUP BY lecID HAVING COUNT(*) < 1;