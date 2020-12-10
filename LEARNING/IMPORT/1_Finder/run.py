import sys

class MyFinder(object):
    @classmethod
    def find_module(cls, name, path, target=None):
        print("Importing", name, path, target)
        return None

sys.meta_path.insert(0, MyFinder)

# import socket
import pkg.sub.foo
