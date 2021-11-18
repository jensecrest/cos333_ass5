#!/usr/bin/env python

#--------------------------------------------------------------------------------
# reg.py
# Authors: Jennifer Secrest and AnneMarie Caballero
#--------------------------------------------------------------------------------

"""
TODO: update comment

Implements a command-line argument application that allows user to view
courses from the registrar's office. Allows for user to print all courses
when no argument is provided or to search by area, department, title, and
course number.
"""

import argparse
import sqlite3
import sys
from sys import argv, stderr
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from pickle import dump, load
from search import Search
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QLineEdit, QLabel, QFrame
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QMainWindow, QMessageBox
from PyQt5.QtWidgets import QPushButton, QDesktopWidget, QListWidget, QListWidgetItem

#--------------------------------------------------------------------------------

window = None
dept = None
num = None
area = None
title = None
listwidget = None
host = None
port = None

def main():
    """
    TODO: update comment

    Parse the command-line args, create a query and use that query to print
    the relevant course table.
    """

    global host, port

    try:
        # Extract command-line args
        args = parse_args()
        host = args.host
        port = args.port

        # TODO: kind of a messy way to do this (reconsider?)
        # Retrieve all classes to start
        search = Search('', '', '', '')
        classes = query_server_for_search(host, port, search)

        show_gui(argv, classes)

    except sqlite3.DatabaseError as ex:
        print(argv[0] + ": " + str(ex), file=stderr)
        sys.exit(1)
    except argparse.ArgumentError as ex:
        print(argv[0] + ": " + str(ex), file=stderr)
        sys.exit(2)

def parse_args():
    """
    Return a Namespace that has the values for the command-line arguments saved in it.
    Raises argparse.ArgumentError if positional arguments have invalid inputs.
    TODO: check on this comment
    """

    parser = argparse.ArgumentParser(allow_abbrev=False, description=
                        "Client for the registrar application")
    parser.add_argument("host", type=str,
        help="the host on which the server is running")
    parser.add_argument("port", type=int,
        help = "the port at which the server should listen")

    return parser.parse_args()

def show_gui(argv, classes):
    global window, dept, num, area, title, listwidget

    app = QApplication(argv)

    # TODO: should this be an array?
    dept = QLineEdit()
    num = QLineEdit()
    area = QLineEdit()
    title = QLineEdit()
    
    dept.returnPressed.connect(initiate_search_query)
    num.returnPressed.connect(initiate_search_query)
    area.returnPressed.connect(initiate_search_query)
    title.returnPressed.connect(initiate_search_query)

    submit_button = QPushButton('Submit')
    submit_button.clicked.connect(initiate_search_query)

    layout = QVBoxLayout()

    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(create_inputs(dept, num, area, title, submit_button)) 
    listwidget = QListWidget()
    layout.addWidget(create_output(listwidget, classes))

    frame = QFrame()
    frame.setLayout(layout)

    window = QMainWindow()
    window.setWindowTitle('Princeton University Class Search')
    window.setCentralWidget(frame)
    screen_size = QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)

    window.show()
    exit(app.exec_())

def initiate_search_query():
    global dept, num, area, title, listwidget

    if dept == None or num == None or area == None\
            or title == None:
        # TODO: throw actual correct error 
        raise ValueError()

    dept_text = dept.text()
    num_text = num.text()
    area_text = area.text()
    title_text = title.text()

    classes = query_server_for_search(host, port,
        Search(dept_text, num_text, area_text, title_text))
    
    create_output(listwidget, classes)

def create_inputs(dept, num, area, title, submit_button):
    ## TODO: check spacing 
    ## TODO: modularize 
    grid_layout = QGridLayout()

    grid_layout.addWidget(create_label('Dept: '), 0, 0) #Dept
    grid_layout.addWidget(create_label('Number: '), 1, 0) #Number
    grid_layout.addWidget(create_label('Area: '), 2, 0) #Area
    grid_layout.addWidget(create_label('Title: '), 3, 0) #Title

    grid_layout.addWidget(dept, 0, 1) #Dept
    grid_layout.addWidget(num, 1, 1) #Number
    grid_layout.addWidget(area, 2, 1) #Area
    grid_layout.addWidget(title, 3, 1) #Title

    grid_layout.addWidget(submit_button, 0, 2, 4, 1)

    grid_frame = QFrame()
    grid_frame.setLayout(grid_layout)

    return grid_frame

def create_label(text):
    label = QLabel(text)
    
    # used to align text of label:
    # https://www.geeksforgeeks.org/pyqt5-how-to-align-text-of-label/
    label.setAlignment(QtCore.Qt.AlignRight)

    return label

def create_output(listwidget, classes):
    listwidget.clear()

    for i, regclass in enumerate(classes):
        item = QListWidgetItem()

        item.setFont(QFont("Courier", 10))
        item.setText(str(regclass))

        # Role documentation: 
        # https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html
        # setData() documention: 
        # https://doc.qt.io/qtforpython/PySide6/QtWidgets/QListWidgetItem.html
        item.setData(QtCore.Qt.UserRole, regclass.get_class_id())

        listwidget.insertItem(i, item)

    # Used listwidget documentation:
    # https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QListWidget.html

    listwidget.itemDoubleClicked.connect(initiate_class_details_query)

    return listwidget

def initiate_class_details_query():
    global window, listwidget

    # TODO: error handle different amount than one
    selected_item = listwidget.selectedItems()[0]
    class_id = selected_item.data(QtCore.Qt.UserRole)

    class_details = query_server_for_class_details(host, port,
        class_id)

    # TODO: set title
    QMessageBox.information(window, 'Class Details', str(class_details))
    
def query_server_for_search(host, port, search):
    try:
        with socket() as sock:
            sock.connect((host, port))

            write_flo = sock.makefile(mode='wb')
            dump(True, write_flo)
            dump(search, write_flo)
            write_flo.flush()
            print('Sent search to server')

            read_flo = sock.makefile(mode='rb')
            result = load(read_flo)
            classes = load(read_flo)
            print('Received classes from the server')
            
            return classes
            
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

def query_server_for_class_details(host, port, class_id):
    try:
        with socket() as sock:
            sock.connect((host, port))

            write_flo = sock.makefile(mode='wb')
            # false because this query is not a search
            dump(False, write_flo)
            dump(class_id, write_flo)
            write_flo.flush()
            print('Sent class id to server')

            read_flo = sock.makefile(mode='rb')
            # boolean result, True if success, False if failure
            result = load(read_flo)
            details = load(read_flo)
            print('Received class details from the server')
            
            return details

    # TODO: error handling!  
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

#--------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
