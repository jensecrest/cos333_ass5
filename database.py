#!/usr/bin/env python

#-----------------------------------------------------------------------
# database.py
# Authors: Jennifer Secrest and AnneMarie Caballero
#-----------------------------------------------------------------------

"""
Module on the server side. Contains all code to query database
and create SQLite statements.
"""

from sqlite3 import connect
from contextlib import closing
from regclass import RegClass
from regclassdetails import RegClassDetails

#-----------------------------------------------------------------------

DATABASE_URL = 'file:reg.sqlite?mode=ro'

#-----------------------------------------------------------------------

def create_condition_and_prepared_values(search):
    """
    Use the passed-in search to create a specific condition to be
    attached to the SQL query to ensure the proper query is carried
    out, and an list of the prepared values to accompany that condition.
    Returns a tuple with (condition, prepared_values).

    Keyword arguments:
    search -- a Search object that contains all relevant search fields
    (e.g. area)
    """
    condition = ""
    escape = r"ESCAPE '\' "

    prepared_values = []

    if search.get_dept() is not None:
        dept = replace_wildcards_with_escape_chars(search.get_dept())

        condition += "AND crosslistings.dept LIKE ? "
        prepared_values.append("%" + dept + "%")
        condition += escape

    if search.get_number() is not None:
        num = replace_wildcards_with_escape_chars(search.get_number())

        condition += "AND crosslistings.coursenum LIKE ? "
        prepared_values.append("%" + num + "%")
        condition += escape

    if search.get_area() is not None:
        area = replace_wildcards_with_escape_chars(search.get_area())

        condition += "AND courses.area LIKE ? "
        prepared_values.append("%" + area + "%")
        condition += escape

    if search.get_title() is not None:
        title = replace_wildcards_with_escape_chars(search.get_title())

        condition += "AND courses.title LIKE ? "
        prepared_values.append("%" + title + "%")
        condition += escape

    return (condition, prepared_values)

#-----------------------------------------------------------------------

def replace_wildcards_with_escape_chars(text):
    """
    Adds escape character for wildcards (_ or %) to ensure that
    they are interpreted as characters and not wildcards.
    Returns the text created by adding escape character before
    wildcards.

    Keyword arguments:
    text -- string to be used with LIKE SQL command
    """

    new_text = text

    for index, char in enumerate(text):
        if char == "_":
            new_text = new_text[:index] + r"\_" + new_text[index + 1:]
        elif char == "%":
            new_text = new_text[:index] + r"\%" + new_text[index + 1:]

    return new_text

#-----------------------------------------------------------------------

def get_classes_with_condition(condition, prepared_values):
    """
    Prepares the SQL Query for the given condition and prepared
    values then returns the results as an array of RegClass objects.

    Keyword arguments:
    condition -- conditions to be added to the SQL query
    prepared_values -- values that accompany given condition
    """

    with connect(DATABASE_URL, uri=True) as connection:
        with closing(connection.cursor()) as cursor:

            # classes: courseid, classid
            # courses: courseid, area, title
            # crosslistings: courseid, dept, coursenum

            # prepare query
            stmt_str = "SELECT classes.classid, classes.courseid, "
            stmt_str += "courses.courseid, courses.area, courses.title"
            stmt_str += ", crosslistings.courseid, crosslistings.dept, "
            stmt_str += "crosslistings.coursenum "
            stmt_str += "FROM classes, courses, crosslistings "
            stmt_str += "WHERE classes.courseid = courses.courseid "
            stmt_str += "AND courses.courseid = crosslistings.courseid "
            stmt_str += condition + " "
            stmt_str += "ORDER BY crosslistings.dept, "
            stmt_str += "crosslistings.coursenum, classes.classid ASC"

            # execute query
            if len(prepared_values) == 0:
                cursor.execute(stmt_str)
            else:
                cursor.execute(stmt_str, prepared_values)

            row = cursor.fetchone()

            classes = []

            while row is not None:
                # 0 = class id; 1, 2, 5 = course id; 3 = area;
                # #4 = title; 6 = dept; 7 = coursenum
                classes.append(RegClass([str(row[0]),\
                    str(row[6]), str(row[7]), str(row[3]),\
                    str(row[4])]))

                row = cursor.fetchone()

            return classes

#-----------------------------------------------------------------------

def get_class_details(class_id):
    """
    Prepares the SQL Query for the given class id
    then query the database to construct the results as a
    a RegClassDetails. Returns that RegClassDetails object.

    Keyword arguments:
    class_id - the id of the class to request the details for
    """

    with connect(DATABASE_URL, uri=True) as connection:
        with closing(connection.cursor()) as cursor:

            # query classes variables
            stmt_str = "SELECT classid, courseid, days, starttime, "\
                + "endtime, bldg, roomnum "\
                + "FROM classes WHERE classid = ? "
            cursor.execute(stmt_str, [class_id])

            classes_row = cursor.fetchone()

            if classes_row is None:
                raise ValueError("no class with class id " +\
                                str(class_id) + " exists")

            class_details = []

            # course id
            course_id = str(classes_row[1])
            class_details.append(course_id)
            # days
            class_details.append(str(classes_row[2]))
            # starttime
            class_details.append(str(classes_row[3]))
            # endtime
            class_details.append(str(classes_row[4]))
            # bldg
            class_details.append(str(classes_row[5]))
            # roomnum
            class_details.append(str(classes_row[6]))

            # crosslisting variables
            stmt_str = "SELECT courseid, dept, coursenum "\
                + "FROM crosslistings WHERE "\
                + "crosslistings.courseid = ? "\
                + "ORDER BY dept, coursenum ASC"

            cursor.execute(stmt_str, [course_id])

            cl_row = cursor.fetchone()

            cl_details = []

            depts = []
            course_nums = []

            while cl_row is not None:
                depts.append(str(cl_row[1]))
                course_nums.append(str(cl_row[2]))

                cl_row = cursor.fetchone()

            cl_details = [depts, course_nums]

            # courses variables

            stmt_str = "SELECT courseid, area, title, descrip, "\
                + "prereqs FROM courses WHERE courseid = ? "

            cursor.execute(stmt_str, [course_id])
            courses_row = cursor.fetchone()

            courses_details = []

            # area
            courses_details.append(str(courses_row[1]))
            #title
            courses_details.append(str(courses_row[2]))
            # descrip
            courses_details.append(str(courses_row[3]))
            # prereqs
            courses_details.append(str(courses_row[4]))

            # professor variables

            stmt_str = "SELECT coursesprofs.courseid, "\
                + "coursesprofs.profid, "\
                + "profs.profid, profs.profname "\
                + "FROM coursesprofs, profs WHERE "\
                + "coursesprofs.courseid = ? "\
                + "AND profs.profid = coursesprofs.profid "\
                + "ORDER BY profs.profname ASC"

            cursor.execute(stmt_str, [course_id])
            prof_row = cursor.fetchone()

            prof_names = []

            while prof_row is not None:
                prof_names.append(prof_row[3])

                prof_row = cursor.fetchone()

            return RegClassDetails(class_details, cl_details,
                courses_details, prof_names)
