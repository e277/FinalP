from faker import Faker
import mysql.connector
import csv

fake = Faker()


with open('backend/insert_students.sql', 'w', newline='') as file:
    file.write("SET FOREIGN_KEY_CHECKS=0;\n")
    for i in range(100000):
        firstName = fake.first_name()
        lastName = fake.last_name()
        typeID = fake.random_int(min=1, max=3)
        file.write("INSERT INTO students (firstName, lastName, typeID) VALUES (" + " '" + firstName + "', '" + lastName + "', " + str(typeID) + ");\n")
    file.write("SET FOREIGN_KEY_CHECKS=1;")
