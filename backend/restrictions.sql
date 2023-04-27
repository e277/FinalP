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