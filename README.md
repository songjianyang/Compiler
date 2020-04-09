# 虚拟机 & 简易编译器


lexer.py 用于词法分析
parser.py 语法分析，但是跳过了生成AST的步骤，而是直接将源代码转换成中间代码(虚拟机代码)。这么做属实比较头铁，有缺陷，但实现起来简单。
vm.py  模拟CPU，直接解释执行虚拟机代码。
asm.py 将源代码转换成汇编代码，生成.asm文件。有了汇编代码，就可以调用nasm汇编器生成.o文件，再调用gcc的链接器将.o链接成elf文件。
