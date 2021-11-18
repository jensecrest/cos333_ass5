#!/usr/bin/env python

#-----------------------------------------------------------------------
# search.py
# Author: AnneMarie Caballero and Jen Secrest
#-----------------------------------------------------------------------

class Search:
    """
    Creates a search object that represents a way to
    search classes in the registrar database with four
    main fields: dept, num, area, and title.
    """

    def __init__(self, dept, number, area, title):
        self._dept = str(dept)
        self._number = str(number)
        self._area = str(area)
        self._title = str(title)

    def __str__(self):
        return '( ' + self._dept + ', ' + self._number\
            + ', ' + self._area + ', ' + self._title + ')'

    def get_dept(self):
        """
        Returns the department of the Search object.
        """
        return self._dept

    def get_number(self):
        """
        Returns the course number of the Search object.
        """
        return self._number

    def get_area(self):
        """
        Returns the area of the Search object.
        """
        return self._area

    def get_title(self):
        """
        Returns the title of the Search object.
        """
        return self._title
