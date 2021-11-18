#!/usr/bin/env python

#-----------------------------------------------------------------------
# regclass.py
# Author: AnneMarie Caballero and Jen Secrest
#-----------------------------------------------------------------------

class RegClass:

    """
    Creates an object to represent the relevant information
    about a class in the registrar database (class id, dept,
    course num, area, title). Only has one public method
    to get a class id because the only relevant aspects
    are its string representation and also the class id.
    """

    def __init__(self, class_details):
        self._class_id = class_details[0]
        self._dept = class_details[1]
        self._course_num = class_details[2]
        self._area = class_details[3]
        self._title = class_details[4]

    def __str__(self):
        format_str = '{clsid:>5} {dept:>4} {crsnum:>6} {area:>4} '
        format_str += '{title}'

        return format_str.format(clsid = self._class_id,
            dept = self._dept,
            crsnum = self._course_num, area = self._area,
            title = self._title)

    def get_class_id(self):
        """
        Returns the class id of the regclass object on which it is
        called.
        """
        return self._class_id
