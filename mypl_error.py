#!/usr/bin/python3
#
# Author: Joshua Go
# Course: CPSC 326, Spring 2019
# Assignment: 6
# Description:
#   Generates an error message if an error is found in the syntax, type, or grammer of a MyPL file.
# ----------------------------------------------------------------------

class MyPLError(Exception):

    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        msg = self.message
        line = self.line
        column = self.column
        return 'error: %s at line %i column %i' % (msg, line, column)
