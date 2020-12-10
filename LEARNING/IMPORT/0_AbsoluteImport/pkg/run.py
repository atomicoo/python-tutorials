print(__name__)
print(__package__)

from pkg.foo import a
print(a)

from pkg.sub.bar import b
print(b)
