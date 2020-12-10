import unittest
import sys
import io


def get_stdout(func, *args):
    stdout = sys.stdout
    sys.stdout = io.StringIO()
    func(*args)
    output = sys.stdout.getvalue()
    sys.stdout = stdout
    return output

class MyTestCase(unittest.TestCase):
    def test_remote_server(self):
        from urllib.request import urlopen
        u = urlopen('http://localhost:12800/fib.py')
        data = u.read().decode('utf-8')
        print(data[:16])
        self.assertEqual(data[:16], "print(\"I'm fib\")")
    
    def test_base_load_module(self):
        from base import load_module
        fib = load_module('http://localhost:12800/fib.py')
        self.assertEqual(fib.fib(10), 89)
        spam = load_module('http://localhost:12800/spam.py')
        output = get_stdout(spam.hello, 'Guide')
        self.assertEqual(output, 'Hello Guide\n')
    
    def test_base_install_meta(self):
        from base import install_meta
        install_meta('http://localhost:12800')
        import fib, spam
        self.assertEqual(fib.fib(10), 89)
        output = get_stdout(spam.hello, 'Guide')
        self.assertEqual(output, 'Hello Guide\n')
    
    def test_core_install_meta(self):
        from core import install_meta
        install_meta('http://localhost:12800/')
        import fib, spam
        self.assertEqual(fib.fib(10), 89)
        output = get_stdout(spam.hello, 'Guide')
        self.assertEqual(output, 'Hello Guide\n')


if __name__ == '__main__':
    unittest.main()
