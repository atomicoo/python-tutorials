from inter1 import Interpreter

interpreter = Interpreter()

# 源代码：
# def add_():
#     print(7 + 5)
# 编译后的字节码：
what_to_execute = {
    "instructions": [("LOAD_VALUE", 0),  # 第一个数
                     ("LOAD_VALUE", 1),  # 第二个数
                     ("ADD_TWO_VALUES", None),
                     ("PRINT_ANSWER", None)],
    "numbers": [7, 5] }

interpreter.run_code(what_to_execute)
