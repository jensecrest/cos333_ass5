#!/usr/bin/env python

#-----------------------------------------------------------------------
# regclassdetails.py
# Author: AnneMarie Caballero and Jen Secrest
#-----------------------------------------------------------------------

class RegClassDetails:

    def __init__(self, course_id, days, start_time, end_time,
        bldg, room_num, depts, course_nums, area, title, descrip,
        prereqs, prof_names):
        
        self._course_id = course_id
        self._days = days
        self._start_time = start_time
        self._end_time = end_time
        self._bldg = bldg
        self._room_num = room_num
        self._depts = depts
        self._course_nums = course_nums
        self._area = area
        self._title = title
        self._descrip = descrip
        self._prereqs = prereqs
        self._prof_names = prof_names

    def __str__(self):
        reg_class_details = self.__format_class_info()
        reg_class_details += self.__format_crosslistings_info()
        reg_class_details += self.__format_courses_info()
        reg_class_details += self.__format_profs_info()

        return reg_class_details

    def __format_class_info(self):
        class_info = "Course Id: " + str(self._course_id) + "\n\n"
        class_info += "Days: " + str(self._days) + "\n"
        class_info += "Start time: " + str(self._start_time) + "\n"
        class_info += "End time: " + str(self._end_time) + "\n"
        class_info += "Building: " + str(self._bldg) + "\n"
        class_info += "Room: " + str(self._room_num) + "\n\n"

        return class_info

    def __format_crosslistings_info(self):
        crosslistings_info = ""

        for i in range(len(self._depts)):
            crosslistings_info += "Dept and Number: " +\
                self._depts[i] + " " + self._course_nums[i] + "\n"

        crosslistings_info += "\n"

        return crosslistings_info

    def __format_courses_info(self):
        courses_info = "Area: " + str(self._area) + "\n\n"
        courses_info += "Title: " + str(self._title) + "\n\n"
        courses_info += "Description: " + str(self._descrip) + "\n\n"
        courses_info += "Prerequisites: " + str(self._prereqs) + "\n\n"

        return courses_info

    def __format_profs_info(self):
        profs_info = ""

        for prof_name in self._prof_names:
            profs_info += "Professor: " + prof_name + "\n"

        return profs_info