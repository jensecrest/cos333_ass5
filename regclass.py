#!/usr/bin/env python

#-----------------------------------------------------------------------
# regclass.py
# Author: AnneMarie Caballero and Jen Secrest
#-----------------------------------------------------------------------

class RegClass:

    def __init__(self, class_id, dept, course_num, area, title):
        self._class_id = class_id
        self._dept = dept
        self._course_num = course_num
        self._area = area
        self._title = title

    def __str__(self):
        format_str = '{clsid:>5} {dept:>4} {crsnum:>6} {area:>4} {title}'

        return format_str.format(clsid = self._class_id, dept = self._dept,
            crsnum = self._course_num, area = self._area, 
            title = self._title)

    def set_class_id(self, class_id):
        self._class_id = class_id

    def get_class_id(self):
        return self._class_id

    def set_dept(self, dept):
        self._dept = dept

    def get_dept(self):
        return self._dept

    def set_number(self, course_num):
        self._course_num = course_num

    def get_course_num(self):
        return self._course_num

    def set_area(self, area):
        self._area = area

    def get_area(self):
        return self._area

    def set_title(self, title):
        self._title = title

    def get_title(self):
        return self._title