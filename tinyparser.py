
import sys
from lexer import Lexer
from token import TokenType

class Parser(object):

    def __init__(self, lexer,emitter):
        self.lexer = lexer
        self.emitter = emitter
        self.symbols = set()
        self.labelsDeclared = set()
        self.labelsGotoed = set()

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()
    def checkToken(self,kind):
        return kind == self.curToken.kind

    def checkPeek(self,kind):
        return kind == self.peekToken.kind

    def match(self,kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
    def abort(self, message):
        sys.exit("Error. " + message)
    def program(self):
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(void) {")
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        while not self.checkToken(TokenType.EOF):
            self.statement()
        self.emitter.emitLine("\treturn 0;")
        self.emitter.emitLine("}")
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)
    def statement(self):
        self.tabs = 1
        if self.checkToken(TokenType.PRINT):
            self.nextToken()
            if self.checkToken(TokenType.STRING):
                self.emitter.emitLine("\t"*self.tabs+"printf(\"" + self.curToken.text + "\\n\");")
                self.nextToken()
            else:
                self.emitter.emit("\t"*self.tabs+"printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emitLine("\t"*self.tabs+"));")
        elif self.checkToken(TokenType.IF):
            self.nextToken()
            self.emitter.emit( "\t"*self.tabs+"if (")
            self.tabs = self.tabs * 2
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine(") {")
            while not self.checkToken(TokenType.ENDIF):
                self.statement()
            self.match(TokenType.ENDIF)
            self.emitter.emitLine("\t"*self.tabs+"}")
        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            self.emitter.emit("\t"*self.tabs+"while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine(") {")

            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()
            self.match(TokenType.ENDWHILE)
            self.emitter.emitLine("\t"*self.tabs+"}")
        elif self.checkToken(TokenType.LABEL):
            self.nextToken()

            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)
            self.emitter.emitLine("\t"*self.tabs + self.curToken.text + ":")
            self.match(TokenType.IDENT)
        elif self.checkToken(TokenType.GOTO):
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.emitter.emitLine("\t" * self.tabs + self.curToken.text + ";")
            self.match(TokenType.IDENT)
        elif self.checkToken(TokenType.LET):
            self.nextToken()
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("\t" * self.tabs + "float " + self.curToken.text + ";")
            self.emitter.emit("\t" * self.tabs +  self.curToken.text + "=")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            self.emitter.emitLine(";")
        elif self.checkToken(TokenType.INPUT):
            self.nextToken()
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("\tfloat " + self.curToken.text + ";")
            self.emitter.emitLine("if(= == scanf(\"%" + "f\", &" + self.curToken.text + ")) {")
            self.emitter.emitLine(self.curToken.text + "= 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)
        else:
            self.abort("Invalid statement at " + self.curToken.text + "(" + self.curToken.kind.name + ")")
        self.nl()
    
    def comparison(self):
        self.expression()

        if self.isCOmparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison operatpor at: " + self.curToken.text)
        while self.isCOmparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
    def isCOmparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)
    def expression(self):
        self.term()

        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()
    def term(self):
        self.unary()

        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()
    
    def unary(self):
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary()
    def primary(self):
        if self.checkToken(TokenType.INTEGER) or self.checkToken(TokenType.FLOAT):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            self.abort("Unexpected token at " + self.curToken.text)
    def nl(self):
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()