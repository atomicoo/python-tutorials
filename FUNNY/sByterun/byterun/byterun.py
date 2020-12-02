from __future__ import print_function

import collections
import operator
import dis
import sys
import types
import inspect

class VirtualMachineError(Exception):
    pass

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
            # Prefixes any opcode which has an argument too big to fit into the
            # default two bytes. ext holds two additional bytes which, taken
            # together with the subsequent opcode’s argument, comprise a
            # four-byte argument, ext being the two most-significant bytes.
            # We simply ignore the EXTENDED_ARG because that calculation
            # is already done by dis, and stored in next currentOp.
            # Lib/dis.py:_unpack_opargs
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
                bytecode_fn = getattr(self, 'byte_%s' % byteName, None)
                if not bytecode_fn:
                    raise VirtualMachineError(
                        "unknown bytecode type: %s" % byteName
                    )
                why = bytecode_fn(*arguments)
        except:
            # 存储运行指令时的异常信息
            self.last_exception = sys.exc_info()[:2] + (None,)
            why = 'exception'
        return why
    
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
        if f_back:
            self.f_builtins = f_back.f_builtins
        else:
            self.f_builtins = f_locals['__builtins__']
            if hasattr(self.f_builtins, '__dict__'):
                self.f_builtins = self.f_builtins.__dict__
        # 最后运行指令，初始为 0
        self.f_lasti = 0


def make_cell(value):
    """创建一个真实的 cell 对象"""
    # Thanks to Alex Gaynor for help with this bit of twistiness.
    # Construct an actual cell object by creating a closure right here,
    # and grabbing the cell object out of the function we create.
    fn = (lambda x: lambda: x)(value)
    return fn.__closure__[0]


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
        # self.func_closure = closure
        self.__doc__ = code.co_consts[0] if code.co_consts else None
        # 有时我们需要用到真实 Python 的函数，下面的代码是为它准备的
        kw = {
            'argdefs': self.func_defaults,
        }
        # 为闭包创建 cell 对象
        # if closure:
        #     kw['closure'] = tuple(make_cell(0) for _ in closure)
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


Block = collections.namedtuple("Block", "type, handler, level")


if __name__ == '__main__':
    import dis
    import textwrap
    code = textwrap.dedent("""\
        print(1+2)
    """)
    # compile 能够将源代码编译成字节码
    code_obj = compile(code, "tmp", "exec")
    print(dis.dis(code_obj))
    vm = VirtualMachine()
    vm.run_code(code_obj)

