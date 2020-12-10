print(__name__)
print(__package__)

from .foo import a
print(a)

from .sub.bar import b
print(b)
