#!/usr/bin/env python

#-----------------------------------------------------------------------
# reg.py
# Authors: Jennifer Secrest and AnneMarie Caballero
#-----------------------------------------------------------------------

"""
Creates an application using GUI and networking technologies to
have an interface that displays the results of queries of a server
that allows access to registrar data, specifically allows users
to see and search classes, and also display class details.
"""

import argparse
import sys
from sys import argv, stderr
from socket import socket
from pickle import dump, load
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QLineEdit, QLabel, QFrame,\
    QGridLayout, QVBoxLayout, QMainWindow, QMessageBox,\
    QDesktopWidget, QListWidget, QListWidgetItem
from search import Search
from threading import Thread

#-----------------------------------------------------------------------

def main():
    """
    Parse the command-line args (host and port to access
    for the database server), and use them to create a GUI
    application that interfaces with the server
    in order to display registrar information, specifically
    class lists, that are searchable and also enable the user
    to view class details of classes visible in this class list.
    """

    try:
        # Extract command-line args
        args = __parse_args()
        host = args.host
        port = args.port

        __show_gui(argv, host, port)

    except argparse.ArgumentError as ex:
        print(argv[0] + ": " + str(ex), file=stderr)
        sys.exit(2)

#-----------------------------------------------------------------------

def __parse_args():
    parser = argparse.ArgumentParser(allow_abbrev=False, description=
                        "Client for the registrar application")
    parser.add_argument("host", type=str,
        help="the host on which the server is running")
    parser.add_argument("port", type=int,
        help = "the port at which the server should listen")

    return parser.parse_args()

#-----------------------------------------------------------------------

def __show_gui(arg, host, port):
    app = QApplication(arg)

    window = QMainWindow()
    window.setWindowTitle('Princeton University Class Search')
    screen_size = QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)

    dept = QLineEdit()
    num = QLineEdit()
    area = QLineEdit()
    title = QLineEdit()

    
    
    #     author = author_lineedit.text()
    #     if worker_thread is not None:
    #         worker_thread.stop()
    #     worker_thread = WorkerThread(host, port, author, queue)
    #     worker_thread.start()

    worker_thread = None
    def __initiate_search_query():
        nonlocal worker_thread

        dept_text = dept.text()
        num_text = num.text()
        area_text = area.text()
        title_text = title.text()

        try:

            if worker_thread is not None:
                worker_thread.stop()
            worker_thread = WorkerThread(host, port, search, queue)
            worker_thread.start()

        except Exception as ex:
            QMessageBox.critical(window, 'Server Error', str(ex))
            return

        if classes_response[0]:
            __create_output(classes_response[1], host,\
                port, window, list_widget)
        else:
            QMessageBox.critical(window, 'Error',
                str(classes_response[1]))

    dept.textChanged.connect(__initiate_search_query)
    num.textChanged.connect(__initiate_search_query)
    area.textChanged.connect(__initiate_search_query)
    title.textChanged.connect(__initiate_search_query)

    layout = QVBoxLayout()

    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(__create_inputs(dept, num, area, title))

    list_widget = QListWidget()
    layout.addWidget(list_widget)

    def __initiate_class_details_query():
        selected_item = list_widget.selectedItems()[0]
        class_id = selected_item.data(QtCore.Qt.UserRole)

        try:
            class_details_response =\
                __query_server_for_class_details(host, port, class_id)
        except Exception as ex:
            QMessageBox.critical(window, 'Server Error', str(ex))
            return

        if class_details_response[0]:
            QMessageBox.information(window, 'Class Details',\
                str(class_details_response[1]))
        else:
            QMessageBox.critical(window,\
                'Error', str(class_details_response[1]))
    
    list_widget.itemActivated.connect(__initiate_class_details_query)

    frame = QFrame()
    frame.setLayout(layout)
    window.setCentralWidget(frame)

    window.show()

    # execute initial empty search to get all courses
    __initiate_search_query()

    sys.exit(app.exec_())

#-----------------------------------------------------------------------

def __create_inputs(dept, num, area, title):
    grid_layout = QGridLayout()

    grid_layout.addWidget(__create_label('Dept: '), 0, 0) #Dept
    grid_layout.addWidget(__create_label('Number: '), 1, 0) #Number
    grid_layout.addWidget(__create_label('Area: '), 2, 0) #Area
    grid_layout.addWidget(__create_label('Title: '), 3, 0) #Title

    grid_layout.addWidget(dept, 0, 1) #Dept
    grid_layout.addWidget(num, 1, 1) #Number
    grid_layout.addWidget(area, 2, 1) #Area
    grid_layout.addWidget(title, 3, 1) #Title

    grid_frame = QFrame()
    grid_frame.setLayout(grid_layout)

    return grid_frame

#-----------------------------------------------------------------------

def __create_label(text):
    label = QLabel(text)

    # used to align text of label:
    # https://www.geeksforgeeks.org/pyqt5-how-to-align-text-of-label/
    label.setAlignment(QtCore.Qt.AlignRight)

    return label

#-----------------------------------------------------------------------

def __create_output(classes, host, port, window, list_widget):

    list_widget.clear()

    for i, regclass in enumerate(classes):
        item = QListWidgetItem()

        item.setFont(QFont("Courier", 10))
        item.setText(str(regclass))

        # Role documentation:
        # https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html
        # setData() documention:
        # https://doc.qt.io/qtforpython/PySide6/QtWidgets/
        # QListWidgetItem.html
        item.setData(QtCore.Qt.UserRole, regclass.get_class_id())

        list_widget.insertItem(i, item)

    list_widget.item(0).setSelected(True)

#-----------------------------------------------------------------------

class WorkerThread (Thread):

    def __init__(self, host, port, search, queue):
        Thread.__init__(self)
        self._host = host
        self._port = port
        self._search = search
        self._queue = queue
        self._should_stop = False

    def stop(self):
        self._should_stop = True

    def run(self):
        try:
            classes_response = __query_server_for_search(self._host, self._port, self._search)

            if not self._should_stop:
                self._queue.put((True, classes_response))
        except Exception as ex:
            if not self._should_stop:
                self._queue.put((False, ex))

#-----------------------------------------------------------------------

def poll_queue_helper(queue, books_textedit):

    item = queue.get()
    while item is not None:
        books_textedit.clear()
        successful, data = item
        if successful:
            books = data
            if len(books) == 0:
                books_textedit.insertPlainText('(None)')
            else:
                pattern = '<strong>%s</strong>: %s ($%.2f)<br>'
                for book in books:
                    books_textedit.insertHtml(pattern % book.to_tuple())
        else:
            ex = data
            books_textedit.insertPlainText(str(ex))
        books_textedit.repaint()
        item = queue.get()

#-----------------------------------------------------------------------

def __query_server_for_search(host, port, search):
    with socket() as sock:
        sock.connect((host, port))

        write_flo = sock.makefile(mode='wb')
        dump(True, write_flo)
        dump(search, write_flo)
        write_flo.flush()
        print('Sent search to server')

        read_flo = sock.makefile(mode='rb')
        query_successful = load(read_flo)

        if query_successful:
            classes = load(read_flo)
            print('Received classes from the server')
            return (True, classes)

        print('Received details from the server')
        ex_message = load(read_flo)
        return (False, ex_message)

#-----------------------------------------------------------------------

def __query_server_for_class_details(host, port, class_id):
    with socket() as sock:
        sock.connect((host, port))

        write_flo = sock.makefile(mode='wb')
        # false because this query is not a search
        dump(False, write_flo)
        dump(class_id, write_flo)
        write_flo.flush()
        print('Sent class id to server')

        read_flo = sock.makefile(mode='rb')

        query_successful = load(read_flo)

        if query_successful:
            details = load(read_flo)
            print('Received details from the server')
            return (True, details)

        print('Received exception message from server')
        ex_message = load(read_flo)
        return (False, ex_message)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    main()
