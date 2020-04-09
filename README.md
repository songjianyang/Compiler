# 虚拟机 & 简易编译器

**新手练习，玩具代码。**

lexer.py 
- 用于词法分析

parser.py 
- 使用递归下降进行语法分析，但是跳过了生成AST的步骤，而是直接将源代码转换成中间代码(虚拟机代码)。
- 这么做属实比较头铁，有缺陷，但实现起来简单。

vm.py
- 模拟CPU，直接解释执行虚拟机代码。

asm.py 
- 将源代码转换成汇编代码，生成.asm文件。
- 有了汇编代码，就可以调用nasm生成.o文件，再调用gcc将.o链接成ELF可执行文件。


## 使用方法
运行环境：
- Python2.7
- Ubuntu 16.04


测试Demo： 这段代码不属于任何语言，是我自己设计的语法，它看上去像JavaScript，C和Python的混合体。
```
var i,j

def test(i,j){
    i = 0
    while i<6{
        i = i + 1
        j = 6
        while j > i{
            j = j - 1
            print(" ")
        }
        j = 0
        while j < 2 * i {
            print("*")
            j = j + 1
        }
        print("\n")
    }
}

test(i,j)
```

虚拟机解释执行：
```
python vm.py demo.txt
```

![](/images/vm.jpg)



编译成可执行文件运行：（需要提前安装好nasm和gcc）
```
python asm.py demo.txt
./a.out
```
![](/images/asm.jpg)



## 虚拟机设计思路

设计方式采用的是栈式虚拟机，最重要的三个部分：eip、栈、变量表。
- eip ：指向下一个要运行的指令。
- 栈 ：用来存储变量的值，和需要计算的数据。
- 变量表：用来存储变量名和数据的关系。

虚拟机用来解释执行中间代码，使用parser.py可以将源代码转换成中间代码，它看起来和汇编代码很像。

源代码：
```
var a
a = 1 + 1
```

转换成中间代码：
```
var a
push 1
push 1
add
pop a
```

## 中间代码到汇编

asm.py 用来将中间代码，转换成汇编，这里的汇编其实是nasm语法的汇编，所以我可以利用一些nasm语法特性，实现起来稍微方便一点。

asm.py 将会生成一个.asm后缀的汇编文件，并自动调用nasm将其转换成.o文件，此时距离可执行文件还差一步，因为我在实现print功能的时候用的是printf，所以还需要调用gcc进行链接，最后将生成a.out。

源代码：
```
var a
a = 1 + 1
```
汇编代码：
```
push 1
push 1

pop eax
add [esp],eax

pop ebx
mov [a],ebx
```

## 语法

它所支持的语法有很多流行语言的影子：
- 比如JavaScript的var声明变量；
- C和Java花括号{}表示代码块，print必须要用"%d"格式化字符串
- Python的def声明函数。

因为我是新手，所以本着哪种特性好写就用哪种的原则。

支持的语法特性： 变量、条件语句、循环语句、函数、递归

数据类型只支持两种：数字，字符串。

数字:
```
var a
a = 123
```

字符串:
```
var a
a = "hello"
```

变量：
```
var a
var b,c,d,e
```
**重点：变量名必须是纯字母，不能取name1这种数字和字母混合的名字。**

在使用变量前，必须要用var来声明，否则会报错。

运算符： + - * /

运算符只支持加减乘除，并且只能用来运算数字。
```
var a
a = 2 + 2 - 3
a = a * 6
a = a / 2
```

逻辑符号： > < == 

逻辑运算只支持三种：大于、小于、等于

条件语句：
```
if 2>1{
    print("hello")
}else{
    print("bye bye")
}
```

循环语句：
```
while 1<5{
    print("hello")
}
```

函数：
```
def test(a){
    print("hello %s" % a)
}
```

递归：
支持递归语法，即函数自己调用自己。
```
def test(a){
    if a > 5{
        print("bye bye")
        return
    }else{
        print("hello")
        a = a + 1
        test(a)  
    }
}
```

print语法必须要加格式化字符串，并且必须要有括号。
它写起来和Python差不多：
```
print("hello")
print("hello,%s" % name)
print("hello,%d" % number)
```

### 缺点
缺点太多了有点说不过来，捡两个最明显的说：
1. 支持的数据类型太少，缺少像浮点数和数组这种基本的数据类型。
2. 缺乏语义检查，因为我跳过了AST步骤，直接生成中间代码，这就导致我不能专门进行语义检查。如果你乱写程序只有Parser的语法检查为你提供错误，否则只能等到虚拟机或ELF在运行时导致崩溃才能知道。

### 参考资料

[Let’s Build A Simple Interpreter](https://ruslanspivak.com/lsbasi-part1/)

[自己动手写编译器](https://pandolia.net/tinyc/ch3_Pcode_syntax_a.html)
