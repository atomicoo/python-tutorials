import sys
from importlib import abc
from importlib.machinery import ModuleSpec
import imp
from urllib.request import urlopen

# Debugging
import logging
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def load_module(url):
    logger.debug("Load module: get source from %s", url)
    u = urlopen(url)
    s = u.read().decode('utf-8')
    logger.debug("Load module: create module %s", url)
    m = sys.modules.setdefault(url, imp.new_module(url))
    c = compile(s, url, 'exec')
    m.__file__ = url
    m.__package__ = ''
    logger.debug("Load module: exec code object %s", c)
    exec(c, m.__dict__)
    return m

class UrlMetaFinder(abc.MetaPathFinder):
    def __init__(self, baseurl):
        self._baseurl = baseurl
    
    def find_module(self, fullname, path=None):
        logger.debug("Find module: fullname=%s, path=%s", fullname, path)
        if path is None:
            baseurl = self._baseurl
        else:
            if not path.startswith(self._baseurl):
                return None
            baseurl = path
        try:
            logger.debug("Find module: module %s found", fullname)
            loader = UrlMetaLoader(baseurl)
            return loader
        except Exception:
            logger.debug("Find module: module %s not found", fullname)
            return None

    # def find_spec(self, fullname, path=None, target=None):
    #     if path is None:
    #         baseurl = self._baseurl
    #     else:
    #         if not path.startswith(self._baseurl):
    #             return None
    #         baseurl = path
    #     try:
    #         loader = UrlMetaLoader(baseurl)
    #         return ModuleSpec(fullname, loader, is_package=loader.is_package(fullname))
    #     except Exception:
    #         return None
        

class UrlMetaLoader(abc.SourceLoader):
    def __init__(self, baseurl):
        self._baseurl = baseurl
    
    # def load_module(self, fullname):
    #     c = self.get_code(fullname)
    #     m = sys.modules.setdefault(fullname, imp.new_module(fullname))
    #     m.__file__ = self.get_filename(fullname)
    #     m.__loader__ = self
    #     m.__package__ = fullname
    #     exec(c, m.__dict__)
    #     return None
    
    def get_code(self, fullname):
        u = urlopen(self.get_filename(fullname))
        return u.read()

    # def execute_module(self, module):
    #     pass

    def get_data(self):
        pass

    def get_filename(self, fullname):
        return self._baseurl + fullname + '.py'

def install_meta(address):
    finder = UrlMetaFinder(address)
    sys.meta_path.append(finder)
    logger.debug('%s installed on sys.meta_path', finder)


if __name__ == '__main__':
    print("Base Url Import.")

