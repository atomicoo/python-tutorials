from inter2 import Interpreter

interpreter = Interpreter()

# 源代码：
# def sum_():
#     a = 1
#     b = 2
#     print(a + b)
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

interpreter.run_code(what_to_execute)
