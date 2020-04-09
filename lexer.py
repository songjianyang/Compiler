NUMBER, STRING, ID, WORD = 'NUMBER', 'STRING', 'ID', 'WORD'
ADD, SUB, MUL, DIV, ASSIGN = 'ADD', 'SUB', 'MUL', 'DIV', 'ASSIGN'
CMPGT, CMPLT, EQUAL = 'CMPGT', 'CMPLT', 'EQUAL'
LBRACKET, RBRACKET, LPAREN, RPAREN = 'LBRACKET', 'RBRACKET', 'LPAREN', 'RPAREN'
COMMA, QUOT, PERCENT = 'COMMA', 'QUOT', 'PERCENT'
LINEEND, SPACE, EOF = ';', ' ', 'EOF'
 

class Token():
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value))

    def __repr__(self):
        return self.__str__()


class Lexer():
    def __init__(self, text):
        self.text = self.readfile(text)
        self.pos = 0
        self.isEOF = False

    def get_number(self):
        result = ''
        while self.pos <= len(self.text) - 1 and self.text[self.pos].isdigit():
            result += self.text[self.pos]
            self.pos += 1
        return int(result)

    def get_word(self):
        result = ''
        while self.pos <= len(self.text) - 1 and self.text[self.pos].isalpha():
            result += self.text[self.pos]
            self.pos += 1
        return result

    def get_str(self):
        result = '"'
        self.pos += 1
        while self.pos <= len(self.text) - 1 and self.text[self.pos] != '"':
            result += self.text[self.pos]
            self.pos += 1
        self.pos += 1
        result += '"'
        return result

    def skip_space(self):
        while self.pos <= len(self.text) - 1 and self.text[self.pos] == SPACE:
            self.pos += 1
        return self.pos

    def get_next_token(self):
        text = self.text
        pos = self.pos

        if self.pos > len(text) - 1:
            self.isEOF = True
            return Token(EOF, None)
        if text[pos] == SPACE:
            self.skip_space()
            return self.get_next_token()
        if text[pos] == LINEEND:
            self.pos += 1
            return self.get_next_token()

        if text[pos].isalpha():
            content = self.get_word()
            if content in ('if', 'while', 'else', 'def', 'print', 'return'):
                token = Token(ID, content)
            else:
                token = Token(WORD, content)
            return token
        elif text[pos].isdigit():
            token = Token(NUMBER, self.get_number())
            return token
        elif text[pos] == '"':
            token = Token(STRING, self.get_str())
            return token
        elif text[pos] == '+':
            token = Token(ADD, text[pos])
            self.pos += 1
            return token
        elif text[pos] == '-':
            token = Token(SUB, text[pos])
            self.pos += 1
            return token
        elif text[pos] == '*':
            token = Token(MUL, text[pos])
            self.pos += 1
            return token
        elif text[pos] == '/':
            token = Token(DIV, text[pos])
            self.pos += 1
            return token
        elif text[pos] == '{':
            token = Token(LBRACKET, text[pos])
            self.pos += 1
            return token
        elif text[pos] == '}':
            token = Token(RBRACKET, text[pos])
            self.pos += 1
            return token
        elif text[pos] == '>':
            token = Token(CMPGT, text[pos])
            self.pos += 1
            return token
        elif text[pos] == '<':
            token = Token(CMPLT, text[pos])
            self.pos += 1
            return token
        elif text[pos] == ',':
            token = Token(COMMA, text[pos])
            self.pos += 1
            return token
        elif text[pos] == '(':
            token = Token(LPAREN, text[pos])
            self.pos += 1
            return token
        elif text[pos] == ')':
            token = Token(RPAREN, text[pos])
            self.pos += 1
            return token
        elif text[pos] == '%':
            token = Token(PERCENT, text[pos])
            self.pos += 1
            return token
        elif text[pos] == '=':
            if text[pos + 1] == '=':
                token = Token(EQUAL, '==')
                self.pos += 2
            else:
                token = Token(ASSIGN, text[pos])
                self.pos += 1
            return token

        self.pos += 1

    def lexer(self):
        result = []
        while self.isEOF == False:
            result.append(self.get_next_token())
        return result

    def readfile(self, filename):
        text = ''
        for line in file(filename):
            line.strip()
            line = line.replace('\n', ' ')
            text += line
        return text



