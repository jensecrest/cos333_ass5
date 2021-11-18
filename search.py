#!/usr/bin/env python

#-----------------------------------------------------------------------
# search.py
# Author: AnneMarie Caballero and Jen Secrest
#-----------------------------------------------------------------------

class Search:

    def __init__(self, dept, number, area, title):
        self._dept = dept
        self._number = str(number)
        self._area = area
        self._title = title

    def __str__(self):
        return '( ' + self._dept + ', ' + self._number\
            + ', ' + self._area + ', ' + self._title + ')'

    def set_dept(self, dept):
        self._title = dept

    def get_dept(self):
        return self._dept

    def set_number(self, number):
        self._number = str(number)

    def get_number(self):
        return self._number

    def set_area(self, area):
        self._area = area

    def get_area(self):
        return self._area

    def set_title(self, title):
        self._title = title

    def get_title(self):
        return self._title