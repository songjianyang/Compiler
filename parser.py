from lexer import *


class Parser():
    def __init__(self, filename):
        self.token_stream = Lexer(filename).lexer()
        self.token_index = 0
        self.current_token = self.token_stream[self.token_index]
        self.arg = ''
        self.if_num = 0
        self.while_num = 0
        self.code = []
        self.func_code = []
        self.func_name = ''

    def error(self):
        raise Exception('Error parsing input')

    def peek(self, index):
        return self.token_stream[self.token_index + index]

    def eat(self, type):
        if self.current_token.type in type:
            self.token_index += 1
            self.current_token = self.token_stream[self.token_index]
        else:
            self.error()

    def factor(self):
        if self.current_token.type == NUMBER:
            num = self.current_token
            self.eat(NUMBER)
            return self.code.append(['push', num.value])
        elif self.current_token.type == WORD:
            word = self.current_token
            self.eat(WORD)
            return self.code.append(['push', self.func_name + word.value])
        elif self.current_token.type == STRING:
            string = self.current_token
            self.eat(STRING)
            return self.code.append(['push', string.value])
        return self.error()

    def term(self):
        self.factor()
        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
                self.factor()
                self.code.append(['mul'])
            elif token.type == DIV:
                self.eat(DIV)
                self.factor()
                self.code.append(['div'])
        return self.code

    def expr(self):
        self.term()
        while self.current_token.type in (ADD, SUB, CMPLT, CMPGT, EQUAL):
            token = self.current_token
            if token.type == ADD:
                self.eat(ADD)
                self.term()
                self.code.append(['add'])
            elif token.type == SUB:
                self.eat(SUB)
                self.term()
                self.code.append(['sub'])
            elif token.type == CMPGT:
                self.eat(CMPGT)
                self.expr()
                self.code.append(['cmpgt'])
                self.code.append(['jle', '$'])
            elif token.type == CMPLT:
                self.eat(CMPLT)
                self.expr()
                self.code.append(['cmplt'])
                self.code.append(['jge', '$'])
            elif token.type == EQUAL:
                self.eat(EQUAL)
                self.expr()
                self.code.append(['cmp'])
                self.code.append(['jne', '$'])
        return self.code

    def variable(self):
        if self.current_token.type == WORD:
            name = self.current_token.value
            if name == 'var':
                self.eat(WORD)
                self.code.append(['var', self.func_name + self.current_token.value])
                self.eat(WORD)
                while self.current_token.type == COMMA:
                    self.eat(COMMA)
                    if self.current_token.type == WORD:
                        self.code.append(['var', self.func_name + self.current_token.value])
                        self.eat(WORD)
            else:
                self.eat(WORD)
                if self.current_token.type == ASSIGN:
                    self.eat(ASSIGN)
                    if self.current_token.type == STRING:
                        self.code.append(['push', self.current_token.value])
                        self.eat(STRING)
                    else:
                        self.expr()
                    self.code.append(['pop', self.func_name + name])
        return self.code

    def block(self):
        if self.current_token.type == LBRACKET:
            self.eat(LBRACKET)
            while self.current_token.type is not RBRACKET:
                self.statement()
                if self.current_token.value == 'return':
                    self.eat(ID)
                    self.func_code.append(['ret'])
            self.eat(RBRACKET)
        return self.code

    def param(self):
        if self.current_token.type == WORD:
            word = self.current_token
            self.eat(WORD)
            return word.value
        else:
            self.error()

    def params(self):
        while self.current_token.type is not RPAREN:
            p = self.param()
            self.arg += self.func_name + p
            if self.current_token.type == COMMA:
                self.arg += ','
                self.eat(COMMA)
                self.params()
        return self.func_code

    def param_list(self):
        if self.current_token.type == LPAREN:
            self.eat(LPAREN)
            self.params()
            self.func_code.append(['arg', self.arg])
            self.arg = ''
            self.eat(RPAREN)
        return self.func_code

    def call_param(self, func_name):
        if self.current_token.type == NUMBER:
            num = self.current_token
            self.eat(NUMBER)
            return self.code.append(['push', num.value, func_name])
        elif self.current_token.type == WORD:
            word = self.current_token
            self.eat(WORD)
            return self.code.append(['push', self.func_name + word.value, func_name])
        elif self.current_token.type == STRING:
            string = self.current_token
            self.eat(STRING)
            return self.code.append(['push', string.value, func_name])
        return self.error()

    def call_param_list(self, func_name):
        while self.current_token.type is not RPAREN:
            self.call_param(func_name)
            if self.current_token.type == COMMA:
                self.eat(COMMA)
                self.call_param_list(func_name)
        return self.code

    def call(self):
        if self.current_token.type == WORD:
            func_name = self.current_token.value
            self.eat(WORD)
            self.eat(LPAREN)
            self.call_param_list(func_name)
            self.eat(RPAREN)
            self.code.append(['push', 'eip'])
            self.code.append(['call', '@%s:' % func_name])
        return self.code

    def if_statement(self):
        self.eat(ID)
        if_num = self.if_num
        self.if_num += 1
        self.code.append(['_start_if%d:' % if_num])
        cmp_jmp = len(self.expr())
        self.block()
        self.code.append(['jmp', '_end_if%d:' % if_num])
        if self.current_token.value == 'else':
            self.code[cmp_jmp - 1][1] = '_else%d:' % if_num
            self.eat(ID)
            self.code.append(['_else%d:' % if_num])
            self.block()
        else:
            self.code[cmp_jmp - 1][1] = '_end_if%d:' % if_num
        self.code.append(['_end_if%d:' % if_num])
        return self.code

    def while_statement(self):
        self.eat(ID)
        while_num = self.while_num
        self.while_num += 1
        self.code.append(['_start_while%d:' % while_num])
        jmp = len(self.expr())
        self.code[jmp - 1][1] = '_end_while%d:' % while_num
        self.block()
        self.code.append(['jmp', '_start_while%d:' % while_num])
        self.code.append(['_end_while%d:' % while_num])
        return self.code

    def def_statement(self):
        self.eat(ID)
        func_name = self.param()
        self.func_name = func_name + '_'
        self.func_code.append(['@%s:' % func_name])
        self.func_code.append(['var', 'ebp'])
        self.param_list()
        backup = self.code
        self.code = self.func_code
        self.block()
        self.code = backup
        self.func_code.append(['ret'])
        self.func_code.append(['end_%s:' % func_name])
        self.func_name = ''
        return self.code

    def print_statement(self):
        self.eat(ID)
        if self.current_token.type == LPAREN:
            self.eat(LPAREN)
            str = ''
            while self.current_token.type is not RPAREN:
                if self.current_token.type == WORD:
                    s = self.func_name + self.current_token.value
                else:
                    s = self.current_token.value
                if s == '%':
                    s = '|'
                str += s
                self.eat(self.current_token.type)
            self.eat(RPAREN)
            self.code.append(['print', str])
        return self.code

    def statement(self):
        if self.current_token.type in (ID, WORD):
            if self.current_token.value == 'if':
                return self.if_statement()
            elif self.current_token.value == 'while':
                return self.while_statement()
            elif self.current_token.value == 'def':
                return self.def_statement()
            elif self.current_token.value == 'print':
                return self.print_statement()
            else:
                if self.peek(1).type == LPAREN:
                    return self.call()
                else:
                    return self.variable()
        return self.error()

    def program(self):
        while self.current_token.type is not EOF:
            self.statement()
        self.code.append(['exit'])
        self.code.extend(self.func_code)
        return self.code


