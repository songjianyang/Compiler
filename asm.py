import re
import os
import sys
import math
from parser import *

code = Parser(sys.argv[1]).program()

index = 0
tmp = {}
asm = ['global main',
       'extern printf',
       'extern exit',
       'section .data',
       'format: times 256 db 0,0',
       'section .text',
       'main:']


def gen_var(arg):
    if arg is not 'ebp':
        var = '%s: times 256 db 0,0' % arg
        asm.insert(5, var)


def gen_add(arg):
    add = '''
    pop eax
    add [esp],eax '''
    asm.append(add)


def gen_sub(arg):
    sub = '''
    pop eax
    sub [esp],eax '''
    asm.append(sub)


def gen_mul(arg):
    mul = '''
    pop eax
    pop ebx
    mul ebx
    push eax
    '''
    asm.append(mul)


def gen_pop(arg):
    pop = '''
    pop ebx
    mov [%s],ebx
    ''' % arg
    asm.append(pop)


def gen_div(arg):
    div = '''
    mov edx,0
    pop ebx
    pop eax
    div ebx
    push eax    
    '''
    asm.append(div)


def gen_ret(arg):
    ret = 'ret'
    asm.append(ret)


def gen_cmpgt(arg):
    cmpgt = '''
    pop eax
    pop ebx
    cmp ebx,eax
    '''
    asm.append(cmpgt)


def gen_cmplt(arg):
    cmplt = '''
        pop eax
        pop ebx
        cmp ebx,eax
        '''
    asm.append(cmplt)


def gen_cmp(arg):
    cmp = '''
        pop eax
        pop ebx
        cmp ebx,eax
        '''
    asm.append(cmp)


def gen_jle(arg):
    jle = '''
    jle %s
    ''' % arg.replace(':', '')
    asm.append(jle)


def gen_jne(arg):
    jne = '''
    jne %s
    ''' % arg.replace(':', '')
    asm.append(jne)


def gen_jge(arg):
    jge = '''
    jge %s
    ''' % arg.replace(':', '')
    asm.append(jge)


def gen_jmp(arg):
    jmp = '''
    jmp %s
    ''' % arg.replace(':', '')
    asm.append(jmp)


def gen_exit(arg):
    exit = '''
    push 0
    call exit
    '''
    asm.append(exit)


def gen_call(arg):
    call = 'call %s' % arg.replace(":", '')
    asm.append(call)


def gen_push(arg):
    global index
    if arg == 'eip':
        return
    if len(code[index]) > 2:
        func_name = code[index][2]
        value = code[index][1]
        if func_name not in tmp:
            tmp.update({func_name: []})
        tmp[func_name].append(value)
    elif '"' in str(arg):
        arg = eval(arg)
        if code[index + 1][0] == 'pop':
            v = code[index + 1][1]
            x = int(math.ceil(len(arg) / 4.0))
            for i in xrange(0, x):
                i = i * 4
                push = 'mov dword [%s+%d],"%s"' % (v, i, arg[i:i + 4])
                asm.append(push)
            index += 1
        else:
            error()
    elif str(arg).isdigit():
        asm.append('push %s' % arg)
    else:
        asm.append('push dword [%s]' % arg)


def func_index(func_name):
    func_i = asm.index('call @%s' % func_name)
    func_i = func_i if func_i > 0 else 0
    return func_i


def gen_arg(arg):
    if arg:
        params = arg.split(',')
        params.reverse()
        func_name = params[0].split('_')[0]

        for var_name in params:
            gen_var(var_name)
            value = tmp[func_name].pop()
            if '"' in str(value):
                value = value.replace('"', '')
                x = int(math.ceil(len(value) / 4.0))
                for i in xrange(0, x):
                    i = i * 4
                    local_var = 'mov dword [%s+%d],"%s"' % (var_name, i, value[i:i + 4])
                    asm.insert(func_index(func_name), local_var)
            elif str(value).isalpha():
                local_var = '''
                cld 
                mov ecx,256
                mov esi,%s
                mov edi,%s
                rep movsb
                ''' % (value, var_name)
                asm.insert(func_index(func_name), local_var)
            else:
                local_var = "mov dword [%s],%d" % (str(var_name), int(value))
                asm.insert(func_index(func_name), local_var)


def gen_print(arg):
    stack_n = 0

    if '|' in arg:
        fmt, var = arg.split('|')
        fmt = fmt.replace('"', '').replace("\\n", '^')
        fmt += '$'
        fmt_p = re.findall(r'%[sd]', fmt)
        var_p = var.split(',')
        x = int(math.ceil(len(fmt) / 4.0))
        for i in xrange(0, x):
            i = i * 4
            push = 'mov dword [%s+%d],`%s`' % ('format', i, fmt[i:i + 4])
            push = push.replace("^", '\\n').replace('$','\\x00')
            asm.append(push)

        params = range(0, len(var_p))
        params.reverse()
        for i in params:
            if fmt_p[i] == '%d':
                print_ = '''
                push dword [%s]
                ''' % var_p[i]
                asm.append(print_)
                stack_n += 4
            elif fmt_p[i] == '%s':
                print_ = '''
                lea eax,[%s]
                push eax
                ''' % var_p[i]
                asm.append(print_)
                stack_n += 4
            else:
                error()
    else:
        arg = arg.replace('"', '').replace("\\n", '^')
        arg += '$'
        x = int(math.ceil(len(arg) / 4.0))
        for i in xrange(0, x):
            i = i * 4
            push = 'mov dword [%s+%d],`%s`' % ('format', i, arg[i:i + 4])
            push = push.replace("^", '\\n').replace("$",'\\x00')
            asm.append(push)

    print_ = '''
            push format
            call printf
            add esp,%d
            ''' % (int(stack_n) + 4)
    asm.append(print_)


def error():
    raise Exception('Error input')


def run():
    global index
    epcode, operands = 0, 0

    while index < len(code):
        code_line = code[index]
        opcode = code_line[0]
        if len(code_line) > 1:
            operands = code_line[1]
        if ':' in opcode:
            asm.append(opcode)
        else:
            action = eval('gen_' + opcode)
            action(operands)
        index += 1

    f = open('./a.asm', 'w+')
    for l in asm:
        f.write(l + '\n')
    f.close()

    os.system('nasm -felf32 a.asm && gcc -m32 a.o && rm a.asm && rm a.o')


run()
