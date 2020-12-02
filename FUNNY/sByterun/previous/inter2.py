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

