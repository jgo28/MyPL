#!/usr/bin/python3
#
# Author: Joshua Go
# Course: CPSC 326, Spring 2019
# Assignment: 6
# Description:
#   Identifies token types such as comma and while. It takes in a source file written in MyPL and outputs the set of
#   tokens in the file.
# ----------------------------------------------------------------------

import mypl_token as token
import mypl_error as error

import mypl_token as token
import mypl_error as error

class Lexer(object):

    def __init__(self, input_stream):
        self.line = 1
        self.column = 0
        self.input_stream = input_stream

    def __peek(self):
        pos = self.input_stream.tell()
        symbol = self.input_stream.read(1)
        self.input_stream.seek(pos)
        return symbol

    def __read(self):
        return self.input_stream.read(1)

    def __isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def next_token(self):
        global symbol, endLine, isComment, isString, firstColumn, foundSymbol, foundFirstCol
        symbol = ''
        isComment = False   # checks if the input is a comment
        endLine = False     # indicates if it is the end of the line
        isString = False    # indicates if the symbol is a string
        firstColumn = 0   # tracks the first column of a symbol
        foundFirstCol = False   # first column on symbol has been found
        foundSymbol = False     # indicates if a symbol is found
        # read until end of file or until last symbol
        while self.__peek() != '' or foundSymbol:
            if symbol.isspace() and not isString:
                symbol = ''
            # if it is the end of the line, increment line number and reset variables
            if self.__peek() == '\n':
                if isString:
                    raise error.MyPLError('reached newline reading string', self.line, self.column + 1)
                if isComment:
                    symbol = ''
                isComment = False
                self.__read()  # read the '\n'
                endLine = True
            # end of the string
            if self.__peek() == '"' and isString:
                isString = False
                self.__read()
                self.column += 1
                if self.__peek() == ' ':
                    self.__read()
                    self.column += 1
                return token.Token(token.STRINGVAL, symbol, self.line, firstColumn)
            # read next symbol if not end of line
            if not endLine and not foundSymbol:
                # skip over symbol that is commented
                if isComment:
                    self.__read()
                else:
                    symbol += self.__read()     # add character to current symbol
                    if isString:
                        self.column += 1
            # if the token is a comment, ignore the line
            if symbol == '#':
                isComment = True
            # token is a string
            if symbol == '"' and not isString:
                symbol = ''
                self.column += 1
                firstColumn = self.column
                isString = True
            # symbol is a token
            if not isComment and not isString:
                if not foundFirstCol:
                    firstColumn = self.column + 1
                    foundFirstCol = True
                if not foundSymbol:
                    self.column += 1
                # compare symbol to the token types in mypl_token.py
                if self.__peek() == " " or endLine or foundSymbol or self.__peek() == '':
                    # read the whitespace if it is not the end of the line
                    if not endLine and not foundSymbol:
                        self.__read()
                        self.column += 1
                    symLength = len(symbol)     # length of symbol
                    # subtract symbol length to get column position before increments
                    if foundSymbol:
                        column = firstColumn
                    else:
                        column = self.column - symLength    # original column of the token
                    line = self.line    # original line of the token
                    sym = symbol    # create copy of the symbol
                    # reset the symbol, go to new line
                    if endLine:
                        symbol = ''
                        self.line += 1
                        self.column = 0
                        endLine = False
                    if symLength > 0:
                        #
                        #   MATHEMATICAL EXPRESSIONS
                        #
                        if sym == '=':  # symbol is '=' or '=='
                            return token.Token(token.ASSIGN, sym, line, column)
                        elif sym == '==':
                            return token.Token(token.EQUAL, sym, line, column)
                        elif sym == '<':  # symbol is '<' or '<=':
                            return token.Token(token.LESS_THAN, sym, line, column)
                        elif sym == '<=':
                            return token.Token(token.LESS_THAN_EQUAL, sym, line, column)
                        elif sym == '>':  # symbol is '>' or '>='
                            return token.Token(token.GREATER_THAN, sym, line, column)
                        elif sym == '>=':
                            return token.Token(token.GREATER_THAN_EQUAL, sym, line, column)
                        elif sym == '!=':  # symbol is not equal (!=)
                            return token.Token(token.NOT_EQUAL, sym, line, column)
                        elif sym == '+':
                            return token.Token(token.PLUS, sym, line, column)
                        elif sym == '-':
                            return token.Token(token.MINUS, sym, line, column)
                        elif sym == '*':
                            return token.Token(token.MULTIPLY, sym, line, column)
                        elif sym == '%':
                            return token.Token(token.MODULO, sym, line, column)
                        #
                        #   PUNCTUATION
                        #
                        elif sym == ':':
                            return token.Token(token.COLON, sym, line, column)
                        elif sym == '/':
                            return token.Token(token.DIVIDE, sym, line, column)
                        elif sym == '.':
                            return token.Token(token.DOT, sym, line, column)
                        elif sym == ',':
                            return token.Token(token.COMMA, sym, line, column)
                        elif sym == ';':
                            return token.Token(token.SEMICOLON, sym, line, column)
                        elif sym == '(':
                            return token.Token(token.LPAREN, sym, line, column)
                        elif sym == ')':
                            return token.Token(token.RPAREN, sym, line, column)
                        #
                        #   CHARACTERS
                        #
                        elif sym == 'if':
                            return token.Token(token.IF, sym, line, column)
                        elif sym == 'else':
                            return token.Token(token.ELSE, sym, line, column)
                        elif sym == 'elif':
                            return token.Token(token.ELIF, sym, line, column)
                        elif sym == 'while':
                            return token.Token(token.WHILE, sym, line, column)
                        elif sym == 'then':
                            return token.Token(token.THEN, sym, line, column)
                        elif sym == 'do':
                            return token.Token(token.DO, sym, line, column)
                        elif sym == 'not':
                            return token.Token(token.NOT, sym, line, column)
                        elif sym == 'end':
                            return token.Token(token.END, sym, line, column)
                        elif sym == 'return':
                            return token.Token(token.RETURN, sym, line, column)
                        elif sym == 'new':
                            return token.Token(token.NEW, sym, line, column)
                        elif sym == 'nil':
                            return token.Token(token.NIL, sym, line, column)
                        elif sym == 'set':
                            return token.Token(token.SET, sym, line, column)
                        elif sym == 'and':
                            return token.Token(token.AND, sym, line, column)
                        elif sym == 'or':
                            return token.Token(token.OR, sym, line, column)
                        elif sym == 'fun':
                            return token.Token(token.FUN, sym, line, column)
                        #
                        #   CHARACTERS: TYPES
                        #
                        elif sym == 'bool':
                            return token.Token(token.BOOLTYPE, sym, line, column)
                        elif sym == 'int':
                            return token.Token(token.INTTYPE, sym, line, column)
                        elif sym == 'float':
                            return token.Token(token.FLOATTYPE, sym, line, column)
                        elif sym == 'string':
                            return token.Token(token.STRINGTYPE, sym, line, column)
                        elif sym == 'struct':
                            return token.Token(token.STRUCTTYPE, sym, line, column)
                        elif sym == 'var':
                            return token.Token(token.VAR, sym, line, column)
                        #
                        #   CHARACTERS: VALUES
                        #
                        elif sym == 'true' or sym == 'false':
                            return token.Token(token.BOOLVAL, sym, line, column)
                        elif sym.isdigit():
                            # numbers such as 01 are not valid
                            if sym[0] == '0' and symLength > 1:     # check if the number is valid
                                raise error.MyPLError('unexpected symbol "' + sym + '"', line, column)
                            return token.Token(token.INTVAL, sym, line, column)
                        else:
                            global numDecimals, hasDecimal, isNumber, numberInFront
                            numDecimals = 0     # number of decimal places
                            hasDecimal = False  # number has a '.'
                            isNumber = True     # symbol is a number
                            numberInFront = False   # the symbol starts with a number
                            if sym[0].isdigit():    # first value of symbol is a digit
                                numberInFront = True
                            # checks to see if value is a float
                            for i in sym:
                                if not i.isdigit():
                                    # throw error if the symbol starts with a number and also has characters
                                    if i.isalpha and numberInFront and i != '.':
                                        raise error.MyPLError('unexpected symbol "' + i + '"', line, column)
                                    if i == '.':
                                        # throw error if '.' is lacking a number after it
                                        if numberInFront and i == sym[-1]:
                                            raise error.MyPLError('missing digit in float value', line,
                                                                  column + 1 + sym.index('.'))
                                        numDecimals += 1
                                    else:
                                        isNumber = False
                                if numDecimals == 1:
                                    hasDecimal = True
                            # value is a float
                            if isNumber and hasDecimal:
                                return token.Token(token.FLOATVAL, sym, line, column)
                            # value is an ID
                            else:
                                if not sym.isspace():
                                    if foundSymbol:
                                        return token.Token(token.ID, sym, line, firstColumn)
                                    return token.Token(token.ID, sym, line, column)
                # when there is no whitespace between characters
                elif symbol.isalpha() or symbol.isdigit() or self.__isfloat(symbol):
                    if self.__peek() == ";" or self.__peek() == "(" or self.__peek() == ")":
                        foundSymbol = True
                    elif self.__peek() == '=' and symbol[0].isalpha():
                        foundSymbol = True
                    elif self.__peek() == "!":
                        foundSymbol = True
                    elif self.__peek() == "<":
                        foundSymbol = True
                    elif self.__peek() == ">":
                        foundSymbol = True
                    elif self.__peek() == ":":
                        foundSymbol = True
                    elif self.__peek() == ",":
                        foundSymbol = True
                    elif not symbol.isdigit() and symbol.isalpha() and self.__peek() == ".":
                        foundSymbol = True
                    elif self.__peek() == '%':
                        foundSymbol = True
                    elif self.__peek() == '+':
                        foundSymbol = True
                    elif self.__peek() == '/':
                        foundSymbol = True
                    elif self.__peek() == '-':
                        foundSymbol = True
                elif self.__peek() == '=' and symbol[0].isalpha():
                    foundSymbol = True
                elif symbol == '=' and self.__peek().isdigit():
                    foundSymbol = True
                elif symbol == '==' and self.__peek().isdigit():
                    foundSymbol = True
                elif self.__peek() == ",":
                    foundSymbol = True
                elif symbol == ',':
                    foundSymbol = True
                elif not symbol.isalpha() and not symbol.isdigit() and self.__peek() == '.':
                    foundSymbol = True
                elif symbol == ':':
                    foundSymbol = True
                elif symbol == '%':
                    foundSymbol = True
                elif symbol == '+':
                    foundSymbol = True
                elif symbol == '/':
                    foundSymbol = True
                elif symbol == '-':
                    foundSymbol = True
                elif self.__peek() == '=' and symbol[-1].isdigit():
                    foundSymbol = True
                elif self.__peek().isalpha() and symbol[-1] == '.':
                    foundSymbol = True
                elif symbol == '!=':
                    if self.__peek().isdigit() or self.__peek().isalpha() or self.__isfloat(symbol):
                        foundSymbol = True
                elif symbol == '<=':
                    if self.__peek().isdigit() or self.__peek().isalpha() or self.__isfloat(symbol):
                        foundSymbol = True
                elif symbol == '>=':
                    if self.__peek().isdigit() or self.__peek().isalpha() or self.__isfloat(symbol):
                        foundSymbol = True
                elif symbol == '=':
                    if self.__peek() == '=':
                        if self.__peek().isdigit() or self.__peek().isalpha() or self.__isfloat(symbol):
                            foundSymbol = True
                    else:
                        foundSymbol = True
                elif self.__peek() == '"' or self.__peek() == ";" or self.__peek() == "(" or \
                        self.__peek() == ")":
                    if self.__peek().isdigit() or self.__peek().isalpha() or self.__isfloat(symbol):
                        foundSymbol = True
                    foundSymbol = True
                elif self.__peek() == ":":
                    foundSymbol = True
                elif symbol[0] == ';' or symbol[0] == '(' or symbol[0] == ')':
                    foundSymbol = True

        # end of the file
        self.column = 0
        return token.Token(token.EOS, '', self.line, self.column)