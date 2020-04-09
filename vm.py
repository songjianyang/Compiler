from __future__ import print_function
import re
import sys
from parser import *

eip = 0
eflag = 0
stack = []
var_table = {}
param_num = []
ret_addr = []

code = Parser('source1').program()


def do_push(arg):
    global eip
    global ret_addr
    if arg in var_table:
        index = var_table[arg]
        stack.append(stack[index])
    elif 'eip' in str(arg):
        ret_addr.append(int(eip + 1))
    else:
        stack.append(arg)


def do_pop(arg):
    if arg:
        index = var_table[arg]
        stack[index] = stack.pop()
    else:
        stack.pop()


def do_var(arg):
    global var_table
    var_table.update({arg: len(stack)})
    stack.append(0)


def do_add(arg):
    num1 = stack.pop()
    num2 = stack.pop()
    stack.append(int(num2) + int(num1))


def do_sub(arg):
    num1 = stack.pop()
    num2 = stack.pop()
    stack.append(int(num2) - int(num1))


def do_div(arg):
    num1 = stack.pop()
    num2 = stack.pop()
    stack.append(int(num2) / int(num1))


def do_mul(arg):
    num1 = stack.pop()
    num2 = stack.pop()
    stack.append(int(num2) * int(num1))


def do_cmpgt(arg):
    global eflag
    num1 = stack.pop()
    num2 = stack.pop()
    if num2 > num1:
        eflag = 1
    else:
        eflag = 0


def do_cmplt(arg):
    global eflag
    num1 = stack.pop()
    num2 = stack.pop()
    if num2 < num1:
        eflag = 0
    else:
        eflag = 1


def do_cmp(arg):
    global eflag
    num1 = stack.pop()
    num2 = stack.pop()
    if num2 == num1:
        eflag = 1
    else:
        eflag = 0


def do_jge(arg):
    global eip
    if eflag == 1:
        eip = code.index([arg])


def do_jle(arg):
    global eip
    if eflag == 0:
        eip = code.index([arg])


def do_jne(arg):
    global eip
    if eflag == 0:
        eip = code.index([arg])


def do_jmp(arg):
    global eip
    eip = code.index([arg])


def do_call(arg):
    global var_table
    global eip
    eip = code.index([arg])


def do_ret(arg):
    global var_table
    global eip
    global ret_addr
    global param_num

    stack.pop()
    eip = int(ret_addr.pop())

    pn = param_num.pop()
    for i in xrange(pn):
        stack.pop()


def do_arg(arg):
    global var_table
    global param_num
    ebp = var_table['ebp']
    if ',' in arg:
        n = 1
        params = arg.split(',')
        params.reverse()
        param_num.append(len(params))
        for i in params:
            var_table.update({i: ebp - n})
            n += 1
    else:
        n = 0 if arg == '' else 1
        param_num.append(n)
        var_table.update({arg: ebp - n})


def do_print(arg):
    global var_table

    if '|' in arg:
        fmt, var = arg.split('|')
        fmt_p = re.findall(r'%[sd]', fmt)
        var_p = var.split(',')

        for i in xrange(0, len(var_p)):
            v = stack[var_table[var_p[i]]]
            v = str(fmt_p[i] % v)
            fmt = fmt.replace(fmt_p[i], v, 1).replace('"', '')
        print(fmt.replace('\\n', '\n'), end='')
    else:
        print(eval(str(arg)), end='')


def do_exit(arg):
    sys.exit()


def run():
    global eip
    opcode, operands = 0, 0
    while True:
        code_line = code[eip]
        opcode = code_line[0]
        eip += 1
        if len(code_line) > 1:
            operands = code_line[1]
        if ':' not in opcode:
            action = eval('do_' + opcode)
            action(operands)


run()
