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
from pickle import dump, load
from sys import argv, stderr
from socket import socket
from threading import Thread
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QLineEdit, QLabel, QFrame,\
    QGridLayout, QVBoxLayout, QMainWindow, QMessageBox, QDesktopWidget,\
    QListWidget, QListWidgetItem
from safequeue import SafeQueue
from search import Search

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
    __set_window_properties(window)

    # Create widgets

    dept = QLineEdit()
    num = QLineEdit()
    area = QLineEdit()
    title = QLineEdit()

    list_widget = QListWidget()

    # Set event listeners

    queue, timer= __set_up_queue_and_timer(window, list_widget)
    timer.start()

    worker_thread = None

    def __initiate_search_query():
        nonlocal worker_thread

        search = Search(dept.text(), num.text(), area.text(),\
            title.text())

        if worker_thread is not None:
            worker_thread.stop()

        worker_thread = WorkerThread(host, port, search, queue)
        worker_thread.start()

    dept.textChanged.connect(__initiate_search_query)
    num.textChanged.connect(__initiate_search_query)
    area.textChanged.connect(__initiate_search_query)
    title.textChanged.connect(__initiate_search_query)

    def __initiate_class_details_query():
        __initiate_class_details_query_helper(host, port, window,\
            list_widget)

    list_widget.itemActivated.connect(__initiate_class_details_query)

    __set_up_layout(window, [__create_inputs(dept, num, area, title),\
        list_widget])

    window.show()

    # execute initial empty search to get all courses
    __initiate_search_query()

    sys.exit(app.exec_())

#-----------------------------------------------------------------------

def __set_window_properties(window):
    window.setWindowTitle('Princeton University Class Search')
    screen_size = QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)

#-----------------------------------------------------------------------

def __set_up_queue_and_timer(window, list_widget):

    queue = SafeQueue()

    def poll_queue():
        classes_response = queue.get()

        while classes_response is not None:
            process_successful, process_data = classes_response

            if process_successful:
                query_successful, query_data = process_data

                if query_successful:
                    __populate_list_with_classes(query_data,\
                        list_widget)
                else:
                    if str(query_data) is "A server error occurred. "+\
                        "Please contact the system administrator.":
                        QMessageBox.critical(window, 'Server Error',
                            str(query_data))
                    else: 
                        QMessageBox.critical(window, 'Error',
                            str(query_data))
            else:
                QMessageBox.critical(window, 'Server Error',\
                    str(process_data))

            classes_response = queue.get()

    timer = QTimer()

    timer.timeout.connect(poll_queue)
    timer.setInterval(100) # milliseconds
    timer.start()

    return queue, timer

#-----------------------------------------------------------------------

def __set_up_layout(window, widgets):
    frame = QFrame()

    layout = QVBoxLayout()

    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)

    for widget in widgets:
        layout.addWidget(widget)

    frame.setLayout(layout)
    window.setCentralWidget(frame)

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

def __populate_list_with_classes(classes, list_widget):

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

    first_item = list_widget.item(0)
    if first_item is not None:
        first_item.setSelected(True)

#-----------------------------------------------------------------------

def __query_server_for_class_details(host, port, class_id):
    print('Sent command: get_details')

    with socket() as sock:
        sock.connect((host, port))

        write_flo = sock.makefile(mode='wb')
        # false because this query is not a search
        dump(False, write_flo)
        dump(class_id, write_flo)
        write_flo.flush()

        read_flo = sock.makefile(mode='rb')

        query_successful = load(read_flo)

        if query_successful:
            details = load(read_flo)
            return (True, details)

        ex_message = load(read_flo)
        return (False, ex_message)

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
        print('Sent command: get_overviews')

        try:
            with socket() as sock:
                sock.connect((self._host, self._port))

                write_flo = sock.makefile(mode='wb')
                dump(True, write_flo)
                dump(self._search, write_flo)
                write_flo.flush()

                read_flo = sock.makefile(mode='rb')
                query_successful = load(read_flo)
                data = load(read_flo)

            if not self._should_stop:
                self._queue.put((True, (query_successful, data)))
        except Exception as ex:
            if not self._should_stop:
                self._queue.put((False, ex))

#-----------------------------------------------------------------------

def __initiate_class_details_query_helper(host, port, window,\
    list_widget):
    selected_item = list_widget.selectedItems()[0]
    class_id = selected_item.data(QtCore.Qt.UserRole)

    try:
        successful, data =\
            __query_server_for_class_details(host, port, class_id)
    except Exception as ex:
        QMessageBox.critical(window, 'Server Error', str(ex))
        return

    if successful:
        QMessageBox.information(window, 'Class Details',\
            str(data))
    else:
        QMessageBox.critical(window,\
            'Error', str(data))

#-----------------------------------------------------------------------
if __name__ == '__main__':
    main()
