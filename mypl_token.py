#!/usr/bin/python3
#
# Author: Joshua Go
# Description:
#   This is part of a lexical analyzer program for MyPL that identifies token types such as comma and while. This file
#   provides the list of tokens MyPL uses. It will take in the current token and see if it matches any of the ones
#   listed.
# ----------------------------------------------------------------------

ASSIGN = 'ASSIGN'
EQUAL = 'EQUAL'
NOT_EQUAL = 'NOT_EQUAL'
MULTIPLY = 'MULTIPLY'
FLOATTYPE = 'FLOATTYPE'
NOT = 'NOT'
ELSE = 'ELSE'
SET = 'SET'
BOOLVAL = 'BOOLVAL'
COMMA = 'COMMA'
GREATER_THAN = 'GREATER_THAN'
PLUS = 'PLUS'
STRINGTYPE = 'STRINGTYPE'
WHILE = 'WHILE'
ELIF = 'ELIF'
RETURN = 'RETURN'
INTVAL = 'INTVAL'
GREATER_THAN_EQUAL = 'GREATER_THAN_EQUAL'
STRUCTTYPE = 'STRUCTTYPE'
DO = 'DO'
END = 'END'
NEW = 'NEW'
FLOATVAL = 'FLOATVAL'
DIVIDE = 'DIVIDE'
LESS_THAN = 'LESS_THAN'
MINUS = 'MINUS'
BOOLTYPE = 'BOOLTYPE'
AND = 'AND'
IF = 'IF'
FUN = 'FUN'
NIL = 'NIL'
STRINGVAL = 'STRINGVAL'
LESS_THAN_EQUAL = 'LESS_THAN_EQUAL'
MODULO = 'MODULO'
INTTYPE = 'INTTYPE'
OR = 'OR'
THEN = 'THEN'
VAR = 'VAR'
ID = 'ID'
COLON = 'COLON'
DOT = 'DOT'
SEMICOLON = 'SEMICOLON'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
EOS = 'EOS'
# token types


class Token(object):

    def __init__(self, tokentype, lexeme, line, column):
        self.tokentype = tokentype
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __call__(self):
        return self

    def __str__(self):
        return "%s '%s' %i:%i" % (self.tokentype, self.lexeme, self.line, self.column)