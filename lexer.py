

import sys
from token import Token,TokenType
class Lexer(object):

    def __init__(self, input):
        self.source = input + "\n\n"
        self.curChar = ''
        self.curPos = -1
        self.nextChar()
    def nextChar(self):
        self.curPos += 1
        if self.curPos >= len (self.source):
            self.curChar = '\0'
        else:
            self.curChar = self.source[self.curPos]
    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos + 1]
    def abort(self, msg):
        sys.exit("Lexing error: " + msg)
    def skipWhitepace(self):
        while self.curChar == '\t' or self.curChar == '\r' or self.curChar == ' ':
            self.nextChar()
    def skipComment(self):
        if self.curChar == '#':
            while self.curChar != '\n':
                self.nextChar()
    def getToken(self):
        token = None
        self.skipWhitepace()
        self.skipComment()
        if self.curChar == '+':
            token = Token(self.curChar,TokenType.PLUS)
        elif self.curChar == '-':
            token = Token(self.curChar,TokenType.MINUS)
        elif self.curChar == '*':
            token = Token(self.curChar,TokenType.ASTERISK)
        elif self.curChar == '/':
            token = Token(self.curChar,TokenType.SLASH)
        elif self.curChar == '=':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar+self.curChar, TokenType.EQEQ)
            else:
                token = Token(self.curChar, TokenType.EQ)
        elif self.curChar == '>':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar+self.curChar, TokenType.GTEQ)
            else:
                token = Token(self.curChar, TokenType.GT)
        elif self.curChar == '<':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar+self.curChar, TokenType.LTEQ)
            else:
                token = Token(self.curChar, TokenType.LT)
        elif self.curChar == '!':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar+self.curChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())
        elif self.curChar == '\"':
            self.nextChar()
            startPos = self.curPos

            while self.curChar != '\"':
                if self.curChar == '\r' or self.curChar == '\n' or self.curChar == '\t' or self.curChar == '\\' or self.curChar == '%':
                    self.abort("Illegal character in string ")
                self.nextChar()
            tokText = self.source[startPos : self.curPos]
            token = Token(tokText, TokenType.STRING)
        elif self.curChar.isdigit():
            startPos = self.curPos
            this_type = TokenType.INTEGER
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.':
                this_type = TokenType.FLOAT
                self.nextChar()
                if not self.peek().isdigit():
                    self.abort("Illegal character in float")
                while self.peek().isdigit():
                    self.nextChar()
            tokText = self.source[startPos:self.curPos + 1]
            token = Token(tokText, this_type)
        elif self.curChar.isalpha():
            startPos = self.curPos
            while self.peek().isalnum():
                self.nextChar()
            tokText = self.source[startPos:self.curPos+1]
            keyword = Token.checkIfKeyWord(tokText)
            if keyword == None:
                token = Token(tokText,TokenType.IDENT)
            else:
                token = Token(tokText, keyword)  
        elif self.curChar == '\n':
            token = Token(self.curChar,TokenType.NEWLINE)
        elif self.curChar == '\0':
            token = Token(self.curChar,TokenType.EOF)
        else:
            self.abort("Unknown token: " + self.curChar)

        self.nextChar()
        return token