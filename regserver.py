#!/usr/bin/env python

#-----------------------------------------------------------------------
# regserver.py
# Authors: Jennifer Secrest and AnneMarie Caballero
#-----------------------------------------------------------------------

"""
Creates a server that handles requests for class lists and
class details by receiving requests written to the server, and
responding to them with a boolean as to whether that
request was successful and the pertinent information (
e.g. either a class list or the details for a class.)
"""

import argparse
import sqlite3
import sys
from sys import stderr, argv
from os import name
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from pickle import load, dump
from database import create_condition_and_prepared_values,\
    get_class_details, get_classes_with_condition

DATABASE_URL = 'file:reg.sqlite?mode=ro'

#-----------------------------------------------------------------------

def handle_client(sock):
    """
    Handles a request from the client for either a class list
    or class details by reading in the request information
    from the passed-in socket sock: a boolean indicating
    whether or not it is a search [which is a class list request;
    if not, it's  a class details request], and the relevant query
    information [either a Search or a class id]. Then,
    queries the reg.sqlite database using the database module
    to return the response information:either True and the requested
    data, or False and the pertinent error information.

    Keyword arguments:
        sock -- the socket to be reading and writing information to
    """
    read_flo = sock.makefile(mode='rb')
    request_type_is_search = load(read_flo)
    data = load(read_flo)

    response = None
    write_flo = sock.makefile(mode='wb')

    try:
        if request_type_is_search:
            print('Read search from client: ' + str(data))

            # if we're executing a search then data will be a Search
            db_values = create_condition_and_prepared_values(data)
            response = get_classes_with_condition(db_values[0],\
                db_values[1])

        # if it's not a search, then it's a request for class details
        else:
            print('Read class details request from client: ' +\
                str(data))

            # if we're getting class details,
            # data will be the class id as a string
            response = get_class_details(data)

        dump(True, write_flo) # query succeeded!
        dump(response, write_flo)

    except ValueError as ex:
        print(str(ex), file=stderr)
        dump(False, write_flo)
        dump(str(ex), write_flo)

    except sqlite3.DatabaseError as ex:
        print(str(ex), file=stderr)
        dump(False, write_flo)
        dump('A server error occurred. '+\
            'Please contact the system administrator.', write_flo)

    write_flo.flush()
    print('Wrote response to client')

#-----------------------------------------------------------------------

def main():
    """
    Parses the command-line argument of a port, and connects the
    server to this port. Then, until server is closed, handles requests
    for class lists (including overviews) and class details
    from the registrar database.
    """

    try:
        parser = argparse.ArgumentParser(allow_abbrev=False,
        description="Server for the registrar application")
        parser.add_argument("port", type=int,
        help = "the port at which the server should listen")
        # parser.add_argument("port", type=int,
        # help = "the port at which the server should listen")

        args = parser.parse_args()
        port = args.port
        # delay = args.delay

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
                        print('Accepted connection for ' +\
                            str(client_addr))
                        print('Opened socket for ' + str(client_addr))

                        handle_client(sock)

                    print('Closed socket')
                except Exception as ex:
                    print(ex, file=stderr)
                    sys.exit(1)
        except Exception as ex:
            print(ex, file=stderr)
            sys.exit(1)

    except argparse.ArgumentError as ex:
        print(argv[0] + ": " + str(ex), file=stderr)
        sys.exit(2)

#-----------------------------------------------------------------------
if __name__ == '__main__':
    main()
