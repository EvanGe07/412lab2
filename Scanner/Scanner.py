from collections import deque
import sys


# A Scanner for ILOC
class Scanner:
    # Initialize the Type table
    def __init__(self, file_obj):
        # File related variables #
        self.file = file_obj
        self.next_line = ""
        self.next_char = ''
        self.line_ptr = -1  # set to -1 because we next_char() immediately
        self.next_line_tokens = 0
        self.EoF = False
        self.lineNo = 0

        # Internal stack that stores the stream of tokens #
        self.tokens = deque()

        # Accepting State Set #
        self.SA = {5, 7, 11, 12, 18, 24, 27, 33, 35, 36, 37, 38}

        self.letter_set = [',', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '=', '>', 'I',
                           'a', 'b', 'd', 'e', 'f', 'h', 'i', 'l', 'm', 'n', 'o', 'p', 'r', 's',
                           't', 'u']

        self.delta_table = [[-1 for i in range(30)] for j in range(39)]
        self.delta_table[0] = [36, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, 34, -1, -1, 22,
                               -1, -1, -1, -1, -1, -1, 8, 19, 25, 28, -1, 13, 1, -1, -1]
        self.delta_table[1][28] = 2; self.delta_table[1][29] = 6
        self.delta_table[2][24] = 3
        self.delta_table[3][26] = 4
        self.delta_table[4][17] = 5
        # self.delta_table[5]
        self.delta_table[6][15] = 7
        # self.delta_table[7]
        self.delta_table[8][24] = 9; self.delta_table[8][27] = 14
        self.delta_table[9][14] = 10
        self.delta_table[10][16] = 11
        self.delta_table[11][13] = 12
        # self.delta_table[12]
        self.delta_table[13] = [-1, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 14, -1, -1]
        self.delta_table[14][19] = 15
        self.delta_table[15][20] = 16
        self.delta_table[16][18] = 17
        self.delta_table[17][28] = 18
        # self.delta_table[18]
        self.delta_table[19][29] = 20
        self.delta_table[20][21] = 21
        self.delta_table[21][28] = 18
        self.delta_table[22][16] = 23
        self.delta_table[23][16] = 24
        # self.delta_table[24]
        self.delta_table[25][24] = 26
        self.delta_table[26][25] = 27
        # self.delta_table[27] = {}
        self.delta_table[28][29] = 29
        self.delta_table[29][28] = 30
        self.delta_table[30][25] = 31
        self.delta_table[31][29] = 32
        self.delta_table[32][28] = 33
        # self.delta_table[33]
        self.delta_table[34][12] = 35
        # self.delta_table[35]
        # self.delta_table[36]
        self.delta_table[37] = [-1, 37, 37, 37, 37, 37, 37, 37, 37, 37, 37, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        self.delta_table[38] = [-1, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

        # Token Type Table #
        self.Type = ["invalid" for i in range(39)]
        self.Type[5] = "MEMOP"
        self.Type[7] = "ARITHOP"
        self.Type[11] = "MEMOP"
        self.Type[12] = "LOADI"
        self.Type[18] = "ARITHOP"
        self.Type[24] = "ARITHOP"
        self.Type[27] = "NOP"
        self.Type[33] = "OUTPUT"
        self.Type[35] = "INTO"
        self.Type[36] = "COMMA"
        self.Type[37] = "CONST"
        self.Type[38] = "REG"

        # Error State #
        self.se = -1

    # the pointer points at the last white space in this line,
    # WARNING: next_char doesn't get updated here, be careful!
    def clear_whitespace(self):
        while Scanner.iswhitespace(self.peek_char('n')):
            self.line_ptr += 1

    def peek_char(self, flag):
        try:
            if flag == 'n':
                return self.next_line[self.line_ptr + 1]
            elif flag == 'c':
                return self.next_line[self.line_ptr]
        except IndexError:
            return '\n'

    # SET next_char and ADVANCE line_ptr
    def next_character(self):
        self.line_ptr += 1
        try:
            self.next_char = self.next_line[self.line_ptr]
        except IndexError:
            self.next_char = '\n'

    def next_two_are_comment(self):
        try:
            if self.next_line[self.line_ptr + 1] == '/' and self.next_line[self.line_ptr + 2] == '/':
                return True
            else:
                return False
        except IndexError:
            return False


    def delta(self, state, char):
        try:
            return self.delta_table[state][self.letter_set.index(char)]
        except:
            return self.se
        # try:
        #     return self.delta_table[state][char]
        # except:
        #     return self.se

    # Roll back line_ptr but doesn't update next_char!
    def rollback(self):
        self.line_ptr -= 1
        #self.next_char = self.next_line[self.line_ptr]

    # returns <token, lexeme> if possible,
    def scan_next_word(self):
        state = 0
        lexeme = ""
        stack = ["bad"]

        # check new-line
        #if self.next_char == '\n':
        #if self.next_line[self.line_ptr + 1] == '\n':
        if self.peek_char('n') == '\n':
            self.line_ptr += 1
            #self.lineNo += 1
            return "\n"

        # check comment
        if self.next_two_are_comment():
            #print "comment detected!"
            #self.lineNo += 1
            return "//"

        while state != self.se:
            #print "next char: ", self.next_character()
            self.next_character()
            lexeme += self.next_char

            # print "lexeme", lexeme
            # print "state: ", state
            # print "next char", self.next_char

            if state in self.SA:
                stack = []
            stack.append(state)

            #print "state, next_char input", state, self.next_char
            #print self.delta_table[0]
            state = self.delta(state, self.next_char)
            #print "updated state:", state

        trunc = ""
        while state not in self.SA and state != "bad":
            state = stack.pop()
            #print "lexeme: ", lexeme
            if lexeme:
                trunc = lexeme[-1] + trunc
            lexeme = lexeme[: - 1]
            #lexeme = Scanner.truncate(lexeme)
            #print "pointer", self.line_ptr
            self.rollback()
        #print "STATE", state

        if state in self.SA:
            if self.Type[state] == "REG":
                return self.Type[state], int(lexeme[1:]), self.lineNo
            elif self.Type[state] == "CONST":
                return self.Type[state], int(lexeme), self.lineNo
            else:
                return self.Type[state], lexeme, self.lineNo
        else:
            #Scanner.error("Invalid token!")
            #print "appear once only"
            Scanner.lex_error(trunc, self.lineNo)
            return "invalid", trunc, self.lineNo

    # scans the next available line and store the stream of tokens
    def scan_next_line(self):
        self.next_line = self.file.readline()
        self.lineNo += 1
        self.line_ptr = -1
        self.next_char = ''
        self.next_line_tokens = 0

        # scans the line until 1) reaches \n; 2) finds an invalid lexical error;
        if self.next_line == "":
            self.EoF = True
        else:
            is_eol = Scanner.isEoL(self.peek_char('n'))
            #is_comment = self.next_two_are_comment()
            #print "line", self.next_line
            self.clear_whitespace()
            token = self.scan_next_word()
            #print self.tokens
            #print "POGGERS", token
            # if token[0] == "invalid":
            #     self.tokens.append(token)
            while token[0] != "invalid" and not is_eol and token != "//": #not is_comment:
                self.clear_whitespace()
                is_eol = Scanner.isEoL(self.peek_char('n'))
                self.tokens.append(token)
                self.next_line_tokens += 1
                token = self.scan_next_word()

    # pops the next <token, lexeme> pair or "invalid" from the queue, or EoF,
    # or Nothing if the next line consists of comments, '\n', or whitespaces
    def next_word(self):
        #print self.tokens
        if self.EoF:
            #print "I'd be surprised if this gets triggered!"
            return "EoF"
        elif self.tokens:
            return self.tokens.popleft()
        else:
            self.scan_next_line()
            #print "POG", self.tokens
            if self.EoF:
                return "EoF"
            elif self.tokens:
                #return "EoF" if self.EoF else self.tokens.popleft()
                return self.tokens.popleft()
            # self.next_word()

    # Static Helper Methods #
    @staticmethod
    def truncate(lexeme):
        return lexeme[: - 1]

    @staticmethod
    def error(msg):
        print(msg)

    @staticmethod
    def iswhitespace(string):
        return True if (string == " " or string == "\t") else False

    @staticmethod
    def isEoL(string):
        return True if string == '\n' else False

    @staticmethod
    def lex_error(word, lineNo):
        print >> sys.stderr, "Lexical Error: %i: \"%s\" is not a valid word." % (lineNo, word)