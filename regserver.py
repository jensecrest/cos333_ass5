#!/usr/bin/env python

#--------------------------------------------------------------------------------
# regserver.py
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
from sys import stderr, argv
from os import name
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from pickle import load, dump
from database import create_condition_and_prepared_values, get_class_details, get_classes_with_condition
from search import Search

DATABASE_URL = 'file:reg.sqlite?mode=ro'

#-----------------------------------------------------------------------

def handle_client(sock):
    read_flo = sock.makefile(mode='rb')
    request_type_is_search = load(read_flo)
    data = load(read_flo)

    response = None

    if request_type_is_search:
        print('Read search from client: ' + str(data))

        # if we're executing a search then data will be a Search
        db_values = create_condition_and_prepared_values(data)
        response = get_classes_with_condition(db_values[0], db_values[1])
    
    # if it's not a search, then it's a request for class details
    else:
        print('Read class details request from client: ' + str(data))

        # if we're getting class details, data will be the class id as a string
        response = get_class_details(data)

    write_flo = sock.makefile(mode='wb')

    dump(True, write_flo) # query succeeded!
    dump(response, write_flo)
    
    write_flo.flush()
    print('Wrote response to client')

    # TODO: add exception handling - write False and error message if it's false

#-----------------------------------------------------------------------

def main():
    """ TODO: UPDATE
    Parse the command-line args, create a query and use that query to print
    the relevant course table.
    """

    try:
        parser = argparse.ArgumentParser(allow_abbrev=False,
        description="Server for the registrar application")
        parser.add_argument("port", type=int,
        help = "the port at which the server should listen")

        args = parser.parse_args()
        port = args.port

        try:
            server_sock = socket()
            print('Opened server socket')
            if name != 'nt':
                server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            server_sock.bind(('', port))
            print('Bound server socket to port')
            server_sock.listen()
            print('Listening')
            while True:
                try:
                    sock, client_addr = server_sock.accept()
                    with sock:
                        print('Accepted connection for ' + str(client_addr))
                        print('Opened socket for ' + str(client_addr))
                        handle_client(sock)
                except Exception as ex:
                    print(ex, file=stderr)
        except Exception as ex:
            print(ex, file=stderr)
            exit(1)

    # TODO: UPDATE EXCEPTIONS
    except sqlite3.DatabaseError as ex:
        print(argv[0] + ": " + str(ex), file=stderr)
        sys.exit(1)
    except ValueError as ex:
        print(argv[0] + ": " + str(ex), file=stderr)
        sys.exit(1)
    except argparse.ArgumentError as ex:
        print(argv[0] + ": " + str(ex), file=stderr)
        sys.exit(2)

#--------------------------------------------------------------------------------
if __name__ == '__main__':
    main()