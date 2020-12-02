# Python 解释器

[TOC]

从一个玩具解释器开始，逐步了解 Python 解释器内部机制，最终参考 Byterun（现有 Python 解释器）实现一个简单但可用的 Python 解释器。

主要内容：

- Python 程序的运行原理
- Python 解释器的内部机制
- 如何实现一个 Python 解释器
- 编写 Python 程序的小技巧

## Hello，解释器

### 解释器定义

开宗明义，什么是 Python 解释器？本文的 Python 解释器仅指代最后执行字节码的部分，不包括将源代码编译成字节码的部分，即一个能运行 Python 字节码的 Python 虚拟机。

### 解释器结构

解释器所处理的字节码来自于对**源代码**进行词法分析、语法分析和编译后所生成的 code object 中的指令集合。它相当于 Python 代码的一个**中间层表示**，好比汇编代码之于 C 代码。

我们的 Python 解释器将模拟**堆栈机器**，仅使用多个栈来完成对字节码操作的执行。

### 玩具解释器

解释器界的 `Hello World`：仅实现简单的加法功能。

最基本的三条指令：

- LOAD_VALUE
- ADD_TWO_VALUES
- PRINT_ANSWER

举个例子：

```Python
# 源代码：
def add_():
    print(7 + 5)

# 编译后的字节码：
what_to_execute = {
    "instructions": [("LOAD_VALUE", 0),  # 第一个数
                     ("LOAD_VALUE", 1),  # 第二个数
                     ("ADD_TWO_VALUES", None),
                     ("PRINT_ANSWER", None)],
    "numbers": [7, 5] }
```

这里的 `what_to_execute` 对应 Python 的 code object，`instructions` 对应 Python 字节码，`numbers` 为常量列表。

玩具解释器完成加法操作步骤：

- `LOAD_VALUE`：将两个数压入栈中
- `ADD_TWO_VALUES`：弹出两个数，相加，将结果压入栈中
- `PRINT_ANSWER`：弹出答案并打印

具体代码：

```Python
# inter1.py
class Interpreter:
    '''解释器类，类的实例为解释器
    '''

    def __init__(self):
        '''初始化一个空列表作为栈
        '''
        self.stack = []

    def LOAD_VALUE(self, number):
        '''将一个数值压入栈中
        '''
        self.stack.append(number)

    def ADD_TWO_VALUES(self):
        '''弹出栈中的两个数值，求和后将结果压入栈中
        '''
        first_num = self.stack.pop()
        second_num = self.stack.pop()
        total = first_num + second_num
        self.stack.append(total)

    def PRINT_ANSWER(self):
        '''将栈中的数值弹出，返回
        '''
        answer = self.stack.pop()
        print(answer)

    def run_code(self, what_to_execute):
        '''执行字节码指令
        '''
        # 指令列表
        instructions = what_to_execute['instructions']
        # 常数列表
        numbers = what_to_execute['numbers']
        # 遍历指令列表，依次执行
        for step in instructions:
            instruction, argument = step
            if instruction == 'LOAD_VALUE':
                value = numbers[argument]
                self.LOAD_VALUE(value)
            if instruction == 'ADD_TWO_VALUES':
                self.ADD_TWO_VALUES()
            if instruction == 'PRINT_ANSWER':
                self.PRINT_ANSWER()
```

测试结果：

```Python
In [1]: from inter1 import Interpreter

In [2]: interpreter = Interpreter()

In [3]: what_to_execute = {
   ...:     "instructions": [("LOAD_VALUE", 0),  # 第一个数
   ...:                      ("LOAD_VALUE", 1),  # 第二个数
   ...:                      ("ADD_TWO_VALUES", None),
   ...:                      ("PRINT_ANSWER", None)],
   ...:     "numbers": [7, 5] }

In [4]: interpreter.run_code(what_to_execute)
12
```

### 变量的概念

上述例子只是常量的加法运算，接下来引入变量。需要新增两条指令：

- `STORE_NAME`：存储变量值，将栈顶的数值存入变量
- `LOAD_NAME`：读取变量值，将变量值压入栈中

此外，存储变量名需要新增一个变量名列表。

举个例子：

```Python
# 源代码：
def add_():
    a = 1
    b = 2
    print(a + b)

# 编译后的字节码：
what_to_execute = {
    "instructions": [("LOAD_VALUE", 0),
                     ("STORE_NAME", 0),
                     ("LOAD_VALUE", 1),
                     ("STORE_NAME", 1),
                     ("LOAD_NAME", 0),
                     ("LOAD_NAME", 1),
                     ("ADD_TWO_VALUES", None),
                     ("PRINT_ANSWER", None)],
    "numbers": [1, 2],
    "names":   ["a", "b"] }
```

注意，这里不考虑**命名空间与作用域**的问题，因此在实现解释器时可以直接将变量名与值的映射关系以字典的形式存储在解释器对象的成员变量中。

此外，由于新增了变量名列表，还需要一个参数解析方法 `parse_argument` 来判断指令是针对**常量列表**还是**变量名列表**进行取值。

具体代码：

```Python
# inter2.py
class Interpreter:
    '''解释器类，类的实例为解释器
    '''

    def __init__(self):
        '''初始化一个空列表作为栈
        '''
        self.stack = []         # 栈
        self.environment = {}   # 存储变量映射关系的字典

    def STORE_NAME(self, name):
        '''将变量及其值存入字典
        '''
        value = self.stack.pop()
        self.environment[name] = value

    def LOAD_NAME(self, name):
        '''将变量的值压入栈中
        '''
        value = self.environment[name]
        self.stack.append(value)

    def LOAD_VALUE(self, number):
        '''将一个数值压入栈中
        '''
        self.stack.append(number)

    def ADD_TWO_VALUES(self):
        '''弹出栈中的两个数值，求和后将结果压入栈中
        '''
        first_num = self.stack.pop()
        second_num = self.stack.pop()
        total = first_num + second_num
        self.stack.append(total)

    def PRINT_ANSWER(self):
        '''将栈中的数值弹出，返回
        '''
        answer = self.stack.pop()
        print(answer)

    def parse_argument(self, instruction, argument, what_to_execute):
        '''解析指令参数
        '''
        # 使用常量的指令列表
        numbers = ['LOAD_VALUE']
        # 使用变量名的指令列表
        names = ['LOAD_NAME', 'STORE_NAME']
        if instruction in numbers:
            argument = what_to_execute['numbers'][argument]
        if instruction in names:
            argument = what_to_execute['names'][argument]
        return argument

    def run_code(self, what_to_execute):
        '''执行字节码指令
        '''
        # 指令列表
        instructions = what_to_execute['instructions']
        # 常数列表
        numbers = what_to_execute['numbers']
        # 遍历指令列表，依次执行
        for step in instructions:
            instruction, argument = step
            argument = self.parse_argument(instruction, argument,
                    what_to_execute)
            if instruction == 'LOAD_VALUE':
                self.LOAD_VALUE(argument)
            if instruction == 'ADD_TWO_VALUES':
                self.ADD_TWO_VALUES()
            if instruction == 'PRINT_ANSWER':
                self.PRINT_ANSWER()
            if instruction == 'STORE_NAME':
                self.STORE_NAME(argument)
            if instruction == 'LOAD_NAME':
                self.LOAD_NAME(argument)
```

测试结果：

```Python
In [1]: from inter2 import Interpreter

In [2]: interpreter = Interpreter()

In [3]: what_to_execute = {
   ...:     "instructions": [("LOAD_VALUE", 0),
   ...:                      ("STORE_NAME", 0),
   ...:                      ("LOAD_VALUE", 1),
   ...:                      ("STORE_NAME", 1),
   ...:                      ("LOAD_NAME", 0),
   ...:                      ("LOAD_NAME", 1),
   ...:                      ("ADD_TWO_VALUES", None),
   ...:                      ("PRINT_ANSWER", None)],
   ...:     "numbers": [1, 2],
   ...:     "names":   ["a", "b"] }

In [4]: interpreter.run_code(what_to_execute)
3
```

注意到指令名与对应方法名相同，因此可以利用 `getattr` 方法直接根据指令名获取方法，避免臃肿的分支结构。只需将 `run_code` 方法 替换成以下 `execute` 方法即可：

```Python
# inter3.py
def execute(self, what_to_execute):
    instructions = what_to_execute["instructions"]
    for each_step in instructions:
        instruction, argument = each_step
        argument = self.parse_argument(instruction, argument, what_to_execute)
        bytecode_method = getattr(self, instruction)
        if argument is None:
            bytecode_method()
        else:
            bytecode_method(argument)
```

## Python 字节码

### 字节码指令

关于 Python 字节码的指令，在上一节的玩具解释器中，为了便于阅读，我们使用了人类可读的命名，但实际的 Python 字节码指令使用的只是1个字节（Python 3.6 之后指令占2个字节）。

举个例子：

```Python
In [1]: def cond():
   ...:     x = 3
   ...:     if x > 5:
   ...:         return 'no'
   ...:     else:
   ...:         return 'yes'
   ...: 

In [2]: print(cond.__code__.co_code)
b'd\x01}\x00|\x00d\x02k\x04r\x10d\x03S\x00d\x04S\x00d\x00S\x00'

In [3]: print(list(bytearray(cond.__code__.co_code)))
[100, 1, 125, 0, 124, 0, 100, 2, 107, 4, 114, 16, 100, 3, 83, 0, 100, 4, 83, 0, 100, 0, 83, 0]
```

其中，`cond.__code__` 是 code object，`cond.__code__.co_code` 是字节码。此外还有 `cond.__code__.co_consts`、`cond.__code__.co_varnames`、`cond.__code__.co_names`。

显然，这种格式的字节码对于人类来说压根看不懂。我们可以使用字节码反汇编器 `dis` 模块来查看，它会将字节码以一种人类可读的形式进行输出：

```Python
In [4]: import dis

In [5]: dis.dis(cond)
  2           0 LOAD_CONST               1 (3)
              2 STORE_FAST               0 (x)

  3           4 LOAD_FAST                0 (x)
              6 LOAD_CONST               2 (5)
              8 COMPARE_OP               4 (>)
             10 POP_JUMP_IF_FALSE       16

  4          12 LOAD_CONST               3 ('no')
             14 RETURN_VALUE

  6     >>   16 LOAD_CONST               4 ('yes')
             18 RETURN_VALUE
             20 LOAD_CONST               0 (None)
             22 RETURN_VALUE
```

输出的5列分别代表：

- 源代码中的行号
- 字节码中的序号
- 人类可读的名称
- 字节码参数
- 字节码参数的内容提示

通过第2列字节码序号的规律可以发现，每条指令及其参数共占2个字节。字节码 `[100, 1, 125, 0, ...]` 中，`100` 和 `125` 表示指令，`1` 和 `0` 表示参数。

可以使用 `dis.opname` 反查指令进行验证：

```Python
dis.opname[100]
Out[6]: 'LOAD_CONST'

In [7]: dis.opname[125]
Out[7]: 'STORE_FAST'
```

### 条件判断与循环

条件判断字节码：

```Python
  In [1]: def cond():
   ...:     x = 3
   ...:     if x > 5:
   ...:         r = 'no'
   ...:     else:
   ...:         r = 'yes'
   ...:     return r
   ...: 

# 条件判断部分字节码
  3           4 LOAD_FAST                0 (x)
              6 LOAD_CONST               2 (5)
              8 COMPARE_OP               0 (<)
             10 POP_JUMP_IF_FALSE       18

  4          12 LOAD_CONST               3 ('yes')
             14 STORE_FAST               1 (r)
             16 JUMP_FORWARD             4 (to 22)

  6     >>   18 LOAD_CONST               4 ('no')
             20 STORE_FAST               1 (r)
```

While循环字节码：

```Python
In [8]: def loop():
   ...:     x = 1
   ...:     while x < 5:
   ...:         x = x + 1
   ...:     return x
   ...: 

# While循环字节码
  3           4 SETUP_LOOP              20 (to 26)
        >>    6 LOAD_FAST                0 (x)
              8 LOAD_CONST               2 (5)
             10 COMPARE_OP               0 (<)
             12 POP_JUMP_IF_FALSE       24

  4          14 LOAD_FAST                0 (x)
             16 LOAD_CONST               1 (1)
             18 BINARY_ADD
             20 STORE_FAST               0 (x)
             22 JUMP_ABSOLUTE            6
        >>   24 POP_BLOCK
```

For循环字节码：

```Python
In [1]: def loop():
   ...:     x = 1
   ...:     for _ in range(5):
   ...:         x = x + 1
   ...:     return x
   ...: 

# For循环字节码
  3           4 SETUP_LOOP              24 (to 30)
              6 LOAD_GLOBAL              0 (range)
              8 LOAD_CONST               2 (5)
             10 CALL_FUNCTION            1
             12 GET_ITER
        >>   14 FOR_ITER                12 (to 28)
             16 STORE_FAST               1 (_)

  4          18 LOAD_FAST                0 (x)
             20 LOAD_CONST               1 (1)
             22 BINARY_ADD
             24 STORE_FAST               0 (x)
             26 JUMP_ABSOLUTE           14
        >>   28 POP_BLOCK
```

### 帧的概念

至此已经大体了解了解释器在函数内部的运行机制，那么函数外呢，`RETURN_VALUE` 之后又是什么？为此，需要引入帧的概念。

**帧**包含了一段代码运行所需要的信息与上下文环境。帧在代码执行时被动态地创建与销毁，每一个帧的创建对应一次**函数调用**，所以每一个帧都有一个 code object 与其关联，同时一个 code object 可以拥有多个帧，因为一个函数可以递归调用自己多次。

帧存在于**调用栈**中,你在程序异常时所看到的 `Traceback` 就是调用栈中的信息。调用栈顾名思义就是每当你在当前函数内调用一次函数就在当前调用栈上压入所调用的函数的帧，在所调用函数返回时再将该帧弹出。

除了调用栈外，代码执行过程中还需要用到两个栈：**数据栈**和**块栈**。数据栈就是前面执行字节码操作时使用的栈；块栈则用于特定的控制流，譬如循环和异常处理。每个帧都拥有自己的数据栈和块栈。

举个例子：`main(模块) -> foo() -> bar()`

```Python
def bar(y):
    z = y + 3    # <--- 执行至此
    return z

def foo():
    a = 1
    b = 2
    return a + bar(b)

foo()
```

![35a0f005e62a7431f107c35161710a1d.png](en-resource://database/2322:1)

当 `CALL_FUNCTION` 时，调用栈的栈顶帧的数据栈的栈顶值（作为位置参数）会被弹出，然后新的栈顶就是要调用的函数，解释器将为其创建一个帧压入调用栈，并将之前弹出的值（位置参数）压入该帧的数据栈中。类似的操作还有 `CALL_FUNCTION_KW` 和 `CALL_FUNCTION_EX`。

当 `RETURN_VALUE` 时，调用栈的栈顶帧的数据栈的栈顶值（即函数返回值）会被弹出，然后调用栈丢弃当前栈顶帧，并将之前的弹出的值（返回值）压入新的栈顶帧的数据栈中。


## 实现 Python 解释器

### Byterun 解释器

Byterun 中的4种主要类型对象：

- `VirtualMachine`：管理最高层结构，特别时调用栈，同时管理指令到操作的映射，是之前 `Interpreter` 类的高级版
- `Frame`：每个 `Frame` 对象都维护一个 code object 引用，并管理必要的状态信息，譬如全局与局部命名空间，以及对调用它自身的帧的引用和最后执行的字节码
- `Function`：控制新帧的创建
- `Block`：只包含3个属性，控制代码流程时使用

### VirtualMachine 类

```Python
class VirtualMachine(object):
    """VirtualMachine 类：管理最高层结构，特别时调用栈，同时管理指令到操作的映射"""

    def __init__(self):
        self.frames = []    # 调用栈
        self.frame = None
        self.return_value = None
        self.last_exception = None
    
    def run_code(self, code_obj, f_globals=None, f_locals=None):
        """运行Python程序的入口
           `code_obj` 为源代码编译后的 code object
           `run_code` 根据 `code_obj` 新建帧并运行
        """
        frame = self.make_frame(code_obj, 
                                f_globals=f_globals, 
                                f_locals=f_locals)
        self.run_frame(frame)
```

### Frame 类

```Python
class Frame(object):
    """Frame 类：维护一个 code object 引用，并管理必要的状态信息"""

    def __init__(self, f_code, f_globals, f_locals, f_back):
        self.f_code = f_code
        self.opcodes = list(dis.get_instructions(self.f_code))
        self.f_globals = f_globals
        self.f_locals = f_locals
        self.f_back = f_back
        self.stack = []    # 数据栈
        self.block_stack = []    # 块栈
        # 由于 Python 在处理不同模块时对命名空间的处理方式可能不同，
        # 在处置内置命名空间时需要做一些额外的工作。
        if f_back:
            self.f_builtins = f_back.f_builtins
        else:
            self.f_builtins = f_locals['__builtins__']
            if hasattr(self.f_builtins, '__dict__'):
                self.f_builtins = self.f_builtins.__dict__
        # 最后运行指令，初始为 0
        self.f_lasti = 0
```

新增 `VirtualMachine` 对 `Frame` 的操作方法：

```Python
	def make_frame(self, code_obj, callargs={}, f_globals=None, f_locals=None):
        """新建帧，主要对帧拥有的命名空间进行初始化
           `code_obj` 为 `code_obj`
           `callargs` 为函数调用时的参数
        """
        if f_globals:
            f_globals = f_globals
            if not f_locals:
                f_locals = f_globals
        elif self.frames:
            f_globals = self.frame.f_globals
            f_locals = {}
        else:
            f_globals = f_locals = {
                '__builtins__': __builtins__,
                '__name__': '__main__',
                '__doc__': None,
                '__package__': None,
            }
        # 将函数调用时的参数更新到局部变量空间中
        f_locals.update(callargs)
        frame = Frame(code_obj, f_globals, f_locals, self.frame)
        return frame
    
    def push_frame(self, frame):
        """调用栈压入帧"""
        self.frames.append(frame)
        self.frame = frame

    def pop_frame(self):
        """调用栈弹出帧"""
        self.frames.pop()
        if self.frames:
            self.frame = self.frames[-1]
        else:
            self.frame = None

    def run_frame(self, frame):
        """运行帧直至返回"""
        # TODO: 运行帧，待完成
        pass
```

`run_frame` 部分将在后面实现。

### Function 类

```Python
class Function(object):

    # __slots__ 会固定对象的属性，无法再动态增加新的属性，这可以节省内存空间
    __slots__ = [
        'func_code', 'func_name', 'func_defaults', 'func_globals',
        'func_locals', 'func_dict', 'func_closure',
        '__name__', '__dict__', '__doc__',
        '_vm', '_func',
    ]

    def __init__(self, name, code, globs, defaults, closure, vm):
        """这部分不需要去深究，但是代码会尽量注释说明"""
        self._vm = vm
        # 这里的 code 即所调用函数的 code_obj
        self.func_code = code
        # 函数名会存在 code.co_name 中
        self.func_name = self.__name__ = name or code.co_name
        # 函数参数的默认值，如 func(a=5,b=3) ，则 func_defaults 为 (5,3)
        self.func_defaults = tuple(defaults)
        self.func_globals = globs
        self.func_locals = self._vm.frame.f_locals
        self.__dict__ = {}
        # 函数的闭包信息
        self.func_closure = closure
        self.__doc__ = code.co_consts[0] if code.co_consts else None
        # 有时我们需要用到真实 Python 的函数，下面的代码是为它准备的
        kw = {
            'argdefs': self.func_defaults,
        }
        # 为闭包创建 cell 对象
        if closure:
            kw['closure'] = tuple(make_cell(0) for _ in closure)
        self._func = types.FunctionType(code, globs, **kw)
    
    def __call__(self, *args, **kwargs):
        """每调用一次函数，将创建一个新帧并运行"""
        # 通过`inspect.getcallargs`获取绑定参数
        callargs = inspect.getcallargs(self._func, *args, **kwargs)
        # 为函数创建新帧
        frame = self._vm.make_frame(
            self.func_code, callargs, self.func_globals, {}
        )
        return self._vm.run_frame(frame)
```

新增 `VirtualMachine` 对 `Frame` 的数据栈的操作：

```Python
    # 栈顶帧的数据栈操作
    def top(self):
        return self.frame.stack[-1]

    def pop(self):
        return self.frame.stack.pop()

    def push(self, *vals):
        self.frame.stack.extend(vals)

    def popn(self, n):
        """弹出多个值"""
        if n:
            ret = self.frame.stack[-n:]
            self.frame.stack[-n:] = []
            return ret
        else:
            return []

    def peek(self, n):
        """获取多个值"""
        return self.frame.stack[-n]
```

在实现 `run_frame` 之前还需要2个函数：

- `parse_byte_and_args`：解析指令及其参数
- `dispatch`：映射每条指令调用的方法

这部分在 `CPython` 中的实现是非常麻烦的，但我们可以使用 Python 现成的 `dis` 库很方便地搞定。

```Python
    def parse_byte_and_args(self):
        """解析指令及其参数（如果有的话）
           需要注意的是，Python 3.6 以后，每条指令占2个字节
        """
        f = self.frame
        opoffset = f.f_lasti
        # 获取要运行的指令
        currentOp = f.opcodes[opoffset]
        byteCode = currentOp.opcode    # 指令码
        byteName = currentOp.opname    # 指令名
        f.f_lasti += 1
        if byteCode == dis.EXTENDED_ARG:
            # `dis` 库已经自动帮我们计算这种情况了，直接忽略即可
            return self.parse_byte_and_args()
        # 指令码 < dis.HAVE_ARGUMENT 都是有参指令
        if byteCode >= dis.HAVE_ARGUMENT:
            intArg = currentOp.arg
            if byteCode in dis.hasconst:   # 查找常量
                arg = f.f_code.co_consts[intArg]
            elif byteCode in dis.hasname:  # 查找变量名
                arg = f.f_code.co_names[intArg]
            elif byteCode in dis.haslocal: # 查找局部变量名
                arg = f.f_code.co_varnames[intArg]
            # 由于 Python 3.6 以后每条指令占2个字节，所以算跳转位置时要 //2
            elif byteCode in dis.hasjrel:  # 相对跳转位置
                arg = f.f_lasti + intArg//2
            elif byteCode in dis.hasjabs:  # 绝对跳转位置
                arg = intArg//2
            else:
                arg = intArg
            arguments = [arg]
        else:
            arguments = []
        return byteName, arguments
```

```Python
	def dispatch(self, byteName, arguments):
        """映射每条指令调用的方法函数"""
        why = None
        try:
            # 一元/二元操作指令都需要弹出数据栈，需与其他指令做出区分
            if byteName.startswith('UNARY_'):
                self.unaryOperator(byteName[6:])
            elif byteName.startswith('BINARY_'):
                self.binaryOperator(byteName[7:])
            else:
                # 通过指令名获取对应方法函数
                bytecode_fn = getattr(self, 'byte_{}' % byteName, None)
                if not bytecode_fn:
                    raise VirtualMachineError(
                        "unknown bytecode type: {}" % byteName
                    )
                why = bytecode_fn(*arguments)
        except:
            # 存储运行指令时的异常信息
            self.last_exception = sys.exc_info()[:2] + (None,)
            why = 'exception'
        return why
```

至此，可以开始实现 `run_frame`：

```Python
    def run_frame(self, frame):
        """运行帧直至返回"""
        self.push_frame(frame)
        while True:
            byteName, arguments = self.parse_byte_and_args()
            why = self.dispatch(byteName, arguments)
            while why and frame.block_stack:
                why = self.manage_block_stack(why)
            if why:
                break
        self.pop_frame()
        if why == 'exception':
            exc, val, tb = self.last_exception
            e = exc(val)
            e.__traceback__ = tb
            raise e
        return self.return_value
```

### Block 类

`Block` 用于某些流控制，尤其是异常处理与循环。

```Python
Block = collections.namedtuple("Block", "type, handler, level")
```

其中，`type` 可取 `loop`、`setup-except`、`finally`。此外，还需要创建 `why` 变量来标记流控制的状态，`why` 可取 `None`、`continue`、`break`、`exception`、`return`。

新增 `VirtualMachine` 对 `Block` 的操作方法：

```Python
    def push_block(self, b_type, handler=None):
        level = len(self.frame.stack)
        self.frame.block_stack.append(Block(b_type, handler, level))

    def pop_block(self):
        return self.frame.block_stack.pop()
    
    def unwind_block(self, block):
        if block.type == 'except-handler':
            # exception 对应3个元素：type、value、traceback
            offset = 3
        else:
            offset = 0
        while len(self.frame.stack) > block.level + offset:
            self.pop()
        if block.type == 'except-handler':
            tb, value, exctype = self.popn(3)
            self.last_exception = exctype, value, tb
    
    def manage_block_stack(self, why):
        """管理一个帧的块栈
           在循环、异常处理、返回等情况种、中操作块栈与数据栈
        """
        frame = self.frame
        block = frame.block_stack[-1]
        if block.type == 'loop' and why == 'continue':
            self.jump(self.return_value)
            why = None
            return why
        self.pop_block()
        self.unwind_block(block)
        if block.type == 'loop' and why == 'break':
            why = None
            self.jump(block.handler)
            return why
        if (block.type in ['setup-except', 'finally'] and why == 'exception'):
            self.push_block('except-handler')
            exctype, value, tb = self.last_exception
            self.push(tb, value, exctype)
            self.push(tb, value, exctype) # yes, twice
            why = None
            self.jump(block.handler)
            return why
        elif block.type == 'finally':
            if why in ('return', 'continue'):
                self.push(self.return_value)
            self.push(why)
            why = None
            self.jump(block.handler)
            return why
        return why
```

###  指令实现

给出部分指令的实现，完整实现请查看[附录 A](#附录A)。

```Python
    ## Stack manipulation

    def byte_LOAD_CONST(self, const):
        self.push(const)

    def byte_POP_TOP(self):
        self.pop()

    ## Names

    def byte_LOAD_NAME(self, name):
        frame = self.frame
        if name in frame.f_locals:
            val = frame.f_locals[name]
        elif name in frame.f_globals:
            val = frame.f_globals[name]
        elif name in frame.f_builtins:
            val = frame.f_builtins[name]
        else:
            raise NameError("name '%s' is not defined" % name)
        self.push(val)

    def byte_CALL_FUNCTION(self, arg):
        lenKw, lenPos = divmod(arg, 256) # KWargs not supported here
        posargs = self.popn(lenPos)
        func = self.pop()
        frame = self.frame
        retval = func(*posargs)
        self.push(retval)

    def byte_RETURN_VALUE(self):
        self.return_value = self.pop()
        return "return"
```

## 参考资料

- [500L：Python 实现 Python 解释器](http://aosabook.org/en/500L/a-python-interpreter-written-in-python.html)
- [Allison Kaptur - Bytes in the Machine: Inside the CPython interpreter](https://www.youtube.com/watch?v=HVUTjQzESeo)
- [So you want to write an interpreter?](https://www.youtube.com/watch?v=LCslqgM48D4)
- [A ten-hour codewalk through the Python interpreter source code](http://pgbovine.net/cpython-internals.htm)

- [Byterun 源代码](https://github.com/nedbat/byterun)
- [CPython 源代码](https://github.com/python/cpython)

## <span id="附录A">附录 A</span>

```Python
    ## Stack manipulation

    def byte_LOAD_CONST(self, const):
        self.push(const)

    def byte_POP_TOP(self):
        self.pop()

    ## Names

    def byte_LOAD_NAME(self, name):
        frame = self.frame
        if name in frame.f_locals:
            val = frame.f_locals[name]
        elif name in frame.f_globals:
            val = frame.f_globals[name]
        elif name in frame.f_builtins:
            val = frame.f_builtins[name]
        else:
            raise NameError("name '%s' is not defined" % name)
        self.push(val)

    def byte_STORE_NAME(self, name):
        self.frame.f_locals[name] = self.pop()

    def byte_LOAD_FAST(self, name):
        if name in self.frame.f_locals:
            val = self.frame.f_locals[name]
        else:
            raise UnboundLocalError(
                "local variable '%s' referenced before assignment" % name
            )
        self.push(val)

    def byte_STORE_FAST(self, name):
        self.frame.f_locals[name] = self.pop()

    def byte_LOAD_GLOBAL(self, name):
        f = self.frame
        if name in f.f_globals:
            val = f.f_globals[name]
        elif name in f.f_builtins:
            val = f.f_builtins[name]
        else:
            raise NameError("global name '%s' is not defined" % name)
        self.push(val)

    ## Operators

    BINARY_OPERATORS = {
        'POWER':    pow,
        'MULTIPLY': operator.mul,
        'FLOOR_DIVIDE': operator.floordiv,
        'TRUE_DIVIDE':  operator.truediv,
        'MODULO':   operator.mod,
        'ADD':      operator.add,
        'SUBTRACT': operator.sub,
        'SUBSCR':   operator.getitem,
        'LSHIFT':   operator.lshift,
        'RSHIFT':   operator.rshift,
        'AND':      operator.and_,
        'XOR':      operator.xor,
        'OR':       operator.or_,
    }

    def binaryOperator(self, op):
        x, y = self.popn(2)
        self.push(self.BINARY_OPERATORS[op](x, y))

    COMPARE_OPERATORS = [
        operator.lt,
        operator.le,
        operator.eq,
        operator.ne,
        operator.gt,
        operator.ge,
        lambda x, y: x in y,
        lambda x, y: x not in y,
        lambda x, y: x is y,
        lambda x, y: x is not y,
        lambda x, y: issubclass(x, Exception) and issubclass(x, y),
    ]

    def byte_COMPARE_OP(self, opnum):
        x, y = self.popn(2)
        self.push(self.COMPARE_OPERATORS[opnum](x, y))

    ## Attributes and indexing

    def byte_LOAD_ATTR(self, attr):
        obj = self.pop()
        val = getattr(obj, attr)
        self.push(val)

    def byte_STORE_ATTR(self, name):
        val, obj = self.popn(2)
        setattr(obj, name, val)

    ## Building

    def byte_BUILD_LIST(self, count):
        elts = self.popn(count)
        self.push(elts)

    def byte_BUILD_MAP(self, size):
        self.push({})

    def byte_STORE_MAP(self):
        the_map, val, key = self.popn(3)
        the_map[key] = val
        self.push(the_map)

    def byte_LIST_APPEND(self, count):
        val = self.pop()
        the_list = self.frame.stack[-count] # peek
        the_list.append(val)

    ## Jumps

    def byte_JUMP_FORWARD(self, jump):
        self.jump(jump)

    def byte_JUMP_ABSOLUTE(self, jump):
        self.jump(jump)

    def byte_POP_JUMP_IF_TRUE(self, jump):
        val = self.pop()
        if val:
            self.jump(jump)

    def byte_POP_JUMP_IF_FALSE(self, jump):
        val = self.pop()
        if not val:
            self.jump(jump)

    def jump(self, jump):
        """移动字节码指针至目标位置"""
        self.frame.f_lasti = jump

    ## Blocks

    def byte_SETUP_LOOP(self, dest):
        self.push_block('loop', dest)

    def byte_GET_ITER(self):
        self.push(iter(self.pop()))

    def byte_FOR_ITER(self, jump):
        iterobj = self.top()
        try:
            v = next(iterobj)
            self.push(v)
        except StopIteration:
            self.pop()
            self.jump(jump)

    def byte_BREAK_LOOP(self):
        return 'break'

    def byte_POP_BLOCK(self):
        self.pop_block()

    ## Functions

    def byte_MAKE_FUNCTION(self, argc):
        name = self.pop()
        code = self.pop()
        defaults = self.popn(argc)
        globs = self.frame.f_globals
        fn = Function(name, code, globs, defaults, None, self)
        self.push(fn)

    def byte_CALL_FUNCTION(self, arg):
        lenKw, lenPos = divmod(arg, 256) # KWargs not supported here
        posargs = self.popn(lenPos)
        func = self.pop()
        frame = self.frame
        retval = func(*posargs)
        self.push(retval)

    def byte_RETURN_VALUE(self):
        self.return_value = self.pop()
        return "return"

    ## Prints

    def byte_PRINT_ITEM(self):
        item = self.pop()
        sys.stdout.write(str(item))

    def byte_PRINT_NEWLINE(self):
        print("")
```

