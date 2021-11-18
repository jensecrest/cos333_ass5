#!/usr/bin/env python

#--------------------------------------------------------------------------------
# regdetails.py
# Authors: Jennifer Secrest and AnneMarie Caballero
#--------------------------------------------------------------------------------

"""
Implements a command-line argument application that allows user to view
class details from the registrar's office. Prints all class details
(e.g. start time, end time, room) for the class with the passed-in
class id.
"""

import argparse
import sqlite3
import sys
import textwrap
from sys import argv, stderr
from sqlite3 import connect
from contextlib import closing

#--------------------------------------------------------------------------------

DATABASE_URL = 'file:reg.sqlite?mode=ro'

def main():
    """
    Parse the command-line arg (the class id), create a query and use that query to print
    the relevant class details.
    """

    try:
        parser = argparse.ArgumentParser(allow_abbrev=False,
        description="Registrar application: show details about a class")
        parser.add_argument("classid", type=int,
        help = "the id of the class whose details should be shown")

        args = parser.parse_args()

        print_class_details(args.classid)

    except sqlite3.DatabaseError as ex:
        print(argv[0] + ": " + str(ex), file=stderr)
        sys.exit(1)
    except ValueError as ex:
        print(argv[0] + ": " + str(ex), file=stderr)
        sys.exit(1)
    except argparse.ArgumentError as ex:
        print(argv[0] + ": " + str(ex), file=stderr)
        sys.exit(2)

def print_classes_info_and_get_course_id(cursor, class_id):
    """
    Query the classes table using cursor to acquire the relevant
    details for class with class id class_id. Print those details.

    Keyword arguments:
    cursor -- used to access and execute query on database
    class_id -- the id of the class for which to print the details from
                the classes table
    """

    # classes variables
    stmt_str = "SELECT classid, courseid, days, starttime, endtime, bldg, roomnum "
    stmt_str += "FROM classes WHERE classid = ? "
    cursor.execute(stmt_str, [class_id])

    classes_row = cursor.fetchone()

    if classes_row is not None:
        course_id = classes_row[1]
    else:
        raise ValueError("no class with class id " + str(class_id) + " exists")

    to_print = "Course Id: " + str(course_id) + "\n\n"
    to_print += "Days: " + str(classes_row[2]) + "\n"
    to_print += "Start time: " + str(classes_row[3]) + "\n"
    to_print += "End time: " + str(classes_row[4]) + "\n"
    to_print += "Building: " + str(classes_row[5]) + "\n"
    to_print += "Room: " + str(classes_row[6]) + "\n"
    print(to_print)

    return course_id

def print_crosslistings_info(cursor, course_id):
    """
    Query the crosslistings table using cursor to acquire the relevant
    details for a class with course id course_id. Sort these details by
    professor then coursenum. Print the details.

    Keyword arguments:
    cursor -- used to access and execute query on database
    course_id -- the id of the course for which to print the details from
                the crosslistings table
    """

    stmt_str = "SELECT courseid, dept, coursenum "
    stmt_str += "FROM crosslistings WHERE crosslistings.courseid = ? "
    stmt_str += "ORDER BY dept, coursenum ASC"
    cursor.execute(stmt_str, [course_id])

    cl_rows = cursor.fetchone()
    while cl_rows is not None:
        print(textwrap.fill(text="Dept and Number: " +
        str(cl_rows[1]) + " " + str(cl_rows[2]), width=72))
        cl_rows = cursor.fetchone()
    print()

def print_courses_info(cursor, course_id):
    """
    Query the courses table using cursor to acquire the relevant
    details for a class with course id course_id. Print those details.

    Keyword arguments:
    cursor -- used to access and execute query on database
    course_id -- the id of the course for which to print the details from
                the courses table
    """

    stmt_str = "SELECT courseid, area, title, descrip, prereqs "
    stmt_str += "FROM courses WHERE courseid = ? "

    cursor.execute(stmt_str, [course_id])
    courses_row = cursor.fetchone()

    print("Area: " + str(courses_row[1]) + "\n")
    print(textwrap.fill(text="Title: " + str(courses_row[2]), width=72) + "\n")
    print(textwrap.fill(text="Description: " + str(courses_row[3]), width=72) + "\n")
    print(textwrap.fill(text="Prerequisites: " + str(courses_row[4]), width=72) + "\n")

def print_profs_info(cursor, course_id):
    """
    Query the coursesprofs and profs tables using cursor to acquire the relevant
    details for a class with course id course_id. Sort by professors
    in ascending order. Print those details.

    Keyword arguments:
    cursor -- used to access and execute query on database
    course_id -- the id of the course for which to print the details from
                the courseprofs and profs table
    """

    stmt_str = "SELECT coursesprofs.courseid, coursesprofs.profid, "
    stmt_str += "profs.profid, profs.profname "
    stmt_str += "FROM coursesprofs, profs WHERE coursesprofs.courseid = ? "
    stmt_str += "AND profs.profid = coursesprofs.profid "
    stmt_str += "ORDER BY profs.profname ASC"
    cursor.execute(stmt_str, [course_id])

    prof_rows = cursor.fetchone()

    while prof_rows is not None:
        print(textwrap.fill(text="Professor: " + prof_rows[3], width=72))
        prof_rows = cursor.fetchone()

def print_class_details(class_id):
    """
    Calls methods to print all details for the class with the given class id.

    Keyword arguments:
    class_id -- the id of the class for which to print the details
    """

    with connect(DATABASE_URL, uri=True) as connection:
        with closing(connection.cursor()) as cursor:

            course_id = print_classes_info_and_get_course_id(cursor, class_id)
            print_crosslistings_info(cursor, course_id)
            print_courses_info(cursor, course_id)
            print_profs_info(cursor, course_id)

#--------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
