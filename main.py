
import sys
from lexer import Lexer
from tinyparser import Parser
from emitter import Emitter

def main():
    print("Teeny tiny compiler")
    if len(sys.argv) != 2:
        sys.exit("Error: COmpiler needs source file as argument")
    with open(sys.argv[1], 'r') as inputFile:
        source = inputFile.read()
    lexer = Lexer(source)
    emitter = Emitter("out.c")
    parser = Parser(lexer,emitter)
    parser.program()
    emitter.writeFile()
    print("Compiling complete")
if __name__=='__main__':
    main()