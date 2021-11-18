#!/usr/bin/env python

#-----------------------------------------------------------------------
# regclassdetails.py
# Author: AnneMarie Caballero and Jen Secrest
#-----------------------------------------------------------------------

class RegClassDetails:
    """
    Creates an object to represent all of the main details
    of a class from the reegistrar database. Does not have any
    public methods because the main use of this class is to
    store the details of a class and then print those details.
    """

    def __init__(self, class_details, cl_details,
        course_details, prof_details):
        self._class_details = class_details
        self._cl_details = cl_details
        self._course_details = course_details
        self._prof_details = prof_details

    def __str__(self):
        reg_class_details = self.__format_class_info()
        reg_class_details += self.__format_crosslistings_info()
        reg_class_details += self.__format_courses_info()
        reg_class_details += self.__format_profs_info()

        return reg_class_details

    def set_class_data(self, class_details):
        """
        Set the data for classes

        Keyword arguments:
            class_details -- passes in the array with
                appropriate class details (should have
                course_id, days, starttime, endtime,
                bldg and roomnum)
        """
        self._class_details = class_details

    def set_cl_data(self, cl_details):
        """
        Set the data for crosslistings

        Keyword arguments:
            cl_details -- passes in the array with
            appropriate class details (departments and
            course numbers)
        """
        self._cl_details = cl_details

    def set_courses_data(self, courses_details):
        """
        Set the data for courses

        Keyword arguments:
            courses_details - array with appropriate details
                for courses (area, title, descrip, and prereqs)
        """

        self._course_details = courses_details

    def set_prof_data(self, prof_names):
        """
        Set the data for professors

        Keyword arguments:
            prof_names -- list of names of professors who teach
            the course in question
        """
        self._prof_details = prof_names

    def __format_class_info(self):
        class_info = "Course Id: " + str(self._class_details[0])\
            + "\n\n"
        class_info += "Days: " + str(self._class_details[1]) + "\n"
        class_info += "Start time: " + str(self._class_details[2])\
            + "\n"
        class_info += "End time: " + str(self._class_details[3])\
            + "\n"
        class_info += "Building: " + str(self._class_details[4])\
            + "\n"
        class_info += "Room: " + str(self._class_details[5])\
            + "\n\n"

        return class_info

    def __format_crosslistings_info(self):
        crosslistings_info = ""

        depts = self._cl_details[0]
        course_nums = self._cl_details[1]

        for i, dept in enumerate(depts):
            crosslistings_info += "Dept and Number: " +\
                dept + " " + course_nums[i] + "\n"

        crosslistings_info += "\n"

        return crosslistings_info

    def __format_courses_info(self):
        courses_info = "Area: " + str(self._course_details[0])\
            + "\n\n"
        courses_info += "Title: " + str(self._course_details[1])\
            + "\n\n"
        courses_info += "Description: " + str(self._course_details[2])\
            + "\n\n"
        courses_info += "Prerequisites: " +\
            str(self._course_details[3]) + "\n\n"

        return courses_info

    def __format_profs_info(self):
        profs_info = ""

        for prof_name in self._prof_details:
            profs_info += "Professor: " + prof_name + "\n"

        return profs_info
